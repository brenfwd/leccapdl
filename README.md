<div align="center">
   <img width="500" alt="LeccapDL" src="https://github.com/user-attachments/assets/8cef4e0d-7662-4d35-ab6f-1b64ee6a1e03" />
</div>

<hr />

LeccapDL is a Python utility to enable students to download lecture recordings from the [University of Michigan's CAEN Lecture Recording Service](https://caen.engin.umich.edu/lecrecording/) for **personal** use. The program uses Python and Selenium for interactive authentication using the University's login system.

<table><td>
   
**Table of Contents**

- [Features](#features)
- [Instructions](#instructions)
   - [Setup](#setup)
   - [Running](#running)
- [FAQ](#faq)
- [License](#license) 

</td></table>

## Features

- **Course Download**: Downloads an entire semester of lecture recordings at once, neatly organized into its own directory.
- **Interactive Login**: Uses an interactive browser window allowing you to log in to your university account safely.
- **Progress Animations**: Provides realtime download progress using the tqdm library.

## Instructions

### Setup

1. Clone the repo and `cd` into it
1. Run `python3 -m venv env`
1. Activate the environment
   1. On Linux/Mac: `source env/bin/activate`
   1. On Windows: idk, use WSL
1. Install dependencies with `pip install -r requirements.txt`

![Setup Instructions](https://github.com/user-attachments/assets/b8c193b6-61d9-4c94-9953-460e046f3a78)

### Running

1. Simply run `python3 main.py` and enter your desired course name

A Selenium-controlled browser window will appear. You will need to log into your University of Michigan account in order to access the lecture capture site.

![Running Instructions](https://github.com/user-attachments/assets/f2755726-d729-4775-ab7e-ac8192dcd1e8)

### FAQ

- Can I trust this with my login info?
   - All the source code is plainly visible in [main.py](./main.py). Please feel free to read through it closely if you are wary of entering your login info.
- Are subtitles supported?
   - Yes, the script attempts to download subtitle files and saves them as `.srt` files alongside the video files.
- Are the lecture slides also downloaded?
   - Yes, if the recording includes slides, those will be embedded side-by-side in the video file.
- Are my username and password stored somewhere?
   - Yes, your cookies and other data will be stored in the `./chrome-data/` directory for subsequent runs. If you are done with the program for a while, consider deleting this directory when you are done, so that your credentials aren't stored for longer than needed.
- Is this allowed?
   - Downloading videos for a course you are/were enrolled in, and using those video files solely for your own personal use, should be completely fine. However, understand that by using this program you are doing so at your own risk. If you are considering distributing the files downloaded by this program, please do further research and ask for permission from the appropriate rights holders for the content as needed.

## License

Licensed under the GNU Affero General Public License, version 3.0. See [LICENSE](./LICENSE).
