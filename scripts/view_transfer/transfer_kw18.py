#!/usr/bin/env python

"""ckwg +29
 * Copyright 2019 by Kitware, Inc.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without
 * modification, are permitted provided that the following conditions are met:
 *
 *  * Redistributions of source code must retain the above copyright notice,
 *    this list of conditions and the following disclaimer.
 *
 *  * Redistributions in binary form must reproduce the above copyright notice,
 *    this list of conditions and the following disclaimer in the documentation
 *    and/or other materials provided with the distribution.
 *
 *  * Neither name of Kitware, Inc. nor the names of any contributors may be used
 *    to endorse or promote products derived from this software without specific
 *    prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
 * AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
 * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
 * ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
 * ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
 * DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
 * CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
 * OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
 * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 */

Map KW18 from one camera to another


"""

import numpy as np
import numpy.linalg as npl
from camera_io import load_camera_krtd_file
import os.path
import cv2

from optparse import OptionParser


def load_kw18_file(fname):
    data = []
    header = ""
    with open(fname) as f:
        for line in f:
            if line.lstrip()[0] == '#':
                header += line
                continue
            data.append(line.rstrip().split())
    return data, header


def write_kwiver_tracks(f, data, img_num):
    for id, (u, v) in data.items():
        f.write("%d %d %g %g 1.0 1.0 0.0 255 255 255 0\n" % (id, img_num, u, v))


def project(cam, wld_pt):
    """Project a world point into an image with a camera"""
    # map to normalized image coordinates
    img_pt = cam[0] * (cam[1] * np.matrix(wld_pt.flat).transpose() + cam[2])
    return img_pt[:2] / img_pt[2]


def backproject_to_height(cam, img_pt, height=0):
    """Back an image point to a specified world height"""
    # map to normalized image coordinates
    npt = npl.solve(cam[0], np.array(list(img_pt)+[1.0]))
    M = cam[1].copy()
    M[:, 2] = height * M[:, 2] + cam[2]
    wpt = npl.solve(M, npt)
    return np.matrix([wpt[0]/wpt[2], wpt[1]/wpt[2], height]).transpose()


def backproject_to_plane(cam, img_pt, plane):
    """Back an image point to a specified world plane"""
    # map to normalized image coordinates
    npt = np.matrix(npl.solve(cam[0], np.array(list(img_pt)+[1.0])))
    M = cam[1].transpose()
    n = np.matrix(plane[:3]).flatten()
    d = plane.flat[3]
    Mt = M * cam[2]
    Mp = M * npt.transpose()
    return Mp * (np.dot(n, Mt) - d) / np.dot(n, Mp) - Mt


def backproject_bbox(cam, box):
    # project base of the box to the ground
    pc = backproject_to_height(cam, ((box[0]+box[2])/2, box[3]), 0)
    ray = pc - (-cam[1].transpose() * cam[2])
    ray[2] = 0.0
    ray = ray / npl.norm(ray)

    p1 = backproject_to_height(cam, (box[0], box[3]), 0)
    p2 = backproject_to_height(cam, (box[2], box[3]), 0)
    vh = p2 - p1
    vd = np.matrix([-vh.item(1), vh.item(0), 0]).transpose()
    vd = ray * npl.norm(vh)
    vh = np.matrix([-vd.item(1), vd.item(0), 0]).transpose()
    p1 = pc - vh/2
    p2 = pc + vh/2
    p3 = p2 + vd
    p4 = p1 + vd
    if npl.norm(vd) == 0.0:
        return None
    n = vd / npl.norm(vd)
    d = - (n.transpose() * p3).item()
    back_plane = np.vstack((n,d))
    p5 = backproject_to_plane(cam, (box[0], box[1]), back_plane)
    height = p5.flat[2]
    box3d = np.zeros((8,3))
    box3d[0, :] = p1.flatten()
    box3d[1, :] = p2.flatten()
    box3d[2, :] = p3.flatten()
    box3d[3, :] = p4.flatten()
    box3d[4:, :] = box3d[:4, :]
    box3d[4:, 2] = height
    return box3d


def box_around_box3d(cam, box3d):
    pts = np.zeros((8, 2))
    for c, p in enumerate(box3d):
        pts[c, :] = project(cam, p).flat
    return np.min(pts, 0).tolist() + np.max(pts, 0).tolist()


