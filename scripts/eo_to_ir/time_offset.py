# -*- coding: utf-8 -*-
"""
Created on Thu May 30 13:32:09 2019

@author: eric.smith
"""

import os.path
import numpy as np
import cv2
import subprocess
import sys
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

blocksize = 16
width = 352
height = 240
thresh = 300
maxoffset = 500
mincount = 40

def compute_descriptors(filenames, H):
    
    img0 = cv2.imread(filenames[0])
    img0 = cv2.cvtColor(img0, cv2.COLOR_BGR2GRAY)
    if (H is not None):
        img0 = cv2.warpPerspective(img0, H, (width,height), borderValue = (0,0,0))
        
    descriptors = []
    c = 0
    for f in range(1,len(filenames)):
        c += 1        
        img1 = cv2.imread(filenames[f])
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY).astype(np.float)
        if (H is not None):
            img1 = cv2.warpPerspective(img1, H, (width,height), borderValue = (0,0,0))
        
        diff = np.abs(img1 - img0)
        #cv2.imwrite("blo%db.png"%c, diff.astype(np.uint8))
        descriptor = []
        for i in range(0,diff.shape[0]-blocksize,blocksize):
            for j in range(0,diff.shape[1]-blocksize,blocksize):
                val = np.sum(diff[i:i+blocksize,j:j+blocksize])
                descriptor.append(val)

        d = np.array(descriptor)
        dmax = np.amax(d)
        if (dmax > thresh):
            descriptors.append(d / np.linalg.norm(d))
        else:
            descriptors.append(None)
        img0 = img1
    
        
    return descriptors
    
    
def descr_dist(d1, d2):
    if (d1 is not None and d2 is not None):
        return np.linalg.norm(d1 - d2), 1.0
    elif d1 is None and d2 is not None:
        return np.linalg.norm(d2), 1.0
    elif d1 is not None and d2 is None:
        return np.linalg.norm(d1), 1.0
    return 0.0,0.0

def align(directory1, directory2, H):
    
    imgtypes = ['.jpg', '.png', '.JPG']
    filenames1 = [ os.path.join(directory1,f) for f in os.listdir(directory1) if os.path.isfile(os.path.join(directory1,f)) and os.path.splitext(f)[1] in imgtypes]  
    filenames2 = [ os.path.join(directory2,f) for f in os.listdir(directory2) if os.path.isfile(os.path.join(directory2,f)) and os.path.splitext(f)[1] in imgtypes]    
    
    descriptors1 = compute_descriptors(filenames1, H)
    descriptors2 = compute_descriptors(filenames2, None)

    nd1 = len(descriptors1)
    nd2 = len(descriptors2)
    
    best = 0
    bestdist = 1e200
    for offset in range(0,maxoffset):
        dist = 0.0
        count = 0.0
        for i,j in zip(range(0,nd1), range(offset,nd2)):
            d,c = descr_dist(descriptors1[i], descriptors2[j])
            dist += d
            count += c
        dist /= count
        if (dist < bestdist and count > mincount):
            best = offset
            bestdist = dist
    
    for offset in range(0,maxoffset):
        dist = 0.0
        count = 0.0
        for i,j in zip(range(offset,nd1), range(0,nd2)):
            d,c = descr_dist(descriptors1[i], descriptors2[j])
            dist += d
            count += c
        dist /= count
        if (dist < bestdist and count > mincount):
            best = -offset
            bestdist = dist
            
    print (best)
    print (bestdist)
    return best
    
if __name__ == "__main__":
    irdir = r'C:\Data\diva\2018-03-15.10-35-00.10-40-00.hospital.G479.avi'
    eodir = r'C:\Data\diva\2018-03-15.10-35-06.10-40-06.hospital.G301.avi'
    #irdir = r'C:\Data\diva\ir'
    #eodir = r'C:\Data\diva\eo'
    outdir = r'C:\Data\diva'
    Hfile = r'C:\Data\diva\metadata\geometry\2018-03\homographies\G301-G479.txt'
    H = np.loadtxt(Hfile)
    align(eodir, irdir, H)