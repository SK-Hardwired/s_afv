# sony_afv
# Visualizer of AF data from Sony cameras JPEG EXIFs

This tool allows to visualize some statuses of PDAF sensors or CAF stored in EXIF metadata of JPEGs fron Sony cameras. Auto focus statuses are parsed from EXIF and presented as ExifTool interprets them.

With this tool you can see:
- For cameras with 15-points PDAF (for example, SLT-A57):
  - AF hit status for each sensor at shutter release. AF hit displayed by colors from black to white. Black = out of focus. White = In Focus
  - If Face Detection was on, and Face(s) detected - they are highlighted with green frame
  - What AF points were used for final focus adjustments (have additional RED frame)
  - What AF point was reported as in Focus (Yellow circle)
  
For CAF cameras (for example, DSC-RX100M4)
  - If Face Detection was on, and Face(s) detected - they are highlighted with green frame
  - What area was reported as in Focus (Yellow circle). Actually what camera thinks it focused at.
  
This tool consists of 2 scripts:
  - afv.py - this is start module providing simple GUI to select JPG file. YOU SHOULD START THIS FILE
  - afv_draw.py - drawing module which draws selected file and all visualization using matplotlib module.
  
Prerequisities:
  - Python 3.5.3
  - matplotlib module installed (pip install matplotlib) (http://matplotlib.org/)
  - Phil Harvey's EXIFTool binary (named exiftool.exe) to be placed in the same folder as afv and afv_draw scripts. Exiftool download (http://www.sno.phy.queensu.ca/~phil/exiftool/)

Warning! You will get no results or corrupted results if you JPEG photos (their EXIF) were modified or by image processing software. So please use JPEGs straight from the camera.
