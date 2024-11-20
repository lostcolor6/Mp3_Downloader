# Mp3_Downloader
Simple Application with GUI (PyQt5) to download Music from Youtube as .mp3 files
You can choose to insert 
- one link
- a playlist link



### Requirements
````
pip install yt-dlp
pip install PyQt5 
```` 

also make sure `ffmpeg` is installed 
(open-source multimedia framework used for processing video and audio files (encoding, decoding, etc.)
- still works without it on single videos but will throw errors (playlists wont work)

## How to Install FFmpeg

**Windows**

- Download the latest FFmpeg static build from the official site: https://ffmpeg.org/download.html.
  (for example on the build from gyan.dev the `ffmpeg-release-essentials` is sufficent)
- Extract the files to a folder (e.g., `C:\ffmpeg`).
- Add the `bin` directory to your system's PATH:
- Go to Control Panel > System > Advanced system settings > Environment Variables.
- Find the Path variable, click Edit, and add the path to the `bin` folder (e.g., `C:\ffmpeg\bin`).


## Disclaimer:

This application is intended for personal use only. Downloading content from YouTube or other platforms may violate their terms of service and copyright laws. Users are solely responsible for ensuring they have the necessary permissions or rights to download and use the content.

The developer of this application assumes no responsibility for any misuse, including downloading copyrighted materials without authorization. It is your responsibility to comply with all applicable laws and the terms of service of the respective platform.
