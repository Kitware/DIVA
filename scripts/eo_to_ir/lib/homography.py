import numpy as np


def load_homography_file(homography_file_path):
    return np.loadtxt(homography_file_path)


def apply_homography(homography, bounds):
    # Bounds are expected in x0, y0, x1, y1
    x0, y0, x1, y1 = bounds

    bound_points = np.array([[x0, y0, 1.0],
                             [x0, y1, 1.0],
                             [x1, y0, 1.0],
                             [x1, y1, 1.0]])

    homographied = (np.matmul(bound_points, np.transpose(homography)))

    homographied = homographied[:, 0:2] / homographied[:, 2][:, None]

    return (np.min(homographied[:, 0]),
            np.min(homographied[:, 1]),
            np.max(homographied[:, 0]),
            np.max(homographied[:, 1]))
