import numpy as np
import numpy.linalg as npl


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
    back_plane = np.vstack((n, d))
    p5 = backproject_to_plane(cam, (box[0], box[1]), back_plane)
    height = p5.flat[2]
    box3d = np.zeros((8, 3))
    box3d[0, :] = p1.flatten()
    box3d[1, :] = p2.flatten()
    box3d[2, :] = p3.flatten()
    box3d[3, :] = p4.flatten()
    box3d[4:, :] = box3d[:4, :]
    box3d[4:, 2] = height
    return box3d


def project(cam, wld_pt):
    """Project a world point into an image with a camera"""
    # map to normalized image coordinates
    img_pt = cam[0] * (cam[1] * np.matrix(wld_pt.flat).transpose() + cam[2])
    return img_pt[:2] / img_pt[2]


def box_around_box3d(cam, box3d):
    pts = np.zeros((8, 2))
    for c, p in enumerate(box3d):
        pts[c, :] = project(cam, p).flat
    return np.min(pts, 0).tolist() + np.max(pts, 0).tolist()


def view_to_view(src_cam, dest_cam, bounds):
    box3d = backproject_bbox(src_cam, bounds)
    if box3d is None:
        print("Warning, bad projection!  Skipping.")
        return None

    tgt_box = box_around_box3d(dest_cam, box3d)

    return tgt_box
