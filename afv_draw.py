import os
import sys
import re
import json
import subprocess
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
from PIL import Image
import numpy as np


def norm(val):
     ret = float(val)
     ret = ret/1000
     if ret > 1 :
          ret = 1
     ret = 1-ret    
     ret = str(ret)
     return ret

F = sys.argv[1]

# Create figure and axes
fig,ax = plt.subplots()
fig.subplots_adjust(left=0.02, bottom=0.02, right=0.98, top=0.98)
#fig.tight_layout()

f = Image.open(F)
im = np.array(f, dtype=np.uint8)
f.close()

ypixels, xpixels, bands = im.shape

r_size = 0.039*xpixels

x_center = xpixels/2-r_size/2
y_center = ypixels/2-r_size/2

x_c = xpixels/2
y_c = ypixels/2
spacer = 0.047*xpixels
rad = 0.03*xpixels

# Legend text


# F is the path to your target image file.
exifdata = subprocess.check_output(['exiftool.exe',F],shell=True,universal_newlines=True)
exifdata = exifdata.splitlines()
list(exifdata)
exif = dict()


for i,each in enumerate(exifdata):
  # tags and values are separated by a colon
  tag,val = each.split(':',1) # '1' only allows one split
  exif[tag.strip()] = val.strip()


#for key in sorted(exif.items()) :
#     print(key) 

for key in sorted(exif.items()) :
  if key[0].startswith('AF Status'):
       vl = re.findall('\d+',key[1])
       if not vl:
            vl.append('32768')
#               print (key[0],int(vl[0]))
       if key[0] == 'AF Status Center Horizontal' :
            cross_h = int(vl[0])
       if key[0] == 'AF Status Center Vertical' :
            cross_v = int(vl[0])
            if cross_h < cross_v :
                 cross = cross_h
            else :
                 cross = cross_v
            cross = str(int(cross))
