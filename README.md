# s_afv
# Visualizer of AF data from Sony cameras JPEG EXIFs

![alt text](a7rm2_afv.jpeg "AFV tool displaying focus data on photo made with ILCE-7RM2")

This tool allows to visualize some statuses of PDAF sensors or CAF stored in EXIF metadata of JPEGs fron Sony cameras. Auto focus statuses are parsed from EXIF and presented as ExifTool interprets them. 
I.e. this tool show where are focus points.

**Standalone (no python installed required) Win x64 version  download link (with all libs and dlls) - https://dl.dropboxusercontent.com/u/7216470/afv_bin_win64.zip **

With this tool you can see:
- For SLT cameras with 15-points PDAF (for example, SLT-A57):
  - AF hit status for each sensor at shutter release. AF hit displayed by colors from black to white. Black = out of focus. White = In Focus
  - If Face Detection was on, and Face(s) detected - they are highlighted with red frame
  - What AF points were used for final focus adjustments (have additional RED frame)
  - What AF point was reported as in Focus (Yellow circle)
  
- For CAF cameras (for example, DSC-RX100M4)
  - If Face Detection was on, and Face(s) detected - they are highlighted with red frame
  - What area was reported as in Focus (Yellow circle). Actually what camera thinks it focused at.
  
- For Hybrid AF cameras (like ILCE-5100, ILCE-6000, ILCE-6300, ILCE-6500, ILCE-7RM2,ILCA-99M2)
  - If Face Detection was on, and Face(s) detected - they are highlighted with red frame
  - What area was reported as in Focus (Yellow circle). Actually what camera thinks it focused at.
  - What Focal Plane (on-sensor) AF points were used
  - Note! For ILCA-99M2 displaying of dedicated PDAF points not implemented yet. Only on-sensor PDAF spots statuses supported.
  
This tool consists of 2 scripts:
  - afv.py - this is start module providing simple GUI to select JPG file. YOU SHOULD START THIS FILE
  - afv_draw.py - drawing module which draws selected file and all visualization using matplotlib module.
  
Prerequisities for launching source script:
  - Python 3.5.3
  - matplotlib module installed (pip install matplotlib) (http://matplotlib.org/)
  - Phil Harvey's EXIFTool binary (named exiftool.exe) to be placed in the same folder as afv and afv_draw scripts. Exiftool download (http://www.sno.phy.queensu.ca/~phil/exiftool/)

Warning! You will get no results or corrupted results if you JPEG photos (their EXIF) were modified or by image processing software. So please use JPEGs straight from the camera.
