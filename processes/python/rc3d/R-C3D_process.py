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
from vital.types import DetectedObjectSet, BoundingBox, DetectedObject, DetectedObjectType

import os
import cv2
import numpy as np
import argparse
import pprint
import cPickle as pkl
import sys
import datetime
import json
import _init_paths
# DIVA support scripts
from tdcnn.exp_config import expcfg_from_file, experiment_config
from log_to_nist import sys_to_res, generate_classes, generate_classes_from_json
from roidb_generation import generate_testing_video_db
# R-C3D (https://gitlab.kitware.com/kwiver/R-C3D)
import caffe
from tdcnn.config import cfg_from_file, cfg
from tdcnn.test_online import test_net_online
import diva_python_utils


# Now for the process
class RC3DProcess(KwiverProcess):
    """
    This process gets ain image as input, does some stuff to it and
    sends the modified version to the output port.
    """
    # ----------------------------------------------
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("experiment_file_name", "experiment_file_name",
                            '.', 'experiment configuration for RC3D')
        self.declare_config_using_trait('experiment_file_name')
        self.add_config_trait("model_cfg", "model_cfg",
                            '.', 'model configuration for RC3D')
        self.declare_config_using_trait('model_cfg')
        self.add_config_trait("stride", "stride",
                            '8', 'Temporal Stride for RC3D')
        self.declare_config_using_trait('stride')
        
        self.add_config_trait("gpu", "gpu", "0", "gpu for rc3d")
        self.declare_config_using_trait("gpu")

        # set up required flags
        required = process.PortFlags()
        required.add(self.flag_required)
        #  declare our ports ( port-name, flags)
        self.declare_input_port_using_trait('image', required)
        self.declare_input_port_using_trait('timestamp', required )

        self.declare_output_port_using_trait('detected_object_set', process.PortFlags() )

        

    # ---------------------------------------------
    def _configure(self):
        # look for 'experiment_file_name' key in the config
        expcfg_from_file(self.config_value('experiment_file_name'))
        cfg_from_file(self.config_value('model_cfg'))
        # merge experiment configuration and network configuration
        if experiment_config.json:
            self.classes = generate_classes_from_json(os.path.join(
                                            experiment_config.data_root,
                                            experiment_config.class_index))
        else:
            self.classes = generate_classes(os.path.join(
                                        experiment_config.data_root,
                                        experiment_config.class_index))
        window_length = cfg.TRAIN.LENGTH[0]
        self.gpu_id = int(self.config_value('gpu'))
        cfg.GPU_ID = self.gpu_id
        experiment_config.gpu = self.gpu_id
        print 'Testing the network'
        # Set device and load the network
        caffe.set_mode_gpu()
        caffe.set_device(self.gpu_id)
        self.net = caffe.Net(os.path.join(experiment_config.model_root,
                                     experiment_config.test.network),
                        os.path.join(experiment_config.experiment_root,
                                     experiment_config.results_path,
                                     experiment_config.test.model), caffe.TEST)
        self.net.name = os.path.splitext(os.path.basename(experiment_config.test.model))[0]
        # Initialize buffer for RC3D
        self.previous_buffer = None
        
    def compute_absolute_frame(self, frame, buffer_start):
        return buffer_start + frame * int(self.config_value("stride"))

    # ----------------------------------------------
    def _step(self):
        # grab image container from port using traits
        in_img_c = self.grab_input_using_trait('image')
        ts = self.grab_input_using_trait('timestamp')

        # Set device configuration for the thread 
        caffe.set_mode_gpu()
        caffe.set_device(self.gpu_id)

        # Get numpy array from the image container
        image = in_img_c.image().asarray()
        det_set = DetectedObjectSet()

        # Strided execution (temporal stride of 8)
        if ts.get_frame()%int(self.config_value('stride')) == 0:
            logs, self.previous_buffer = test_net_online(self.net, 
                                in_img_c.image().asarray(), ts.get_frame(), 
                                int(self.config_value('stride')),
                                max_per_image=experiment_config.test.max_detections,
                                vis=experiment_config.test.visualize,
                                previous_buffer=self.previous_buffer,
                                use_running_frames=True, 
                                dataset_id="pipeline-streamint-input")
            buffer_start = ts.get_frame() - \
                            int(self.config_value('stride')) * cfg.TEST.LENGTH[0]
            if buffer_start <= 0:
                buffer_start = 0

            # Add temporal annotation to detected object set
            classes = []
            scores = []
            for activity_id, bboxes in logs.activities.iteritems():
                for bbox in bboxes:
                    start_frame, end_frame, conf = bbox
                    start_frame = self.compute_absolute_frame(start_frame, buffer_start)
                    end_frame = self.compute_absolute_frame(end_frame, buffer_start)
                    if ts.get_frame() >= start_frame and ts.get_frame() <= end_frame:
                        classes.append(self.classes[activity_id])
                        scores.append(conf)
                        break
            assert len(classes)==len(scores),"Print classes and scores should have same length"
            if len(classes) > 0:
                print "Length: " + str(len(det_set))
                print "Classes: " + str(classes) + " Scores: " + str(scores)
                box = BoundingBox(0, 0, image.shape[1], 
                                image.shape[0])
                dot = DetectedObjectType(classes, scores)
                det_set.add(DetectedObject(box, 0.0, dot))
        # push the set to port
        self.push_to_port_using_trait('detected_object_set', det_set)


# ==================================================================
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.RC3DProcess'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('RC3DProcess', 'Apply R-C3D detector to image stream', RC3DProcess)

    process_factory.mark_process_module_as_loaded(module_name)
