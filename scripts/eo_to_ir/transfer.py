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

eoirmap = {"2018-03-15.10-35-06.10-40-06.hospital.G301" :  "2018-03-15.10-35-00.10-40-00.hospital.G479",
         "2018-03-15.10-40-06.10-45-06.hospital.G301" :  "2018-03-15.10-40-00.10-45-00.hospital.G479",
         "2018-05-16.14-15-09.14-19-59.hospital.G301" :  "2018-05-16.14-15-00.14-20-00.hospital.G479",
         "2018-05-16.14-20-00.14-25-09.hospital.G301" :  "2018-05-16.14-20-00.14-25-00.hospital.G479",
         "2018-05-16.14-25-10.14-29-59.hospital.G301" :  "2018-05-16.14-25-00.14-30-00.hospital.G479",
         "2018-05-16.14-30-00.14-34-59.hospital.G301" :  "2018-05-16.14-30-00.14-35-00.hospital.G479",
         "2018-05-16.14-35-00.14-40-00.hospital.G301" :  "2018-05-16.14-35-00.14-40-00.hospital.G479",
         "2018-05-16.14-40-00.14-45-00.hospital.G301" :  "2018-05-16.14-40-00.14-45-00.hospital.G479",
         "2018-05-16.14-45-00.14-50-00.hospital.G301" :  "2018-05-16.14-45-00.14-50-00.hospital.G479",
         "2018-05-16.14-50-00.14-55-00.hospital.G301" :  "2018-05-16.14-50-00.14-55-00.hospital.G479",
         "2018-05-16.14-55-00.15-00-00.hospital.G301" :  "2018-05-16.14-55-00.15-00-00.hospital.G479",
         "2018-05-16.15-10-00.15-15-00.hospital.G301" :  "2018-05-16.15-10-00.15-15-00.hospital.G479",
         "2018-05-18.13-00-06.13-05-06.hospital.G301" :  "2018-05-18.13-00-00.13-05-00.hospital.G479",
         "2018-05-18.13-05-06.13-10-06.hospital.G301" :  "2018-05-18.13-05-00.13-10-00.hospital.G479",
         "2018-03-08.10-55-05.11-00-05.admin.G335" :  "2018-03-08.10-55-00.11-00-00.admin.G478",
         "2018-03-15.10-35-00.10-40-00.admin.G335" :  "2018-03-15.10-35-00.10-40-00.admin.G478",
         "2018-03-15.10-40-00.10-45-00.admin.G335" :  "2018-03-15.10-40-00.10-45-00.admin.G478",
         "2018-05-16.14-15-08.14-20-08.admin.G335" :  "2018-05-16.14-15-00.14-20-00.admin.G478",
         "2018-05-16.14-20-08.14-25-08.admin.G335" :  "2018-05-16.14-20-00.14-25-00.admin.G478",
         "2018-05-16.14-25-08.14-30-08.admin.G335" :  "2018-05-16.14-25-00.14-30-00.admin.G478",
         "2018-05-16.14-30-08.14-35-08.admin.G335" :  "2018-05-16.14-30-00.14-35-00.admin.G478",
         "2018-05-16.14-35-08.14-40-08.admin.G335" :  "2018-05-16.14-35-00.14-40-00.admin.G478",
         "2018-05-16.14-40-08.14-45-08.admin.G335" :  "2018-05-16.14-40-00.14-45-00.admin.G478",
         "2018-05-16.14-45-08.14-50-08.admin.G335" :  "2018-05-16.14-45-00.14-50-00.admin.G478",
         "2018-05-16.14-50-08.14-55-08.admin.G335" :  "2018-05-16.14-50-00.14-55-00.admin.G478",
         "2018-05-16.14-55-08.15-00-08.admin.G335" :  "2018-05-16.14-55-00.15-00-00.admin.G478",
         "2018-05-16.15-00-08.15-05-08.admin.G335" :  "2018-05-16.15-00-00.15-05-00.admin.G478",
         "2018-05-18.13-00-02.13-05-02.admin.G335" :  "2018-05-18.13-00-00.13-05-00.admin.G478",
         "2018-05-18.13-05-02.13-10-02.admin.G335" :  "2018-05-18.13-05-00.13-10-00.admin.G478",
         "2018-03-15.10-35-00.10-40-00.school.G336" :  "2018-03-15.10-35-00.10-40-00.school.G474",
         "2018-03-15.10-40-00.10-45-00.school.G336" :  "2018-03-15.10-40-00.10-45-00.school.G474",
         "2018-05-16.14-15-08.14-20-08.school.G336" :  "2018-05-16.14-15-00.14-20-00.school.G474",
         "2018-05-16.14-20-08.14-25-08.school.G336" :  "2018-05-16.14-20-00.14-25-00.school.G474",
         "2018-05-16.14-25-08.14-30-08.school.G336" :  "2018-05-16.14-25-00.14-30-00.school.G474",
         "2018-05-16.14-30-08.14-35-08.school.G336" :  "2018-05-16.14-30-00.14-35-00.school.G474",
         "2018-05-16.14-35-08.14-40-08.school.G336" :  "2018-05-16.14-35-00.14-40-00.school.G474",
         "2018-05-16.14-45-08.14-50-08.school.G336" :  "2018-05-16.14-45-00.14-50-00.school.G474",
         "2018-05-16.14-50-08.14-55-08.school.G336" :  "2018-05-16.14-50-00.14-55-00.school.G474",
         "2018-05-16.14-55-08.15-00-08.school.G336" :  "2018-05-16.14-55-00.15-00-00.school.G474",
         "2018-05-16.15-05-08.15-10-08.school.G336" :  "2018-05-16.15-05-00.15-10-00.school.G474",
         "2018-05-16.15-10-08.15-15-08.school.G336" :  "2018-05-16.15-10-00.15-15-00.school.G474",
         "2018-05-18.13-00-03.13-05-02.school.G336" :  "2018-05-18.13-00-00.13-05-00.school.G474",
         "2018-05-18.13-05-03.13-10-02.school.G336" :  "2018-05-18.13-05-00.13-10-00.school.G474",
         "2018-03-15.10-35-00.10-40-00.school.G338" :  "2018-03-15.10-35-00.10-40-00.school.G477",
         "2018-03-15.10-40-00.10-45-00.school.G338" :  "2018-03-15.10-40-00.10-45-00.school.G477",
         "2018-05-18.13-00-03.13-05-03.school.G338" :  "2018-05-18.13-00-00.13-04-59.school.G477",
         "2018-05-18.13-05-03.13-10-03.school.G338" :  "2018-05-18.13-05-00.13-10-00.school.G477",
         "2018-03-15.10-35-03.10-40-03.bus.G340" :  "2018-03-15.10-35-00.10-40-00.bus.G475",
         "2018-03-15.10-40-03.10-45-03.bus.G340" :  "2018-03-15.10-40-00.10-45-00.bus.G475",
         "2018-05-18.13-00-07.13-05-07.bus.G340" :  "2018-05-18.13-00-00.13-05-00.bus.G475",
         "2018-05-18.13-05-07.13-10-07.bus.G340" :  "2018-05-18.13-05-00.13-10-00.bus.G475",
         "2018-03-15.10-35-06.10-40-06.hospital.G341" :  "2018-03-15.10-35-00.10-40-00.hospital.G476",
         "2018-03-15.10-40-06.10-45-06.hospital.G341" :  "2018-03-15.10-40-00.10-45-00.hospital.G476",
         "2018-05-18.13-00-05.13-05-05.hospital.G341" :  "2018-05-18.13-00-00.13-05-00.hospital.G476",
         "2018-05-18.13-05-05.13-10-05.hospital.G341" :  "2018-05-18.13-05-00.13-10-00.hospital.G476"}

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
    subprocess.call([r'C:\Dev\ffmpeg\bin\ffmpeg.exe', '-i', vid1, r'vid_eo\frame%04d.jpg'], stderr=open(os.devnull, 'wb'))
    if (os.path.isdir('vid_ir')):
       shutil.rmtree('vid_ir')
       time.sleep(5) #windows error sometimes if mkdir follows rmtree
    os.mkdir('vid_ir')
    print('frames from ir')
    subprocess.call([r'C:\Dev\ffmpeg\bin\ffmpeg.exe', '-i', vid2, r'vid_ir\frame%04d.jpg'], stderr=open(os.devnull, 'wb'))
    print('aligning')
    return time_offset.align('vid_eo', 'vid_ir', H)
    

    
if __name__ == "__main__":
    
    root = r'Z:\nodes' #mount path to m1-complete
    homogdir = r'metadata\geometry\eo-ir-homographies' #homogs in metadata repo
    trackdir = r'tracks' #directory where tracks to transfer are stored
    
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

        
    