from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from typing import Optional
from time import sleep
from tqdm import tqdm
import json
import re
import requests


def fuzzy(s: str) -> str:
    return s.replace(" ", "").lower().strip()


def create_filename(s: str) -> str:
    return re.sub(r"[^\w]+", "_", s)


course_name = input("[?] Enter course name (e.g. EECS 281) > ")
course_name = fuzzy(course_name)
print(f"[i] Course files will be saved under '{course_name}'")


class LeccapDownloader:
    fuzzy_course: str
    driver: webdriver.Chrome
    download_path: Path

    def __init__(self, course_name: str) -> None:
        self.fuzzy_course = fuzzy(course_name)
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--user-data-dir=chrome-data")

        # --- PREVIOUS FIXES ---
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        # --- NEW STABILITY FIXES ---
        # Forces a specific port, bypassing the file check that is failing
        chrome_options.add_argument("--remote-debugging-port=9222")
        # Helps prevent crashes in some environments
        chrome_options.add_argument("--no-sandbox")

        self.driver = webdriver.Chrome(options=chrome_options)

        self.download_path = (
            Path(__file__).parent / "downloads" / self.fuzzy_course
        )

    def close(self) -> None:
        self.driver.close()

    def go(self) -> None:
        course_link = self.find_course_link()
        if not course_link:
            print("[!] Could not find course! Check your search term.")
            return
        self.download_course_link(course_link)

    def goto_home(self) -> None:
        self.driver.get("https://leccap.engin.umich.edu/leccap/")
        sleep(1.0)
        while not self.driver.current_url.startswith("https://leccap.engin.umich.edu"):
            sleep(1.0)

    def find_course_link(self) -> Optional[WebElement]:
        print("[i] Searching for course...")
        self.goto_home()
        by_year_link = self.driver.find_element(
            by=By.PARTIAL_LINK_TEXT, value="View courses by year"
        )
        by_year_link.click()
        while True:
            links = self.driver.find_elements(
                by=By.CSS_SELECTOR,
                value='a.list-group-item[href^="/leccap/site/"]',
            )

            matches = [
                link for link in links if fuzzy(link.text).startswith(course_name)
            ]
            if not matches:
                prev_year_link = self.driver.find_element(
                    by=By.CSS_SELECTOR, value=".previous > a:nth-child(1)"
                )
                if (
                    prev_year_link.get_attribute("href") == "#"
                    or prev_year_link.text[-4:] <= "2015"
                ):
                    return None
                prev_year_link.click()
            elif len(matches) > 1:
                print("[?] Multiple matches found in one year - select one:")
                for i, m in enumerate(matches):
                    print(f"{i+1}. {m.text}")
                while True:
                    n = input(f"[?] Choose 1-{len(matches)} > ")
                    try:
                        n = int(n)
                        if n >= 0 and n <= len(matches):
                            break
                    except ValueError:
                        pass
                    print("[!] Please choose a valid option.")
                return matches[n - 1]
            else:
                return matches[0]

    def download_course_link(self, course_link: WebElement) -> None:
        course_link.click()
        play_buttons = self.driver.find_elements(
            by=By.CSS_SELECTOR,
            value='.play-link>a.btn[href^="/leccap/player/r/"]',
        )
        jsons = []
        for btn in tqdm(play_buttons, desc="Download JSON", leave=False):
            href = btn.get_attribute("href")
            assert href
            slug = href.split("/")[-1]
            res = self.driver.execute_async_script(
                f"""
                const callback = arguments[arguments.length - 1];
                fetch("/leccap/player/api/product/?rk={slug}")
                    .then(res => res.json())
                    .then(json => callback(json));
                """
            )
            jsons.append(res)

        def json_filename(j: dict) -> str:
            date_parts = j["date"].split("/")
            date = f"{date_parts[2]}-{date_parts[0]}-{date_parts[1]}"
            return create_filename(f"{date} {j['title']}")

        parent = self.download_path / "json"
        parent.mkdir(parents=True, exist_ok=True)
        for i, j in enumerate(jsons):
            with open(
                parent / f"{i+1:03}-{json_filename(j)}.json",
                "w",
            ) as f:
                f.write(json.dumps(j))
                # print(j)

        print("[i] Downloading media. This may take a very long time...")

        def download_file(url: str, path: Path):
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get("content-length", 0))
            block_size = 1024

            with tqdm(
                total=total_size,
                unit="B",
                unit_scale=True,
                leave=False,
                desc=path.name,
            ) as pb:
                with open(path, "wb") as f:
                    for data in response.iter_content(block_size):
                        pb.update(len(data))
                        f.write(data)

        parent = self.download_path / "videos"
        parent.mkdir(parents=True, exist_ok=True)
        for i, j in enumerate(tqdm(jsons)):
            url = f"https:{j['mediaPrefix']}{j['sitekey']}/{j['info']['products'][0]['movie_exported_name']}.mp4"
            video_filename = f"{i+1:03}-{json_filename(j)}.mp4"
            subtitle_filename = f"{i+1:03}-{json_filename(j)}.vtt"
            download_file(url, parent / video_filename)
            res = self.driver.execute_async_script(
                f"""
                const callback = arguments[arguments.length - 1];
                fetch("/leccap/player/api/webvtt/?rk={j['recordingkey']}")
                    .then(res => res.text())
                    .then(t => callback(t));
                """
            )
            with open(parent / subtitle_filename, "w") as f:
                f.write(res)


downloader = LeccapDownloader(course_name)
downloader.go()
downloader.close()
