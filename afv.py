import os
import sys
#import re
#import json
import subprocess
#import matplotlib.pyplot as plt
#import matplotlib.patches as patches
#from PIL import Image
#import numpy as np
import subprocess
import tkinter as tk
from tkinter import filedialog
os.getcwd()
def openn ():
     F = filedialog.askopenfilename(filetypes=[('JPEG from Sony Camera', '*.jpg')])
     if F :
          subprocess.run(['python','afv_draw.py',F],shell=False)

     
def quitt () :
     root.destroy()
     sys.exit()
     

root = tk.Tk()
B1 = tk.Button(text ="Open...", command = openn) 
B2 = tk.Button(text ="Quit", command = quitt)

B1.pack()
B2.pack()

root.mainloop()

