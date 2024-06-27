# Image Sequencer

## Description
This GUI application converts a series of images into a video file.

## Features
- Cross-platform GUI powered by [DearPyGui](https://github.com/hoffstadt/DearPyGui)
- Convert images into a video with customizable output settings (resolution, frame rate)
- Utilizes [FFmpeg](https://github.com/FFmpeg/FFmpeg) for video encoding

## Demo (Work in Progress)
https://github.com/YeetingWaterbottle/Image-Sequencer/assets/73762047/354026cd-0e96-4e4d-ad81-c27c4ca4baaa

## Requirements
- Python 3
- Dependencies
  - [FFmpeg](https://github.com/FFmpeg/FFmpeg)
  - [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
  - [DearPyGui](https://github.com/hoffstadt/DearPyGui)
  - [xdialog](https://github.com/mathgeniuszach/xdialog)

## Installation
1. Clone the repository: `git clone https://github.com/YeetingWaterbottle/Image-Sequencer.git`
2. Install dependencies: `pip install -r requirements.txt`

## Usage
1. Run the application: `python main.py`
2. Add the image files with the buttons on top
  - Use the "Add Individual" button to select and add individual images.
  - Use the "Add Folder" button to add all images from a selected folder.
3. Configure output parameters
3. Configure output parameters:
  - **Source FPS**: Frames per second of the source images sequence.
  - **Output FPS**: Frames per second of the output video.
  - **Output Filename**: Desired filename for the output video file.
  - **Custom Resolution**: Optionally set a custom resolution; use the scale checkbox to maintain aspect ratio.
  
4. Output the video
- Click "Generate Video" to create the video file in the current working directory.
  - Enable "Overwrite if exist" to force overwrite any existing file with the same name.
- Optionally, click "Generate ffmpeg Command" to print the ffmpeg command to the console.
- Save the concatenation file used by ffmpeg with "Generate Concat. File".
