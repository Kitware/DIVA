# -*- coding: utf-8 -*-
"""
Kwiver process to write ``object_track_set`` from ACT and ``detected_object_set``
from an object detector in NIST specified JSON 
format

@author: Ameya Shringi
"""

#kwiver/sprokit import
from sprokit.pipeline import process
from kwiver.kwiver_process import KwiverProcess

# ACT imports
from exp_config import experiment_config, expcfg_from_file
from virat_dataset import ViratDataset

import threading
import os
import cv2
import numpy as np
import json


class ACTJsonWriter(KwiverProcess):
    """
    Write ``object_track_set`` from ACT and ``detected_object_set`` from an object 
    detector in NIST specified JSON format

    * Input Ports:
        * ``object_track_set`` Tracks obtained from ACT (Required)
        * ``timestamp`` Timestamp associated with the input from which tracks were obtained (Required)
        * ``file_name`` Name of the input source (Required)
        * ``detected_object_set`` Detections obtained from object detector
    * Output Ports:
        * None

    * Configuration:
        * ``exp`` Experiment configuration for ACT (Eg. `exp.yml`_)
        * ``is_aod`` Flag to specify the task for which ACT is used (Default=False)
        * ``confidence_threshold`` Lower bound for confidence associated with an activity (Default=0.2)
        * ``json_path`` Path to json file produced by the writer (default=sysfile.json)
    
    .. Repo Links

    .. _exp.yml: https://gitlab.kitware.com/kwiver/act_detector/blob/act-detector/virat-act-detector-scripts/rgb_actev.yml

    """
    def _parse_bool(self, bool_str):
        """
        Helper function parse boolean string
        :param bool_str: boolean string that must be parsed
        :return boolean associated with the string
        """
        if bool_str == "True":
            return True
        else:
            return False

    def __init__(self, conf):
        """
        Constructor for ACT json writer
        :param conf: Configuration for ACT json writer
        :return None
        """
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("exp", "exp", "experiment.yml", 
                                    "experiment configuration")
        self.declare_config_using_trait("exp")
        self.add_config_trait("is_aod", "is_aod", "False",
                        "Flag to specify if AD/AOD annotation are generated")
        self.declare_config_using_trait("is_aod")
        self.add_config_trait("confidence_threshold", "confidence_threshold",
                        "0.2", "Confidence threshold for the scorer")
        self.declare_config_using_trait("confidence_threshold")
        self.add_config_trait("json_path", "json_path", "sysfile.json",
                        "Json path for system output")
        self.declare_config_using_trait("json_path")
        
        # set up required flags
        required = process.PortFlags()
        required.add(self.flag_required)
        optional = process.PortFlags()
        self.declare_input_port_using_trait("object_track_set", required)
        self.declare_input_port_using_trait("timestamp", required)
        self.declare_input_port_using_trait("file_name", required)
        self.is_aod = self._parse_bool(self.config_value("is_aod"))
        self.declare_input_port_using_trait("detected_object_set", optional)
        self.all_files = []

    def _configure(self):
        """
        Configure ACT json writer process
        """
        expcfg_from_file(self.config_value("exp"))
        if os.path.exists(self.config_value("json_path")):
            os.remove(self.config_value("json_path"))
        self.virat_dataset = ViratDataset(#experiment_config.data.data_root, 
                                    experiment_config.data.frame_roots, 
                                    experiment_config.data.flow_roots,
                                    experiment_config.data.train_annotation_dirs,
                                    experiment_config.data.test_annotation_dirs,
                                    experiment_config.data.class_index, 
                                    experiment_config.data.save_directory,
                                    experiment_config.train.kpf_mode,
                                    experiment_config.train.json_mode,
                                    experiment_config.data.save_prefix)
        self.activity_id = 1
        self.all_activities = []
        if self.is_aod:
            self.detected_object_sets = {}


    def _tubescore(self, tube):
        """
        Helper function to compute average scores of a track
        :param tube: track in form of an ndarray
        :return average of scores
        """
        return np.mean(tube)

    def _video_name_from_path(self, video_path):
        """
        Helper function to get video name form the path
        :param video_path: absolute path to the video
        :return name of the video
        """
        return os.path.split(video_path)[-1] + ".mp4"    

    def _iou(self, activity_detection, object_detection):
        """
        Helper function to compute iou between an activity track and an object detection
        :activity detection: instance of activity track
        :object detection: instance of object detection
        :return iou between two detections
        """
        min_x = max(activity_detection.min_x(), 
                    object_detection.min_x())
        min_y = max(activity_detection.min_y(),
                    object_detection.min_y())
        max_x = min(activity_detection.max_x(),
                    object_detection.max_x())
        max_y = min(activity_detection.max_y(),
                    object_detection.max_y())

        if min_x > max_x or min_y > max_y:
            return 0.0
        else:
            intersection = ( max_x - min_x ) * ( max_y - min_y )
            union = activity_detection.area() + \
                    object_detection.area() - \
                    intersection
            try:
                iou = float(intersection)/union
            except ZeroDivisionError:
                iou = 0.0
            return iou

    def _compute_participating_objects(self, track, video_name):
        """
        Helper function to find out all the object detections associated with an
        activity track and create NIST specifi annotation for those object detections
        :param track: Instance of activity detection
        :param video_name: Input source
        :return List of object annotations
        """
        object_annotations = []
        object_id = 1
        for track_state in track:
            frame_id = track_state.frame_id
            track_detection = track_state.detection.bounding_box()
            if frame_id in self.detected_object_sets.keys():
                object_detections = self.detected_object_sets[frame_id]
            else:
                continue
            for object_detection in object_detections:
                if self._iou(track_detection, object_detection.bounding_box()) > 0.5:
                    object_annotation = {
                        "objectType": object_detection.type().get_most_likely_class(),
                        "objectID": int(object_id),
                        "localization": {
                            video_name: {
                                str(int(frame_id)): {
                                    "presenceConf": float(object_detection.confidence()),
                                    "boundingBox": {
                                        "x": int(object_detection.bounding_box().min_x()),
                                        "y": int(object_detection.bounding_box().min_y()),
                                        "w": int(object_detection.bounding_box().width()),
                                        "h": int(object_detection.bounding_box().height())
                                    }
                                },
                                str(int(frame_id + 1)): {}
                            }
                        }
                    }
                    object_id += 1
                    object_annotations.append(object_annotation)
        if len(object_annotations) > 0:
            print "Added object annotations"
        return object_annotations

    def _create_annotation_from_track(self, track, activity_id, video_name, 
                                        is_aod=False):
        """
        Helper function to create activity annotation from track
        :param track: An instance of the activity track
        :param activity_id: Current value of the unique id used in activity annotation
        :param video_name: Input source
        :param is_aod: Flag to specify is the annotation is for activity detection or activity object detection (default=False)
        :return (activity annoation, new value of activity id )
        """
        start_frame = track.first_frame + 1
        end_frame = track.last_frame + 1
        num_frames = len(track)
        tube_scores = np.zeros(num_frames)
        label = int(track[track.first_frame].detection.type().get_most_likely_class())
        for track_index, track_state in enumerate(track):
            tube_scores[track_index] = track_state.detection.confidence()
        confidence = self._tubescore(tube_scores)

        if confidence > float(self.config_value("confidence_threshold")):
            if is_aod:
                participating_objects = self._compute_participating_objects(track, video_name)
            class_label = self.virat_dataset.labels.keys()[self.virat_dataset.labels.\
                                    values().index(label)]
            if is_aod:
                if len(participating_objects) > 0:
                    return {"activity": class_label, 
                            "activityID": int(activity_id),
                            "presenceConf": float(confidence),
                            "alertFrame": int(end_frame),
                            "localization": {
                                        video_name:     {
                                                            str(start_frame): 1,
                                                            str(end_frame): 0
                                                        }    
                                            },
                            "objects": participating_objects                    
                            }, activity_id+1
                else:
                    return None, activity_id
            else:
                return {"activity": class_label, 
                        "activityID": int(activity_id),
                        "presenceConf": float(confidence),
                        "alertFrame": int(end_frame),
                        "localization": {
                                        video_name :
                                            {
                                                str(start_frame): 1,
                                                str(end_frame): 0
                                            }    
                                    }
                    
                        }, activity_id+1
        else:
            return None, activity_id


    def _step(self):
        """
        Step function for ACT Json Writer
        """
        object_track_set = self.grab_input_using_trait('object_track_set')
        timestamp = self.grab_input_using_trait('timestamp')
        file_name = self.grab_input_using_trait('file_name')
        if self.is_aod:
            detected_object_set = self.grab_input_using_trait('detected_object_set')
            self.detected_object_sets[timestamp.get_frame()] = detected_object_set
        else:
            detected_object_set = None

        if len(object_track_set) > 0:
            for track in object_track_set.tracks():
                activity_annotation, self.activity_id = \
                            self._create_annotation_from_track(track, 
                                    self.activity_id, file_name, self.is_aod)
                if activity_annotation is not None:
                    self.all_activities.append(activity_annotation)

        if file_name not in self.all_files:
            self.all_files.append(file_name)
        #if self.is_aod:
        #    self.detected_object_sets = {}

         
        json_dict = {"filesProcessed": self.all_files, \
                        "activities": self.all_activities}
        with open(self.config_value("json_path"), 'w') as json_f:
            json.dump(json_dict, json_f, indent=4)
		
        
        
def __sprokit_register__():
    """
    Sprokit registration for the process
    """
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.ACTJsonWriter'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('ACTJsonWriter', 
                                'Produce NIST specified JSON file for ACT', 
                                ACTJsonWriter)

    process_factory.mark_process_module_as_loaded(module_name)
