# -*- coding: utf-8 -*-
"""
Created on Thu Jun 06 18:13:28 2019

@author: eric.smith
"""

import os
import shutil
import sys
import numpy as np
import subprocess
import time_offset
import time

#fill in map here { "eovideo" : "irvideo" }
#video filenames without file extensions
eoirmap = {}

#path to ffmpeg
ffmpegpath = r'C:\Dev\ffmpeg\bin\ffmpeg.exe'

root = r'Z:\nodes' #mount path to m1-complete (videos)

homogdir = r'metadata\geometry\eo-ir-homographies' #homogs in metadata repo there is a homog for each day & camera pair

trackdir = r'tracks' #directory where tracks to transfer are stored

def filetopath(root, filename):
    s = filename.split('.')
    date = s[0]
    hour = s[2].split('-')[0]
    return os.path.join(root, date, hour, filename + '.avi')
    
def loadhomog(homogdir, t):
    s1 = t.split('.')
    i1 = s1[0] + '.' + s1[3] + '.' + s1[4]
    print(eoirmap[t])
    s2 = eoirmap[t].split('.')
    i2 = s2[0] + '.' + s2[3] + '.' + s2[4]
    filename = "%s_%s.txt"%(i1, i2)
    filename = os.path.join(homogdir, filename) 
    print(filename)
    if (not os.path.exists(filename)):
        return None
    
    Hinv = np.loadtxt(filename)
    return Hinv, filename
    
def computeFileOffset(t):
    time1 = map(int,t.split('.')[1].split('-'))
    sec_eo = time1[0] * 3600 + time1[1] * 60 + time1[2]
    time2 = map(int,eoirmap[t].split('.')[1].split('-'))
    sec_ir = time2[0] * 3600 + time2[1] * 60 + time2[2]
    timediff = sec_eo - sec_ir
    return timediff * 30
    
def computeVidOffset(vid1, vid2, H):
    if (os.path.isdir('vid_eo')):
        shutil.rmtree('vid_eo')
        time.sleep(5)
    os.mkdir('vid_eo')
    print('frames from eo')
    subprocess.call([ffmpegpath, '-i', vid1, r'vid_eo\frame%04d.jpg'], stderr=open(os.devnull, 'wb'))
    if (os.path.isdir('vid_ir')):
       shutil.rmtree('vid_ir')
       time.sleep(5) #windows error sometimes if mkdir follows rmtree
    os.mkdir('vid_ir')
    print('frames from ir')
    subprocess.call([ffmpegpath, '-i', vid2, r'vid_ir\frame%04d.jpg'], stderr=open(os.devnull, 'wb'))
    print('aligning')
    return time_offset.align('vid_eo', 'vid_ir', H)
    

    
if __name__ == "__main__":
    
    
    offsetfile = 'offset_filename'
    offsetvid = 'offset_video'
    
    tracks = [ os.path.splitext(f)[0] for f in os.listdir(trackdir) if os.path.isfile(os.path.join(trackdir,f)) and os.path.splitext(f)[1] == '.kw18']
    
    out1 = open('transfer-file.bat','w')
    out2 = open('transfer-vid.bat', 'w')
    for t in tracks:
        print(t)
        eovid = filetopath(root, t)
        irvid = filetopath(root, eoirmap[t])
        print(eovid)
        print(irvid)
        
        vid1 = os.path.join('videos',t + '.avi')
        vid2 = os.path.join('videos',eoirmap[t] + '.avi')
        shutil.copyfile(eovid, vid1)
        shutil.copyfile(irvid, vid2)
        
        H, Hfile = loadhomog(homogdir, t)
        off1 = computeFileOffset(t)
        off2 = computeVidOffset(vid1, vid2, H)
        
        print(off1)
        print(off2)
        
        tf = os.path.join(trackdir, t)
        out1.write('python eo_to_ir.py -g %s.geom.yml -a %s.activities.yml -b 352x240 -H %s -f %d -o %s\n'%(tf, tf, Hfile, off1, eoirmap[t]))
        out2.write('python eo_to_ir.py -g %s.geom.yml -a %s.activities.yml -b 352x240 -H %s -f %d -o %s\n'%(tf, tf, Hfile, off2, eoirmap[t]))

        
    