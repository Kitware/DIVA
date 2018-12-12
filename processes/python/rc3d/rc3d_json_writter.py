# -*- coding: utf-8 -*-
"""
Kwiver process to write ``detected_object_set`` from RC3D into NIST specified JSON format

@author: Ameya Shringi
"""

#kwiver/sprokit import
from sprokit.pipeline import process, datum
from kwiver.kwiver_process import KwiverProcess
from vital.types import DetectedObjectSet, BoundingBox, DetectedObject, DetectedObjectType

import os
import numpy
import json
import math
import threading

# RC3D imports
import _init_paths
from log_to_nist import generate_classes, generate_classes_from_json
from tdcnn.exp_config import expcfg_from_file, experiment_config
from tdcnn.config import cfg_from_file, cfg

class RC3DJsonWriter(KwiverProcess):
    """
    Write ``detected_object_set`` from RC3D into NIST specified JSON format
    
    * Input Ports:
        * ``detected_object_set`` Detected object set obtained from RC3D (Required)
        * ``timestamp`` Timestamp associated with the input from which the detected object set was obtained from (Required)
        * ``file_name`` Name of the input source (Required)

    * Output Ports:
        * None

    * Configuration:
        * ``experiment_file_name`` Experiment configuration used by RC3D (Eg. `experiment.yml`_)
        * ``model_cfg`` Model configuration used by RC3D (Eg. `td_cnn_end2end.yml`_)
        * ``stride`` Temporal stride for RC3D (default=8)
        * ``temporal_buffer`` Buffer frames when merging frames (default=8)
        * ``json_path`` Path where output json file is saved (default=sysfile.json)
        * ``confidence_threshold`` Minimum confidence threshold used by RC3D to  accept an activity detection (default=0.05)

    .. Repo links:

    .. _td_cnn_end2end.yml: https://gitlab.kitware.com/kwiver/R-C3D/blob/master/experiments/virat/td_cnn_end2end.yml
    .. _experiment.yml: https://gitlab.kitware.com/kwiver/R-C3D/tree/master/experiments/virat/experiment.yml
    """
    def __init__(self, conf):
        """
        Constructor for RC3D json writer
        :param conf: configuration parameters for RC3D json writer
        :return None
        """
        KwiverProcess.__init__(self, conf)
        # Experiment configuration
        self.add_config_trait("experiment_file_name", "experiment_file_name", \
                                "experiment.yml",
                                "experiment configuration")
        self.declare_config_using_trait('experiment_file_name')
        self.add_config_trait("model_cfg", "model_cfg", \
                                "td_cnn_end2end.yml",
                                "model configuration")
        self.declare_config_using_trait('model_cfg')
        # Temporal Buffer used for merging frames (Not used yet)
        self.add_config_trait("temporal_buffer", "temporal_buffer", \
                                "8", "Allow for some buffer when merging frames")
        self.declare_config_using_trait('temporal_buffer')
        # Match the stride with RC3D's temporal stride
        self.add_config_trait("stride", "stride", \
                                "8", "Temporal stride for RC3D")
        self.declare_config_using_trait("stride")
        # Save path for json
        self.add_config_trait("json_path", "json_path", \
                                "sysfile.json", "Path to save the json file")
        self.declare_config_using_trait("json_path")
        # Threshold to add an activity instance to the log
        self.add_config_trait("confidence_threshold", "confidence_threshold", \
                                "0.05", "confidence threshold for the scorer")
        self.declare_config_using_trait("confidence_threshold")
        # set up required flags
        required = process.PortFlags()
        required.add(self.flag_required)
        self.declare_input_port_using_trait("detected_object_set", required)
        self.declare_input_port_using_trait('timestamp', required )
        self.declare_input_port_using_trait('file_name', required )

    def _configure(self):
        """
        Configure RC3D Json Writer
        """
        # look for 'experiment_file_name' key in the config
        expcfg_from_file(self.config_value('experiment_file_name'))
        if os.path.exists(self.config_value("json_path")):
            print ("Removing old system output file")
            os.remove(self.config_value("json_path"))
        # experiment configuration
        cfg_from_file(self.config_value('model_cfg'))
        self.activity_id = 0
        if experiment_config.json:
            self.classes = generate_classes_from_json(experiment_config.class_index)
        else:
            self.classes = generate_classes(experiment_config.class_index)
        self.current_activity_frames = [-1]*len(self.classes)
        self.start_frames = [0]*len(self.classes)
        video_processed = []
        self.segments = []


    def _step(self):
        """
        Step function for RC3D Json Writer
        """
        # Read detected object set and timestamp
        detected_object_set = self.grab_input_using_trait('detected_object_set')
        ts = self.grab_input_using_trait('timestamp')
        file_name = self.grab_input_using_trait('file_name')
        if len(detected_object_set) > 0:
            for i in range(len(detected_object_set)):
                print "Detected set: " + str(detected_object_set[i].type().class_names(0.0))
                detected_object = detected_object_set[i]
                object_type = detected_object.type()
                if len(object_type.class_names(0.0)) > 0:
                    # Get class name and scores for the activity
                    for class_name in object_type.class_names(0.0):
                        score = object_type.score(class_name)
                        act_id = self.classes.keys()[self.classes.values().
                                                    index(class_name)]
                    
                        if score > float(self.config_value('confidence_threshold')):
                            if int(ts.get_frame()) > 0:
                                self.segments.append({
                                    'activity': str(class_name),
                                    'activityID': int(self.activity_id),
                                    'presenceConf': float(score),
                                    'alert_frame': int(ts.get_frame()), 
                                    'localization': {str(file_name) : {int(ts.get_frame()): 0, 
                                            int(ts.get_frame())- \
                                                    int(self.config_value("stride"))+1: 1}}
                                })
                            else:
                                self.segments.append({
                                    'activity': str(class_name),
                                    'activityID': int(self.activity_id),
                                    'presenceConf': float(score),
                                    'alert_frame': int(ts.get_frame()), 
                                    'localization': {str(file_name) : {int(ts.get_frame())+1: 0, 
                                                                int(ts.get_frame()): 1}}
                                })
                            self.activity_id += 1
                            self.start_frames[act_id] = ts.get_frame()

                else:
                    # This should not execute (Added for debugging purposes)
                    print "Missing object class"

            if len(self.segments) > 0:
                if os.path.exists(self.config_value("json_path")):
                    json_dict = json.load(open(self.config_value('json_path')))
                    if file_name not in json_dict["filesProcessed"]:
                        json_dict["filesProcessed"].append(file_name)
                    json_dict['activities'] = self.segments
                    json.dump(json_dict, open(self.config_value('json_path'), 'w'), 
                                indent=2)
                else:
                    video_processed = [file_name]
                    results = {'filesProcessed': video_processed, 
                               'activities': self.segments}
                    json.dump(results, open(self.config_value('json_path'), 'w'),  
                            indent=2)

            
        
def __sprokit_register__():
    """
    Sprokit registration for the process
    """
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.RC3DJsonWriter'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('RC3DJsonWriter', 
                'Write detected_object_set from rc3d to NIST specified JSON format', 
                RC3DJsonWriter)

    process_factory.mark_process_module_as_loaded(module_name)
