import os.path
import numpy as np
import cv2
import subprocess
import sys

pt = None
matches = []
split = 0


def stab_annotate(img1name, img2name, outputdir, H):
    global matches
    global pt
    global split

    winname_vid = 'image'
    cv2.namedWindow(winname_vid, cv2.WINDOW_NORMAL)
    cv2.moveWindow(winname_vid,0,0)    
    cv2.setMouseCallback(winname_vid, onMouse, None)

    warpimgname = os.path.join(outputdir, 'warp.png')
    drawwarp = False

    img1 = cv2.imread(img1name)
    img2 = cv2.imread(img2name)
    print(img1.dtype)
    h1, w1, d1 = img1.shape
    h2, w2, d2 = img2.shape
    
    img1r = np.zeros([h2, w1, d1],dtype=np.uint8)
    img1r[0:h1,:,:] = img1
    split = w1
 
    img = np.concatenate((img1r, img2), axis=1)
    print(np.amax(img))
    
    warp_img = None
    if H is not None:
        drawwarp = True
        warp_img = cv2.warpPerspective(img1, H, (w2,h2), borderValue = (0,0,0))
        
    cv2.resizeWindow(winname_vid,img.shape[1],img.shape[0]) 
    while (True):
        if (drawwarp and warp_img is not None):
            dispimg = np.concatenate((img1r, warp_img), axis=1)
        else:
            dispimg = img.copy()                
            if (pt is not None):
                cv2.circle(dispimg, (pt[0], pt[1]), 3, [0, 0, 255], thickness=4)
            for m in matches:
                cv2.line(dispimg, (m[0][0], m[0][1]), (m[1][0], m[1][1]), [0,255,255], thickness=1)
           
        cv2.imshow(winname_vid, dispimg)   
        key = cv2.waitKey(5)
        if (not drawwarp and key == ord(' ')):
            src_pts = []
            dst_pts = []
            print(matches)
            for m in matches:
                src_pts.append(m[0])
                dst_pts.append(np.array([m[1][0] - split, m[1][1]]))
            
            src_pts = np.float32(src_pts).reshape(-1,1,2)
            dst_pts = np.float32(dst_pts).reshape(-1,1,2)
            print(src_pts.shape)
            H, mask = cv2.findHomography(src_pts, dst_pts)
            print(H)
            warp_img = cv2.warpPerspective(img1, H, (w2,h2), borderValue = (0,0,0))
            cv2.imwrite(warpimgname, warp_img)
            drawwarp = True
        elif (key == ord('w')):
            drawwarp = not drawwarp
        elif (key == ord('n')):
            write_homog(img1name, img2name, outputdir, H)
            matches = []
            pt = None
            cv2.destroyAllWindows()
            return H
        elif (key == 8):                
            if (len(matches) > 0):
                del matches[-1]                
        elif (key == 27):
            sys.exit(0)
                
    cv2.destroyAllWindows()
    return H
    
def onMouse(event, x, y, hi, _):
    global pt    
    global split
    global matches
    if (event == cv2.EVENT_LBUTTONDOWN):
        if (pt is None):
            pt = np.array([x,y])
        else:
            if (pt[0] < split and x > split):                
                matches.append((pt,np.array([x,y])))
                pt = None
            elif (pt[0] > split and x < split):
                matches.append((np.array([x,y]), pt))
                pt = None
            else:
                pt = np.array([x,y])

def read_homog(d1, d2, outdir):
    #i1 = os.path.splitext(os.path.basename(d1))[0]
    #i2 = os.path.splitext(os.path.basename(d2))[0]
    i1 = os.path.splitext(os.path.basename(d1))[0]
    s1 = i1.split('.')
    i1 = s1[0] + '.' + s1[3] + '.' + s1[4]
    i2 = os.path.splitext(os.path.basename(d2))[0]
    s2 = i2.split('.')
    i2 = s2[0] + '.' + s2[3] + '.' + s2[4]
    filename = "%s_%s.txt"%(i2, i1)
    filename = os.path.join(outdir, filename)
    if (not os.path.exists(filename)):
        return None
        
    Hinv = np.loadtxt(filename)
    return np.linalg.inv(Hinv)

def write_homog(d1, d2, outdir, H):
    i1 = os.path.splitext(os.path.basename(d1))[0]
    s1 = i1.split('.')
    i1 = s1[0] + '.' + s1[3] + '.' + s1[4]
    i2 = os.path.splitext(os.path.basename(d2))[0]
    s2 = i2.split('.')
    i2 = s2[0] + '.' + s2[3] + '.' + s2[4]
    filename = "%s_%s.txt"%(i2, i1)
    f = open(os.path.join(outdir, filename), 'w')
    Hinv = np.linalg.inv(H)
    np.savetxt(f, Hinv)
    f.write('\n')
    f.close()
        
    
if __name__ == "__main__":
    directory = r'C:\Data\diva'
    pairs = r'C:\Data\diva\pairs2.txt'
    outdir = r'C:\Data\diva\metadata\geometry\eo-ir-homographies'
    f = open(pairs,'r')
    H = None
    for line in f:
        splt = line.split()
        H_read = read_homog(os.path.join(directory,splt[1]), os.path.join(directory, splt[0]), outdir)
        if (H_read is not None):
            H = H_read
        H = stab_annotate(os.path.join(directory,splt[1]), os.path.join(directory, splt[0]), outdir, H)
    stab_annotate(irdir, eodir, outdir)