def draw_box(img, box, color=(255,0,0), width=2):
    box = list(map(int, box))
    cv2.line(img, (box[0], box[1]), (box[0], box[3]), color, width)
    cv2.line(img, (box[0], box[3]), (box[2], box[3]), color, width)
    cv2.line(img, (box[2], box[3]), (box[2], box[1]), color, width)
    cv2.line(img, (box[2], box[1]), (box[0], box[1]), color, width)


def draw_box3d(img, cam, box3d, color=(0,0,255), width=1):
    pts = []
    for c, p in enumerate(box3d):
        pts.append(tuple(map(int, project(cam, p).flat)))

    cv2.line(img, pts[0], pts[1], color, width)
    cv2.line(img, pts[1], pts[2], color, width)
    cv2.line(img, pts[2], pts[3], color, width)
    cv2.line(img, pts[3], pts[0], color, width)

    cv2.line(img, pts[4], pts[5], color, width)
    cv2.line(img, pts[5], pts[6], color, width)
    cv2.line(img, pts[6], pts[7], color, width)
    cv2.line(img, pts[7], pts[4], color, width)

    cv2.line(img, pts[0], pts[4], color, width)
    cv2.line(img, pts[1], pts[5], color, width)
    cv2.line(img, pts[2], pts[6], color, width)
    cv2.line(img, pts[3], pts[7], color, width)


def main():
    usage = "usage: %prog [options] src_krtd src_kw18 tgt_krtd tgt_kw18\n\n"
    usage += "  Map KW18 from one camera to another\n"
    parser = OptionParser(usage=usage)

    parser.add_option("-g", "--gui", default=False,
                      action="store_true", dest="gui",
                      help="visualize the tracks in a GUI")
    parser.add_option("-o", "--frame-offset", default=0, type='int',
                      action="store", dest="offset",
                      help="frames to offset output tracks")

    (options, args) = parser.parse_args()

    src_krtd = args[0]
    src_kw18 = args[1]
    tgt_krtd = args[2]
    tgt_kw18 = args[3]

    src_cam = load_camera_krtd_file(src_krtd)
    tgt_cam = load_camera_krtd_file(tgt_krtd)
    #plane = np.array([1,-1,3,5])
    #pt = backproject_to_plane(src_cam, (512,500), plane)
    #print(pt)
    #print((plane[:3] * pt)+plane[3])
    #print(project(src_cam, pt))

    if options.gui:
        img_src = cv2.imread('G335.png')
        img_dst = cv2.imread('G341.png')

    src_tracks, header = load_kw18_file(src_kw18)

    with open(tgt_kw18, 'w') as out:
        out.write(header)
        for ts in src_tracks:
            box = list(map(float, ts[9:13]))
            box3d = backproject_bbox(src_cam, box)
            if box3d is None:
                print("warning, bad projection")
                continue
            tgt_box = box_around_box3d(tgt_cam, box3d)
            center = [(tgt_box[0] + tgt_box[2])/2, (tgt_box[1] + tgt_box[3])/2]
            frame = int(ts[2]) + options.offset
            if frame < 0:
                continue

            if options.gui:
                img1 = img_src.copy()
                img2 = img_dst.copy()
                draw_box(img1, box)
                draw_box3d(img1, src_cam, box3d)
                draw_box3d(img2, tgt_cam, box3d)
                draw_box(img2, tgt_box)
                img1 = cv2.resize(img1, None, fx=0.5, fy=0.5)
                img2 = cv2.resize(img2, None, fx=0.5, fy=0.5)
                cv2.imshow('source',img1)
                cv2.imshow('dest',img2)
                cv2.waitKey(10)

            if tgt_box[2] < 0 or tgt_box[3] < 0 or tgt_box[0] > 1920 or tgt_box[1] > 1080:
                continue

            ts[2] = str(frame)
            ts[7:9] = map(lambda v : "{0:.2f}".format(v), center)
            ts[9:13] = map(lambda v : "{0:.2f}".format(v), tgt_box)
            out.write(' '.join(ts)+"\n")


if __name__ == "__main__":
    main()
