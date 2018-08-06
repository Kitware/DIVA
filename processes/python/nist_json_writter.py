# -*- coding: utf-8 -*-
"""
Kwiver process to write Detetected object set into NIST specified JSON format

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

# RC3D imports
import _init_paths
from log_to_nist import generate_classes
from tdcnn.exp_config import expcfg_from_file, experiment_config
from tdcnn.config import cfg_from_file, cfg

class NISTJSONWriter(KwiverProcess):
    """
    This process takes the detected object sets and converts them into NIST
    specified JSON format
    """
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        # Experiment configuration
        self.add_config_trait("experiment_file_name", "experiment_file_name", \
                                "experiment.yml",
                                "experiment configuration")
        self.declare_config_using_trait('experiment_file_name')
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

    def _configure(self):
        # look for 'experiment_file_name' key in the config
        expcfg_from_file(self.config_value('experiment_file_name'))
        
        # experiment configuration
        if experiment_config.cnn_config is not None:
            cfg_from_file(os.path.join(experiment_config.experiment_root,
                                       experiment_config.cnn_config))
        self.activity_id = 0
        self.classes = generate_classes(os.path.join(experiment_config.data_root,
                                     experiment_config.class_index))
        self.current_activity_frames = [-1]*len(self.classes)
        self.start_frames = [0]*len(self.classes)
        video_processed = []
        self.segments = []


    def _step(self):
        # Dump to json file in the end
        edat = self.peek_at_datum_on_port('timestamp')
        if edat.type == datum.complete:
            video_processed = ["test"]
            results = {'filesProcessed': video_processed, 
                        'activities': self.segments}
            print results
            json.dump(open(self.config_value('json_path'), 'w'), results, indent=2)

        # Read detected object set and timestamp
        detected_object_set = self.grab_input_using_trait('detected_object_set')
        ts = self.grab_input_using_trait('timestamp')
        if len(detected_object_set) > 0:
            for i in range(len(detected_object_set)):
                print "Detected set: " + str(detected_object_set[i].type().all_class_names())
                detected_object = detected_object_set[i]
                object_type = detected_object.type()
                if len(object_type.class_names(0.0)) > 0:
                    # Get class name and scores for the activity
                    for class_name in object_type.class_names(0.0):
                        score = object_type.score(class_name)
                        act_id = self.classes.keys()[self.classes.values().
                                                        index(class_name)]
                        
                        # If the activity was on the last frame and is on the current
                        # frame then increase the activity frame else create a new 
                        # segment
                        if (ts.get_frame() - \
                                int(self.config_value("stride"))> \
                                self.current_activity_frames[act_id]):
                            self.current_activity_frames[act_id] = ts.get_frame()
                        else:
                            if score > float(self.config_value('confidence_threshold')):
                                self.segments.append({
                                    'activity': class_name,
                                    'activityID': self.activity_id,
                                    'presenceConf': float(score),
                                    'alert_frame': self.current_activity_frames[act_id],
                                    'localization': {"test" : {self.start_frames[act_id]: 0, 
                                                    self.current_activity_frames[act_id]: 1}}
                                    })
                                self.activity_id += 1
                                self.start_frames[act_id] = ts.get_frame()
                        
                else:
                    # This should not execute (Added for debugging purposes)
                    print "Missing object class"
                
            
        
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.NISTJSONWriterProcess'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('NISTJSONWriterProcess', 
                                'Write detected object set to NIST specification', 
                                NISTJSONWriter)

    process_factory.mark_process_module_as_loaded(module_name)
