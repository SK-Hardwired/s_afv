import os
import re
import subprocess
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
from matplotlib.widgets import Button
import tkinter as tk
import tkinter.filedialog as tkFileDialog
from PIL import Image
import numpy as np
import rawpy


def norm(val):
     ret = float(val)
     ret = ret/1000
     if ret > 1 :
          ret = 1
     ret = 1-ret
     ret = str(ret)
     return ret


class draw (object) :

     def handle_close(evt):
          fig.close()

     def ofile (self, event):
          global flist,F,pos,oldf
          flist = []
          if 'F' in globals ():
               oldf = F

          F = tkFileDialog.askopenfilename(filetypes=[('JPG or RAW from Sony Camera', ('*.jpg','*.arw'))])
          if not F :
               if 'oldf' not in globals():
                    return
               F = oldf
               for file in os.listdir(os.path.dirname(F)):
                    if file.endswith((".jpg",".JPG",'.arw','.ARW')):
                       flist.append(os.path.dirname(F)+'/'+file)
               flist.sort()
               pos = flist.index(F)


               return
          for file in os.listdir(os.path.dirname(F)):
               if file.endswith((".jpg",".JPG",'.arw','.ARW')):

                  flist.append(os.path.dirname(F)+'/'+file)
          flist.sort()
          #flist.sort(key=len)
          pos = flist.index(F)

          self.start(F)

     def save (self, event):
          global xpixels,ypixels
          sname = tkFileDialog.asksaveasfilename(filetypes=[('JPEG', '*.jpg')],defaultextension='.jpg')
          if not sname:
               return
          extent = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
          wi =(extent.width*fig.dpi)
          fig.savefig(sname, dpi=(fig.dpi*(xpixels/wi)), bbox_inches=extent,pad_inches=0,transparent=True,frameon=False,format='jpg')
          subprocess.call(['exiftool','-tagsFromFile',F,sname,'-overwrite_original_in_place'],shell=True)


     def prevf (self,event):
          global flist,F,pos
          if 'pos' in globals():
               if pos == 0 :
                    pos = len(flist)
               pos = pos-1
               F = flist[pos]
               self.start(F)
          else :
               return


     def nextf (self,event):
          global flist,F,pos
          if 'pos' in globals ():
               if pos == len(flist)-1:
                    pos = -1
               pos = pos+1
               F = flist[pos]
               self.start(F)
          else:
               return

     def zoom (self,event):
          global xpixels,ypixels,z_status
          if z_status == 0:
               x_c = xpixels/2
               y_c = ypixels/2
               bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
               width, height = bbox.width, bbox.height

               width *= fig.dpi
               height *= fig.dpi
               plt.axis([x_c-width/2,x_c+width/2,y_c+height/2,y_c-height/2])
               fig.canvas.draw()
               z_status = 1
          else :
               plt.axis([0,xpixels,ypixels,0])
               fig.canvas.draw()
               z_status = 0


     def start (self,F) :
          global xpixels,ypixels, z_status
          z_status = 0

          plt.sca(ax)
          plt.cla()
          ax.axis('off')
          fig.canvas.set_window_title(os.path.basename(F))
          if '.arw' in F.lower():
               rw = open(F,'rb')
               raw = rawpy.imread(rw)
               im = raw.postprocess(use_camera_wb=True,user_flip=0)
               rw.close()

          if '.jpg' in F.lower():
               f = Image.open(F)
               im = np.array(f, dtype=np.uint8)
               f.close()
          ypixels, xpixels, bands = im.shape

          # F is the path to your target image file.
          exifdata = subprocess.check_output(['exiftool.exe','-a',F],shell=True,universal_newlines=True,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
          exifdata = exifdata.splitlines()
          list(exifdata)
          exif = dict()


          for i,each in enumerate(exifdata):
            # tags and values are separated by a colon
            tag,val = each.split(':',1) # '1' only allows one split
            exif[tag.strip()] = val.strip()


#### IF RAW opened, crop image to proper aspect ratio and resolution according to EXIF (i.e. quick fix of Distortion correction data)
          if exif.get('Full Image Size'):
               fimsize = re.findall('\d+', exif.get('Full Image Size'))
               if int(fimsize[1]) < ypixels or int(fimsize[0]) < xpixels :
                    #debug print ("Crop needed! EXIF Height = ",int(exif.get('Sony Image Height')),", ypixels = ",ypixels)
                    xdiff =  int(fimsize[0])
                    ydiff =  int(fimsize[1])
                    startx = xpixels//2-(xdiff//2)
                    starty = ypixels//2-(ydiff//2)
                    im =im[starty:starty+ydiff,startx:startx+xdiff]
                    ypixels, xpixels, bands = im.shape

               r_size = 0.039*xpixels

               x_center = xpixels/2-r_size/2
               y_center = ypixels/2-r_size/2

               x_c = xpixels/2
               y_c = ypixels/2
               spacer = 0.047*xpixels
               rad = 0.03*xpixels

#15-point AF
          if 'AF Type' in exif :
               if exif.get('AF Type') in ('15-point'):
                    for key in sorted(exif.items()) :
                      if key[0].startswith('AF Status'):
                           vl = re.findall('\d+',key[1])
                           if not vl:
                                vl.append('32768')
                           if key[0] == 'AF Status Center Horizontal' :
                                cross_h = int(vl[0])
                           if key[0] == 'AF Status Center Vertical' :
                                cross_v = int(vl[0])
                                if cross_h < cross_v :
                                     cross = cross_h
                                else :
                                     cross = cross_v
                                cross = str(int(cross))
                                ax.add_patch(patches.Rectangle((x_center,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
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
                                ax.add_patch(patches.Rectangle((x_center,y_center+2*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
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
                                ax.add_patch(patches.Rectangle((x_center,y_center-2*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
                                txt = ax.text(x_center,y_center-2*spacer,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Lower-middle' :
                                ax.add_patch(patches.Rectangle((x_center,y_center+spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center,y_center+spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
                           if key[0] == 'AF Status Upper-middle' :
                                ax.add_patch(patches.Rectangle((x_center,y_center-spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center,y_center-spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Near Left' :
                                ax.add_patch(patches.Rectangle((x_center-spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center-spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
                           if key[0] == 'AF Status Near Right' :
                                ax.add_patch(patches.Rectangle((x_center+spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center+spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Left' :
                                ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center-3.5*spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Right' :
                                ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center+3.5*spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Far Left' :
                                ax.add_patch(patches.Rectangle((x_center-5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center-5*spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Far Right' :
                                ax.add_patch(patches.Rectangle((x_center+5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center+5*spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Lower-left' :
                                ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center+1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center-3.5*spacer,y_center+1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Lower-right' :
                                ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center+1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center+3.5*spacer,y_center+1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Upper-left' :
                                ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center-1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center-3.5*spacer,y_center-1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Upper-right' :
                                ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center-1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center+3.5*spacer,y_center-1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                    if 'AF Point In Focus' in exif:
                      afif = exif.get('AF Point In Focus')
                      if afif == 'Center (vertical)' :
                           ax.add_patch(patches.Circle((x_c,y_c),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Center (horizontal)' :
                           ax.add_patch(patches.Circle((x_c,y_c),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Bottom (vertical)' :
                           ax.add_patch(patches.Circle((x_c,y_c+2*spacer),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Bottom (horizontal)' :
                           ax.add_patch(patches.Circle((x_c,y_c+2*spacer),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Top (vertical)' :
                           ax.add_patch(patches.Circle((x_c,y_c-2*spacer),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Top (horizontal)' :
                           ax.add_patch(patches.Circle((x_c,y_c-2*spacer),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Near Left' :
                           ax.add_patch(patches.Circle((x_c-spacer,y_c),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Near Right' :
                           ax.add_patch(patches.Circle((x_c+spacer,y_c),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Left' :
                           ax.add_patch(patches.Circle((x_c-3.5*spacer,y_c),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Right' :
                           ax.add_patch(patches.Circle((x_c+3.5*spacer,y_c),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Lower-middle' :
                           ax.add_patch(patches.Circle((x_c,y_c+spacer),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Upper-middle' :
                           ax.add_patch(patches.Circle((x_c,y_c-spacer),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Lower-left' :
                           ax.add_patch(patches.Circle((x_c-3.5*spacer,y_c+1.6*spacer),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Lower-right' :
                           ax.add_patch(patches.Circle((x_c+3.5*spacer,y_c+1.6*spacer),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Upper-left' :
                           ax.add_patch(patches.Circle((x_c-3.5*spacer,y_c-1.6*spacer),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Upper-right' :
                           ax.add_patch(patches.Circle((x_c+3.5*spacer,y_c-1.6*spacer),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Far Left' :
                           ax.add_patch(patches.Circle((x_c-5*spacer,y_c),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))
                      if afif == 'Far Right' :
                           ax.add_patch(patches.Circle((x_c+5*spacer,y_c),rad,  linewidth=2,edgecolor = 'y',facecolor='none',alpha =0.9))



                    if 'AF Points Used' in exif:
                      afp_used = (exif.get('AF Points Used')).split(', ')
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
#19-point AF part
               if exif.get('AF Type') in ('19-point'):
                    if exif.get ('Camera Model Name') in ('SLT-A99','SLT-A99V'):
                         r_size = 0.039*xpixels/1.5
                         spacer = 0.047*xpixels/1.5
                         rad = 0.03*xpixels/1.5
                    for key in sorted(exif.items()) :
                      if key[0].startswith('AF Status'):
                           vl = re.findall('\d+',key[1])
                           if not vl:
                                vl.append('32768')
                           if key[0] == 'AF Status Center Horizontal' :
                                cross_h = int(vl[0])
                           if key[0] == 'AF Status Center Vertical' :
                                cross_v = int(vl[0])
                                if cross_h < cross_v :
                                     cross = cross_h
                                else :
                                     cross = cross_v
                                cross = str(int(cross))
                                ax.add_patch(patches.Rectangle((x_center,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
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
                                ax.add_patch(patches.Rectangle((x_center,y_center+2*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
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
                                ax.add_patch(patches.Rectangle((x_center,y_center-2*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
                                txt = ax.text(x_center,y_center-2*spacer,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Lower-middle' :
                                ax.add_patch(patches.Rectangle((x_center,y_center+spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center,y_center+spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
                           if key[0] == 'AF Status Upper-middle' :
                                ax.add_patch(patches.Rectangle((x_center,y_center-spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center,y_center-spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Near Left' :
                                ax.add_patch(patches.Rectangle((x_center-spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center-spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
                           if key[0] == 'AF Status Near Right' :
                                ax.add_patch(patches.Rectangle((x_center+spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center+spacer,y_center,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Left Horizontal' :
                                cross_h = int(vl[0])
                           if key[0] == 'AF Status Left Vertical' :
                                cross_v = int(vl[0])
                                if cross_h < cross_v :
                                     cross = cross_h
                                else :
                                     cross = cross_v
                                cross = str(int(cross))

                                ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
                                txt = ax.text(x_center-3.5*spacer,y_center,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Right Horizontal' :
                                cross_h = int(vl[0])
                           if key[0] == 'AF Status Right Vertical' :
                                cross_v = int(vl[0])
                                if cross_h < cross_v :
                                     cross = cross_h
                                else :
                                     cross = cross_v
                                cross = str(int(cross))

                                ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
                                txt = ax.text(x_center+3.5*spacer,y_center,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Lower-left Horizontal' :
                                cross_h = int(vl[0])
                           if key[0] == 'AF Status Lower-left Vertical' :
                                cross_v = int(vl[0])
                                if cross_h < cross_v :
                                     cross = cross_h
                                else :
                                     cross = cross_v
                                cross = str(int(cross))

                                ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center+1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
                                txt = ax.text(x_center-3.5*spacer,y_center+1.6*spacer,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Lower Far Left' :
                                ax.add_patch(patches.Rectangle((x_center-4.5*spacer,y_center+1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center-4.5*spacer,y_center+1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Upper-right Horizontal' :
                                cross_h = int(vl[0])
                           if key[0] == 'AF Status Upper-right Vertical' :
                                cross_v = int(vl[0])
                                if cross_h < cross_v :
                                     cross = cross_h
                                else :
                                     cross = cross_v
                                cross = str(int(cross))
                                ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center+1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
                                txt = ax.text(x_center+3.5*spacer,y_center+1.6*spacer,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Lower Far Right' :
                                ax.add_patch(patches.Rectangle((x_center+4.5*spacer,y_center+1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center+4.5*spacer,y_center+1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Upper-left Horizontal' :
                                cross_h = int(vl[0])
                           if key[0] == 'AF Status Upper-left Vertical' :
                                cross_v = int(vl[0])
                                if cross_h < cross_v :
                                     cross = cross_h
                                else :
                                     cross = cross_v
                                cross = str(int(cross))
                                ax.add_patch(patches.Rectangle((x_center-3.5*spacer,y_center-1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
                                txt = ax.text(x_center-3.5*spacer,y_center-1.6*spacer,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Upper Far Left' :
                                ax.add_patch(patches.Rectangle((x_center-4.5*spacer,y_center-1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center-4.5*spacer,y_center-1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


                           if key[0] == 'AF Status Upper-right Horizontal' :
                                cross_h = int(vl[0])
                           if key[0] == 'AF Status Upper-right Vertical' :
                                cross_v = int(vl[0])
                                if cross_h < cross_v :
                                     cross = cross_h
                                else :
                                     cross = cross_v
                                cross = str(int(cross))

                                ax.add_patch(patches.Rectangle((x_center+3.5*spacer,y_center-1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
                                txt = ax.text(x_center+3.5*spacer,y_center-1.6*spacer,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Upper Far Right' :
                                ax.add_patch(patches.Rectangle((x_center+4.5*spacer,y_center-1.6*spacer),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(vl[0]),alpha =0.9))
                                txt = ax.text(x_center+4.5*spacer,y_center-1.6*spacer,vl[0], color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Far Left Horizontal' :
                                cross_h = int(vl[0])
                           if key[0] == 'AF Status Far Left Vertical' :
                                cross_v = int(vl[0])
                                if cross_h < cross_v :
                                     cross = cross_h
                                else :
                                     cross = cross_v
                                cross = str(int(cross))
                                ax.add_patch(patches.Rectangle((x_center-5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
                                txt = ax.text(x_center-5*spacer,y_center,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                           if key[0] == 'AF Status Far Right Horizontal' :
                                cross_h = int(vl[0])
                           if key[0] == 'AF Status Far Right Vertical' :
                                cross_v = int(vl[0])
                                if cross_h < cross_v :
                                     cross = cross_h
                                else :
                                     cross = cross_v
                                cross = str(int(cross))

                                ax.add_patch(patches.Rectangle((x_center+5*spacer,y_center),r_size,r_size,linewidth=1,edgecolor='limegreen',facecolor=norm(cross),alpha =0.9))
                                txt = ax.text(x_center+5*spacer,y_center,cross, color='w', weight='bold', fontsize='small', ha='center', va='center')
                                txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

#ILCA-99M2, A77M2 AF POINTS
               if exif.get('Camera Model Name') in ('ILCA-77M2','ILCA-99M2'):
                    if 'AF Points Used' in exif:
                      afp_used = (exif.get('AF Points Used')).split(', ')
                      if exif.get ('Camera Model Name') == 'ILCA-99M2' :
                           r_size = 0.020*xpixels
                           vspacer = 1.2*r_size
                           hspacer = 2.2*r_size
                      if exif.get ('Camera Model Name') == 'ILCA-77M2' :
                           r_size = 0.020*xpixels*1.5
                           vspacer = 1.2*r_size
                           hspacer = 2.2*r_size

#CENTER
                      #E6
                      if 'E6' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D6
                      if 'D6' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F6
                      if 'F6' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C6
                      if 'C6' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G6
                      if 'G6' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #B6
                      if 'B6' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #H6
                      if 'H6' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #A6
                      if 'A6' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c-4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c-4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #I6
                      if 'I6' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c+4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2,y_c+4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))


                      #E5
                      if 'E5' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D5
                      if 'D5' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F5
                      if 'F5' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C5
                      if 'C5' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G5
                      if 'G5' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #B5
                      if 'B5' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #H5
                      if 'H5' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #A5
                      if 'A5' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c-4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c-4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #I5
                      if 'I5' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c+4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-hspacer,y_c+4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))


                      #E7
                      if 'E7' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D7
                      if 'D7' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F7
                      if 'F7' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C7
                      if 'C7' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G7
                      if 'G7' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #B7
                      if 'B7' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #H7
                      if 'H7' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #A7
                      if 'A7' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c-4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c-4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #I7
                      if 'I7' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c+4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+hspacer,y_c+4*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
#LEFT PART
                      #E4
                      if 'E4' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D4
                      if 'D4' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F4
                      if 'F4' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C4
                      if 'C4' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G4
                      if 'G4' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #B4
                      if 'B4' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #H4
                      if 'H4' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-2.8*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))

                      #E3
                      if 'E3' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D3
                      if 'D3' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F3
                      if 'F3' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C3
                      if 'C3' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G3
                      if 'G3' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #B3
                      if 'B3' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #H3
                      if 'H3' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-3.7*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))

                      #E2
                      if 'E2' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D2
                      if 'D2' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F2
                      if 'F2' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C2
                      if 'C2' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G2
                      if 'G2' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #B2
                      if 'B2' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #H2
                      if 'H2' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-4.6*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))


                      #E1
                      if 'E1' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-5.5*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-5.5*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D1
                      if 'D1' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-5.5*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-5.5*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F1
                      if 'F1' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-5.5*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-5.5*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C1
                      if 'C1' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-5.5*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-5.5*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G1
                      if 'G1' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-5.5*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2-5.5*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
#RIGHT PART
                      #E8
                      if 'E8' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D8
                      if 'D8' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F8
                      if 'F8' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C8
                      if 'C8' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G8
                      if 'G8' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #B8
                      if 'B8' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #H8
                      if 'H8' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+2.8*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))

                      #E9
                      if 'E9' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D9
                      if 'D9' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F9
                      if 'F9' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C9
                      if 'C9' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G9
                      if 'G9' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #B9
                      if 'B9' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #H9
                      if 'H9' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+3.7*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))

                      #E10
                      if 'E10' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D10
                      if 'D10' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F10
                      if 'F10' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C10
                      if 'C10' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G10
                      if 'G10' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #B10
                      if 'B10' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c-3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #H10
                      if 'H10' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+4.6*hspacer,y_c+3*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))


                      #E11
                      if 'E11' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+5.5*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+5.5*hspacer,y_c-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #D11
                      if 'D11' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+5.5*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+5.5*hspacer,y_c-vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #F11
                      if 'F11' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+5.5*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+5.5*hspacer,y_c+vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #C11
                      if 'C11' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+5.5*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+5.5*hspacer,y_c-2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                      #G11
                      if 'G11' in afp_used:
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+5.5*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'limegreen',facecolor='none',alpha =0.9))
                      else :
                           ax.add_patch(patches.Rectangle((x_c-r_size/2+5.5*hspacer,y_c+2*vspacer-r_size/2),r_size,r_size,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
#ILCA-99M2 AF POINTS END


          if 'Faces Detected' in exif :
            faces = exif.get('Faces Detected')
            faces = int(faces)

            if faces > 0 :
                 if 'Face 1 Position' in exif:
                      face_coord = exif.get('Face 1 Position')
                      l = list(face_coord.split())
                      l = list(map(float, l))
                      #face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
                      ax.add_patch(patches.Rectangle((l[1],l[0]),l[2],l[3],  linewidth=1,edgecolor='r',facecolor='none'))
                      txt = ax.text(l[1],l[0],'Face 1', color='w', weight='bold', fontsize='small', ha='center', va='center')
                      txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                 if 'Face 2 Position' in exif:
                      face_coord = exif.get('Face 2 Position')
                      l = list(face_coord.split())
                      l = list(map(float, l))
                      #face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
                      ax.add_patch(patches.Rectangle((l[1],l[0]),l[2],l[3],  linewidth=1,edgecolor='r',facecolor='none'))
                      txt = ax.text(l[1],l[0],'Face 2', color='w', weight='bold', fontsize='small', ha='center', va='center')
                      txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                 if 'Face 3 Position' in exif:
                      face_coord = exif.get('Face 3 Position')
                      l = list(face_coord.split())
                      l = list(map(float, l))
                      #face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
                      ax.add_patch(patches.Rectangle((l[1],l[0]),l[2],l[3],  linewidth=1,edgecolor='r',facecolor='none'))
                      txt = ax.text(l[1],l[0],'Face 3', color='w', weight='bold', fontsize='small', ha='center', va='center')
                      txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                 if 'Face 4 Position' in exif:
                      face_coord = exif.get('Face 4 Position')
                      l = list(face_coord.split())
                      l = list(map(float, l))
                      #face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
                      ax.add_patch(patches.Rectangle((l[1],l[0]),l[2],l[3],  linewidth=1,edgecolor='r',facecolor='none'))
                      txt = ax.text(l[1],l[0],'Face 4', color='w', weight='bold', fontsize='small', ha='center', va='center')
                      txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                 if 'Face 5 Position' in exif:
                      face_coord = exif.get('Face 5 Position')
                      l = list(face_coord.split())
                      l = list(map(float, l))
                      #face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
                      ax.add_patch(patches.Rectangle((l[1],l[0]),l[2],l[3],  linewidth=1,edgecolor='r',facecolor='none'))
                      txt = ax.text(l[1],l[0],'Face 5', color='w', weight='bold', fontsize='small', ha='center', va='center')
                      txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                 if 'Face 6 Position' in exif:
                      face_coord = exif.get('Face 6 Position')
                      l = list(face_coord.split())
                      l = list(map(float, l))
                      #face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
                      ax.add_patch(patches.Rectangle((l[1],l[0]),l[2],l[3],  linewidth=1,edgecolor='r',facecolor='none'))
                      txt = ax.text(l[1],l[0],'Face 6', color='w', weight='bold', fontsize='small', ha='center', va='center')
                      txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                 if 'Face 7 Position' in exif:
                      face_coord = exif.get('Face 7 Position')
                      l = list(face_coord.split())
                      l = list(map(float, l))
                      #face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
                      ax.add_patch(patches.Rectangle((l[1],l[0]),l[2],l[3],  linewidth=1,edgecolor='r',facecolor='none'))
                      txt = ax.text(l[1],l[0],'Face 7', color='w', weight='bold', fontsize='small', ha='center', va='center')
                      txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

                 if 'Face 8 Position' in exif:
                      face_coord = exif.get('Face 8 Position')
                      l = list(face_coord.split())
                      l = list(map(float, l))
                      #face = patches.Rectangle((l[1],l[0]),l[2],l[3],linewidth=1,edgecolor='r',facecolor='none')
                      ax.add_patch(patches.Rectangle((l[1],l[0]),l[2],l[3],  linewidth=1,edgecolor='r',facecolor='none'))
                      txt = ax.text(l[1],l[0],'Face 8', color='w', weight='bold', fontsize='small', ha='center', va='center')
                      txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])


          if   (exif.get ('Focal Plane AF Points Used')) :
               if exif.get ('Focal Plane AF Points Used') != '(none)' :
                    if exif.get('Camera Model Name') in ('ILCE-6000','ILCE-5100')  :
                         foc = exif.get ('Focal Plane AF Points Used')
                         foc = [int(s) for s in re.findall(r'\d+',foc)]
                         k=(-1)
                         for j in range (1,10):
                              for i in range (1,12) :
                                   k = k+1
                                   if k in foc :
                                        ax.add_patch(patches.Rectangle((i*(xpixels/11)-xpixels/11/2-r_size/4,ypixels/9*j-ypixels/9/2-r_size/4),r_size/2,r_size/2,linewidth=2,edgecolor = 'lime',facecolor='none',alpha =0.9))
                                   else:
                                        ax.add_patch(patches.Rectangle((i*(xpixels/11)-xpixels/11/2-r_size/4,ypixels/9*j-ypixels/9/2-r_size/4),r_size/2,r_size/2,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                              k = k+10
                         l=10
                         for j in range (1,9) :
                              for i in range (1,11) :
                                   l=l+1
                                   if l in foc :
                                        ax.add_patch(patches.Rectangle((i*(xpixels/11)-r_size/4,ypixels/9*j-r_size/4),r_size/2,r_size/2,linewidth=2,edgecolor = 'lime',facecolor='none',alpha =0.9))
                                   else:
                                        ax.add_patch(patches.Rectangle((i*(xpixels/11)-r_size/4,ypixels/9*j-r_size/4),r_size/2,r_size/2,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))
                              l = l+11
                    elif exif.get('Camera Model Name') in ('ILCE-7RM2')  :
                         foc = exif.get ('Focal Plane AF Points Used')
                         foc = [int(s) for s in re.findall(r'\d+',foc)]
                         k=(-1)
                         for j in range (1,20):
                              for i in range (1,22) :
                                   k = k+1
                                   if k in foc :
                                        ax.add_patch(patches.Rectangle((i*(xpixels/(22*1.5))+xpixels/6-r_size/4,ypixels/(19*1.5)*j+ypixels/7),r_size/4,r_size/4,linewidth=2,edgecolor = 'lime',facecolor='none',alpha =0.9))
                                   else:
                                        ax.add_patch(patches.Rectangle((i*(xpixels/(22*1.5))+xpixels/6-r_size/4,ypixels/(19*1.5)*j+ypixels/7),r_size/4,r_size/4,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))

                    elif exif.get('Camera Model Name') in ('ILCE-7M2')  :
                         foc = exif.get ('Focal Plane AF Points Used')
                         foc = [int(s) for s in re.findall(r'\d+',foc)]
                         k=(-1)
                         for j in range (1,10):
                              for i in range (1,14) :
                                   k = k+1
                                   if k in foc :
                                        ax.add_patch(patches.Rectangle((i*(xpixels/(13*2.35))+xpixels/3.63-r_size/3,ypixels/(9*2.2)*j+ypixels/4.24),r_size/3,r_size/3,linewidth=2,edgecolor = 'lime',facecolor='none',alpha =0.9))
                                   else:
                                        ax.add_patch(patches.Rectangle((i*(xpixels/(13*2.35))+xpixels/3.63-r_size/3,ypixels/(9*2.2)*j+ypixels/4.24),r_size/3,r_size/3,linewidth=2,edgecolor = 'w',facecolor='none',alpha =0.3))



                    elif exif.get('Camera Model Name') in ('ILCE-6300','ILCE-6500','ILCA-99M2','ILCA-77M2','ILCE-9','DSC-RX10M4','DSC-RX100M5','ILCE-7RM3','ILCE-7M3','DSC-RX100M6','ILCE-6400','DSC-RX0', 'DSC-RX0M2', 'MODEL-NAME', 'DSC-RX100M7', 'ILCE-7RM4') :
                         foc = exif.get ('Focal Plane AF Points Used')
                         if int(foc) :

                              r_size = exif.get('Focal Plane AF Point Area')
                              r_size = list(r_size.split())


                              for i in range (1,int(foc)+1) :
                                   afloc = exif.get ('Focal Plane AF Point Location '+str(i))
                                   afloc = list(afloc.split())
                                   afspot = patches.Rectangle((xpixels*int(afloc[0])/int(r_size[0])-xpixels*0.039/2/2,
                                                               ypixels*int(afloc[1])/int(r_size[1])-xpixels*0.039/2/2),
                                                              xpixels*0.039/2,
                                                              xpixels*0.039/2,
                                                              linewidth=1,edgecolor='lime',facecolor='none')

                                   ax.add_patch(afspot)



                    else :
                         foc=[]




               else :
                    foc=[]

          if 'Focus Location' in exif:
            focusp = exif.get('Focus Location')
            #print('Debug ' + focusp)
            focusp = list(focusp.split())
            focusp = list(map(float, focusp))
            if exif.get('AF Area Mode') == 'Tracking' and exif.get('AF Tracking') == 'Lock On AF' and exif.get('Camera Model Name') in ('ILCE-6400','ILCE-9','ILCE-7RM4','ILCE-RX100M7'):
                ax.add_patch(patches.Rectangle((focusp[2]-0.02*xpixels,focusp[3]-0.02*xpixels),0.04*xpixels,0.04*xpixels, linewidth=1,edgecolor='lime',facecolor='none'))
                ax.add_patch(patches.Rectangle((focusp[2]-0.025*xpixels,focusp[3]-0.025*xpixels),0.05*xpixels,0.05*xpixels, linewidth=1,edgecolor='lime',facecolor='none', linestyle='--'))
            elif exif.get('AF Tracking') == 'Face tracking':
                 focuspoint = patches.Circle((focusp[2],focusp[3]),radius=(0.01*xpixels), linewidth=1,edgecolor='lime',facecolor='none')
                 ax.add_patch(focuspoint)
            else:
                 focuspoint = patches.Circle((focusp[2],focusp[3]),radius=(0.01*xpixels), linewidth=1,edgecolor='y',facecolor='none')
                 ax.add_patch(focuspoint)


          if exif.get('AF Type') == '15-point':
               txt = ax.text(0.01*xpixels,0.01*ypixels,str(os.path.basename(F))+' ('+str(pos+1)+'/'+str(len(flist))+')\n'+'15-point focus model detected ('+str(exif.get('Camera Model Name'))+'). Focus Mode: '+str(exif.get('Focus Mode'))+'\nNote: Number next to AF point represents in-focus estimation.\nLess is better (i.e. 0 = in focus; 32768 = out of focus)', color='y', weight='bold', fontsize='small', ha='left', va='top')
               txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
          elif exif.get('AF Type') == '19-point':
               txt = ax.text(0.01*xpixels,0.01*ypixels,str(os.path.basename(F))+' ('+str(pos+1)+'/'+str(len(flist))+')\n'+'19-point focus model detected ('+str(exif.get('Camera Model Name'))+'). Focus Mode: '+str(exif.get('Focus Mode'))+'\nNote: Number next to AF point represents in-focus estimation.\nLess is better (i.e. 0 = in focus; 32768 = out of focus)', color='y', weight='bold', fontsize='small', ha='left', va='top')
               txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

          elif (exif.get ('Focal Plane AF Points Used')) :

               if exif.get('Camera Model Name') in ('ILCE-6000','ILCE-5100','ILCE-7RM2','ILCE-7M2','ILCE-9','ILCE-7RM3','ILCE-7M3','ILCE-6400', 'DSC-RX0', 'DSC-RX0M2', 'MODEL-NAME') :
                    if exif.get('AF Tracking') == 'Face tracking':
                         txt = ax.text(0.01*xpixels,0.01*ypixels,str(os.path.basename(F))+' ('+str(pos+1)+'/'+str(len(flist))+')\n'+'Model with Focal Plane AF Points detected ('+str(exif.get('Camera Model Name'))+'). Focus Mode: '+str(exif.get('Focus Mode'))+'\nFocal Plane AF points used = '+str(len(foc))+'\n'+'EYE AF or Face Tracking engaged!', color='y', weight='bold', fontsize='small', ha='left', va='top')
                         txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
                    else:
                         txt = ax.text(0.01*xpixels,0.01*ypixels,str(os.path.basename(F))+' ('+str(pos+1)+'/'+str(len(flist))+')\n'+'Model with Focal Plane AF Points detected ('+str(exif.get('Camera Model Name'))+'). Focus Mode: '+str(exif.get('Focus Mode'))+'\nFocal Plane AF points used = '+str(len(foc)), color='y', weight='bold', fontsize='small', ha='left', va='top')
                         txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

               if exif.get('Camera Model Name') in ('ILCE-6300','ILCE-6500','ILCA-99M2','ILCA-77M2','ILCE-9','DSC-RX10M4','DSC-RX100M5','ILCE-7RM3','ILCE-7M3','DSC-RX100M6','ILCE-6400', 'DSC-RX0', 'DSC-RX0M2', 'MODEL-NAME', 'DSC-RX100M7', 'ILCE-7RM4') :
                    if exif.get('AF Area Mode') == 'Tracking' and exif.get('AF Tracking') == 'Lock On AF' and exif.get('Camera Model Name') in ('ILCE-6400','ILCE-9','ILCE-7RM4','ILCE-RX100M7'):
                        txt = ax.text(0.01*xpixels,0.01*ypixels,str(os.path.basename(F))+' ('+str(pos+1)+'/'+str(len(flist))+')\n'+'Model with Focal Plane AF Points detected ('+str(exif.get('Camera Model Name'))+'). Focus Mode: '+str(exif.get('Focus Mode'))+'\nFocal Plane AF points used = '+str(foc)+'\n'+'Real time object tracking engaged!', color='y', weight='bold', fontsize='small', ha='left', va='top')
                        txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
                    if exif.get('AF Tracking') == 'Face tracking':
                         txt = ax.text(0.01*xpixels,0.01*ypixels,str(os.path.basename(F))+' ('+str(pos+1)+'/'+str(len(flist))+')\n'+'Model with Focal Plane AF Points detected ('+str(exif.get('Camera Model Name'))+'). Focus Mode: '+str(exif.get('Focus Mode'))+'\nFocal Plane AF points used = '+str(foc)+'\n'+'EYE AF or Face Tracking engaged!', color='y', weight='bold', fontsize='small', ha='left', va='top')
                         txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
                    else:
                         txt = ax.text(0.01*xpixels,0.01*ypixels,str(os.path.basename(F))+' ('+str(pos+1)+'/'+str(len(flist))+')\n'+'Model with Focal Plane AF Points detected ('+str(exif.get('Camera Model Name'))+'). Focus Mode: '+str(exif.get('Focus Mode'))+'\nFocal Plane AF points used = '+str(foc), color='y', weight='bold', fontsize='small', ha='left', va='top')
                         txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])
          else :
                    if not exif.get('Camera Model Name'):
                         ex_cam_mod_name = 'None'
                    else:
                         ex_cam_mod_name = exif.get('Camera Model Name')
                    if not exif.get('Focus Mode'):
                         ex_foc_mode = 'None'
                    else:
                         ex_foc_mode = exif.get('Focus Mode')
                    txt = ax.text(0.01*xpixels,0.01*ypixels,str(os.path.basename(F))+' ('+str(pos+1)+'/'+str(len(flist))+')\n'+str(ex_cam_mod_name)+'. Focus Mode: '+str(ex_foc_mode), color='y', weight='bold', fontsize='small', ha='left', va='top')
                    txt.set_path_effects([path_effects.Stroke(linewidth=2, foreground='black'), path_effects.Normal()])

          ax.imshow(im)

          plt.draw()





# Create figure and axes
callback = draw()
fig = plt.figure()

ax = plt.subplot()

fig.canvas.set_window_title('AF Visualizer')
fig.subplots_adjust(left=0.02, bottom=0.08, right=0.98, top=0.98)
ax.axis('off')
ax.text (0.5,0.5,'Open file with OPEN... button', color='gray', weight='bold', fontsize='x-large', ha='center', va='center')

obutton = plt.axes([0.01, 0.01, 0.1, 0.05])
pbutton = plt.axes([0.12, 0.01, 0.1, 0.05])
nbutton = plt.axes([0.23, 0.01, 0.1, 0.05])
sbutton = plt.axes([0.34, 0.01, 0.1, 0.05])
zbutton = plt.axes([0.45, 0.01, 0.1, 0.05])

fopen = Button(obutton, 'Open...')
fopen.on_clicked(callback.ofile)

prevp = Button(pbutton, 'Previous')
prevp.on_clicked(callback.prevf)

nextp = Button(nbutton, 'Next')
nextp.on_clicked(callback.nextf)

save = Button(sbutton, 'Save')
save.on_clicked(callback.save)

zoom = Button(zbutton, '1:1/Fit')
zoom.on_clicked(callback.zoom)

fig.canvas.mpl_connect('close_event', callback.handle_close)



plt.show()
