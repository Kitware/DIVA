# -*- coding: utf-8 -*-
"""
Created on Mon May 28 13:41:56 2018

@author: Ameya Shringi, Linus Sherrill

Kwiver process based on Wrapper without roidb
"""

# kwiver/sprokit imports
from sprokit.pipeline import process
from kwiver.kwiver_process import KwiverProcess
from vital.util.VitalPIL import from_pil, get_pil_image

import os
import cv2
import numpy as np
import argparse
import pprint
import cPickle as pkl
import sys
import datetime
import json
# From NIST (https://github.com/usnistgov/ActEV_Scorer)
import _init_paths
from ActEV_Scorer import score_basic
from actev18_ad import ActEV18_AD
# DIVA support scripts
import _init_paths
from tdcnn.exp_config import expcfg_from_file, experiment_config
from log_to_nist import sys_to_res, generate_classes
from roidb_generation import generate_testing_video_db
# R-C3D (https://gitlab.kitware.com/kwiver/R-C3D)
os.environ['GLOG_minloglevel'] = '2'
import caffe
from tdcnn.config import cfg_from_file, cfg
from tdcnn.test_online import test_net_online



class FrameIterator(object):
    def __init__(self, image, ts):
        self.video_path = "pipeline-streamint-input"
        self.stride = 1

        self.current_image_index = ts.get_frame()
        self.current_frame = image

    def has_next_frame(self):
        return True

    # return image from container.
    def get_next_frame(self):
        ## current_frame = cv2.imread(self.all_images[self.current_image_index])
        return current_frame.image()

    def reset(self):
        self.current_image_index = 0


# ------------------------------------------------------------------
# Now for the process
class RC3DProcess(KwiverProcess):
    """
    This process gets ain image as input, does some stuff to it and
    sends the modified version to the output port.
    """
    # ----------------------------------------------
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)

        # set up required flags
        required = process.PortFlags()
        required.add(self.flag_required)

        #  declare our ports ( port-name, flags)
        self.declare_input_port_using_trait('image', required)
        self.declare_input_port_using_trait('timestamp', required )

        self.declare_output_port_using_trait('detected_object_set', process.PortFlags() )

        self.all_logs = []
        self.previous_buffer = None

    # ----------------------------------------------
    def _configure(self):
        # look for 'experiment_file_name' key in the config
        expcfg_from_file(self.config_value('experiment_file_name'))

        if experiment_config.cnn_config is not None:
            cfg_from_file(os.path.join(experiment_config.experiment_root,
                                       experiment_config.cnn_config))

        window_length = cfg.TRAIN.LENGTH[0]
        cfg.GPU_ID = experiment_config.gpu
        print 'Testing the network'
        caffe.set_device(experiment_config.gpu)
        caffe.set_mode_gpu()
        self.net = caffe.Net(os.path.join(experiment_config.experiment_root,
                                     experiment_config.test.network),
                        os.path.join(experiment_config.experiment_root,
                                     experiment_config.results_path,
                                     experiment_config.test.model), caffe.TEST)
        self.net.name = os.path.splitext(os.path.basename(experiment_config.test.model))[0]



    # ----------------------------------------------
    def _step(self):
        # grab image container from port using traits
        in_img_c = self.grab_input_using_trait('image')
        ts = self.grab_input_using_trait('timestamp')

        frame_iterator = FrameIterator(in_img_c, ts)


        current_test_log, self.previous_buffer = test_net_online(net, frame_iterator,
                               max_per_image=experiment_config.test.max_detections,
                               vis=experiment_config.test.visualize,
                               previous_buffer=self.previous_buffer,
                               use_running_frames=args.True)

        if len(all_logs) > 1:
            current_test_log, last_log = \
                current_test_log.combine_logs(all_logs[len(all_logs)-1],
                args.temporal_threshold)
            if len(last_log.activities) > 0:
                all_logs[len(all_logs)-1] = last_log
            else:
                all_logs.pop()

            all_logs.append(current_test_log)

        # process log and make detections for this frame.
        det_set = DetectedObjectSet()


        # TBD - scan log and create detected objects
        # bbox = BoundingBox(minx, miny, maxx, maxy)
        # dot = DetectedObjectType()
        # dot.set_score(name, score)
        #
        # DetectedObject(bbox, dot)

        push_to_port_using_trait('detected_object_set', det_set)


# ==================================================================
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.RC3DProcess'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('RC3DProcess', 'Apply R-C3D detector to image stream', RC3DProcess)

    process_factory.mark_process_module_as_loaded(module_name)