#                    print ('Center cross =',norm(cross))
            ax.add_patch(patches.Rectangle((x_center,y_center),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(cross),alpha =0.9))
            txt = ax.text(x_center, y_center,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
            

       if key[0] == 'AF Status Bottom Horizontal' :
            cross_h = int(vl[0])
       if key[0] == 'AF Status Bottom Vertical' :
            cross_v = int(vl[0])
            if cross_h < cross_v :
                 cross = cross_h
            else :
                 cross = cross_v
            cross = str(int(cross))
#                    print ('Bottom cross =',cross)
            ax.add_patch(patches.Rectangle((x_center,y_center+2*spacer),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(cross),alpha =0.9))
            txt = ax.text(x_center,y_center+2*spacer,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if key[0] == 'AF Status Top Horizontal' :
            cross_h = int(vl[0])
       if key[0] == 'AF Status Top Vertical' :
            cross_v = int(vl[0])
            if cross_h < cross_v :
                 cross = cross_h
            else :
                 cross = cross_v
            cross = str(int(cross))
#                    print ('Top cross =',cross) #debug
            ax.add_patch(patches.Rectangle((x_center,y_center-2*spacer),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(cross),alpha =0.9))
            txt = ax.text(x_center,y_center-2*spacer,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if key[0] == 'AF Status Lower-middle' :
            ax.add_patch(patches.Rectangle((x_center,y_center+spacer),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center,y_center+spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
       if key[0] == 'AF Status Upper-middle' :
            ax.add_patch(patches.Rectangle((x_center,y_center-spacer),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center,y_center-spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


       if key[0] == 'AF Status Near Left' :
            ax.add_patch(patches.Rectangle((x_center-spacer,y_center),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center-spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
       if key[0] == 'AF Status Near Right' :
            ax.add_patch(patches.Rectangle((x_center+spacer,y_center),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center+spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


       if key[0] == 'AF Status Left' :
            ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center-3.5*spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if key[0] == 'AF Status Right' :
            ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center+3.5*spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


       if key[0] == 'AF Status Far Left' :
            ax.add_patch(patches.Rectangle((x_center-5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center-5*spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if key[0] == 'AF Status Far Right' :
            ax.add_patch(patches.Rectangle((x_center+5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center+5*spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


       if key[0] == 'AF Status Lower-left' :
            ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center+1.6*spacer),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center-3.5*spacer,y_center+1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if key[0] == 'AF Status Lower-right' :
            ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center+1.6*spacer),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center+3.5*spacer,y_center+1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


       if key[0] == 'AF Status Upper-left' :
            ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center-1.6*spacer),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center-3.5*spacer,y_center-1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if key[0] == 'AF Status Upper-right' :
            ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center-1.6*spacer),r_size,r_size,linewidth=1,edgecolor='g',facecolor=norm(vl[0]),alpha =0.9))
            txt = ax.text(x_center+3.5*spacer,y_center-1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])



if 'AF Points Used' in exif:
  afp_used = (exif.get('AF Points Used')).split(', ')
# TO DELETE afp_used.split(', ')
#          print (afp_used)
  for i in range (0, len(afp_used)) :
       
       if afp_used[i] == 'Center' :
            ax.add_patch(patches.Rectangle((x_center,y_center),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Bottom' :
            ax.add_patch(patches.Rectangle((x_center,y_center+2*spacer),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Top' :
            ax.add_patch(patches.Rectangle((x_center,y_center-2*spacer),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Near Left' :
            ax.add_patch(patches.Rectangle((x_center-spacer,y_center),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Near Right' :
            ax.add_patch(patches.Rectangle((x_center+spacer,y_center),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Left' :
            ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Right' :
            ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Lower-middle' :
            ax.add_patch(patches.Rectangle((x_center,y_center+spacer),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Upper-middle' :
            ax.add_patch(patches.Rectangle((x_center,y_center-spacer),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Far Left' :
            ax.add_patch(patches.Rectangle((x_center-5*spacer,y_center),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Far Right' :
            ax.add_patch(patches.Rectangle((x_center+5*spacer,y_center),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Lower-left' :
            ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center+1.6*spacer),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Lower-right' :
            ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center+1.6*spacer),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))
       if afp_used[i] == 'Upper-left' :
            ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center-1.6*spacer),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))          
       if afp_used[i] == 'Upper-right' :
            ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center-1.6*spacer),r_size,r_size,linewidth=2,edgecolor = 'r',facecolor='none',alpha =0.9))          

if 'Faces Detected' in exif :
  faces = exif.get('Faces Detected')
  faces = int(faces)
#print (faces)

  if faces > 0 :
       if 'Face 1 Position' in exif:
            face_coord = exif.get('Face 1 Position')
            l = list(face_coord.split())
            face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
            ax.add_patch(face)
            txt = ax.text(l[1],l[0],'Face 1', color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if 'Face 2 Position' in exif:
            face_coord = exif.get('Face 2 Position')
            l = list(face_coord.split())
            face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
            ax.add_patch(face)     
            txt = ax.text(l[1],l[0],'Face 2', color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if 'Face 3 Position' in exif:
            face_coord = exif.get('Face 3 Position')
            l = list(face_coord.split())
            face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
            ax.add_patch(face)
            txt = ax.text(l[1],l[0],'Face 3', color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if 'Face 4 Position' in exif:
            face_coord = exif.get('Face 4 Position')
            l = list(face_coord.split())
            face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
            ax.add_patch(face)
            txt = ax.text(l[1],l[0],'Face 4', color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if 'Face 5 Position' in exif:
            face_coord = exif.get('Face 5 Position')
            l = list(face_coord.split())
            face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
            ax.add_patch(face)
            txt = ax.text(l[1],l[0],'Face 5', color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if 'Face 6 Position' in exif:
            face_coord = exif.get('Face 6 Position')
            l = list(face_coord.split())
            face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
            ax.add_patch(face)
            txt = ax.text(l[1],l[0],'Face 6', color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if 'Face 7 Position' in exif:
            face_coord = exif.get('Face 7 Position')
            l = list(face_coord.split())
            face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
            ax.add_patch(face)
            txt = ax.text(l[1],l[0],'Face 7', color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

       if 'Face 8 Position' in exif:
            face_coord = exif.get('Face 8 Position')
            l = list(face_coord.split())
            face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
            ax.add_patch(face)
            txt = ax.text(l[1],l[0],'Face 8', color='w', weight='bold', fontsize='small', ha='center', va='center')
            txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])



#     print (l)
if 'Focus Location' in exif:
  focusp = exif.get('Focus Location')
  foc = list(focusp.split())
  focuspoint = patches.Circle((foc[2],foc[3]),radius=0.02*xpixels,linewidth=1,edgecolor='y',facecolor='none')
  ax.add_patch(focuspoint)
#    print (foc)
if 'AF Point In Focus' in exif:
  afif = exif.get('AF Point In Focus')
  if afif == 'Center (vertical)' :
       ax.add_patch(patches.Circle((x_c,y_c),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Center (horizontal)' :
       ax.add_patch(patches.Circle((x_c,y_c),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Bottom (vertical)' :
       ax.add_patch(patches.Circle((x_c,y_c+2*spacer),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Bottom (horizontal)' :
       ax.add_patch(patches.Circle((x_c,y_c+2*spacer),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Top (vertical)' :
       ax.add_patch(patches.Circle((x_c,y_c-2*spacer),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Top (horizontal)' :
       ax.add_patch(patches.Circle((x_c,y_c-2*spacer),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Near Left' :
       ax.add_patch(patches.Circle((x_c-spacer,y_c),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Near Right' :
       ax.add_patch(patches.Circle((x_c+spacer,y_c),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Left' :
       ax.add_patch(patches.Circle((x_c-3.5*spacer,y_c),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Right' :
       ax.add_patch(patches.Circle((x_c+3.5*spacer,y_c),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Lower-middle' :
       ax.add_patch(patches.Circle((x_c,y_c+spacer),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Upper-middle' :
       ax.add_patch(patches.Circle((x_c,y_c-spacer),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Far Left' :
       ax.add_patch(patches.Circle((x_c-5*spacer,y_c),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Far Right' :
       ax.add_patch(patches.Circle((x_c+5*spacer,y_c),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Lower-left' :
       ax.add_patch(patches.Circle((x_c-3.5*spacer,y_c+1.6*spacer),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Lower-right' :
       ax.add_patch(patches.Circle((x_c+3.5*spacer,y_c+1.6*spacer),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
  if afif == 'Upper-left' :
       ax.add_patch(patches.Circle((x_c-3.5*spacer,y_c-1.6*spacer),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))          
  if afif == 'Upper-right' :
       ax.add_patch(patches.Circle((x_c+3.5*spacer,y_c-1.6*spacer),rad,linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))          

if 'AF Type' in exif :
     if exif.get('AF Type') == '15-point':
          txt = ax.text(0,0,'Note: Number next to AF point represents in-focus estimation.\nLess is better (i.e. 0 = in focus; 32768 = out of focus)', color='y', weight='bold', fontsize='small', ha='left', va='top')
          txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
     else :
          txt = ax.text(0,0,'No "15 Point AF" tag detected - individual AF points statuses not shown.', color='y', weight='bold', fontsize='small', ha='left', va='top')
          txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

else :
          txt = ax.text(0,0,'No "15 Point AF" tag detected - individual AF points statuses not shown.', color='y', weight='bold', fontsize='small', ha='left', va='top')
          txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])




ax.imshow(im)

ax.axis('off')
#wm = plt.get_current_fig_manager()
#wm.window.state('zoomed')
plt.show()
