# -*- coding: utf-8 -*-
"""
Kwiver process to write AD and AOD detections from ACT

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
    This process takes the detected object sets and show them on the image
    """
    def _parse_bool(self, bool_str):
        if bool_str == "True":
            return True
        else:
            return False

    def __init__(self, conf):
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
        self.is_aod = self._parse_bool(self.config_value("is_aod"))
        self.declare_input_port_using_trait("detected_object_set", optional)

    def _configure(self):
        expcfg_from_file(self.config_value("exp"))
        if os.path.exists(self.config_value("json_path")):
            os.remove(self.config_value("json_path"))
        self.virat_dataset = ViratDataset(experiment_config.data.data_root, 
                                    experiment_config.data.frames_root, 
                                    experiment_config.data.flow_root,
                                    experiment_config.data.train_annotation_dirs,
                                    experiment_config.data.test_annotation_dirs,
                                    experiment_config.data.class_index, 
                                    experiment_config.data.save_directory,
                                    experiment_config.train.kpf_mode,
                                    experiment_config.train.json_mode,
                                    experiment_config.data.save_prefix)
        self.video_index = 0
        self.activity_id = 1
        self.num_videos = len(self.virat_dataset.test_video_list)
        self.all_activities = []
        self.video_path = self.virat_dataset.test_video_list[self.video_index]
        self.all_files = [self._video_name_from_path(self.video_path)]
        self.num_frames = self.virat_dataset.test_num_frames(self.video_path)
        if self.is_aod:
            self.detected_object_sets = {}


    def _tubescore(self, tube):
        return np.mean(tube)

    def _video_name_from_path(self, video_path):
        return os.path.split(video_path)[-1] + ".mp4"    

    def _iou(self, activity_detection, object_detection):
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
            return float(intersection)/union


    def _compute_participating_objects(self, track):
        object_annotations = []
        for track_state in track:
            frame_id = track_state.frame_id
            track_detection = track_state.detection.bounding_box()
            if frame_id in self.detected_object_sets.keys():
                object_detections = self.detected_object_sets[frame_id]
            else:
                continue
            object_id = 1
            for object_detection in object_detections:
                if self._iou(track_detection, object_detection.bounding_box()) > 0.5:
                    object_annotation = {
                        "objectType": object_detection.type().get_most_likely_class(),
                        "objectID": int(object_id),
                        "localization": {
                                self._video_name_from_path(self.video_path): {
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
        return object_annotations

    def _create_annotation_from_track(self, track, activity_id, 
                                        is_aod=False):
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
                participating_objects = self._compute_participating_objects(track)
            class_label = self.virat_dataset.labels.keys()[self.virat_dataset.labels.\
                                    values().index(label)]
            if is_aod:
                if len(participating_objects) > 0:
                    return {"activity": class_label, 
                            "activityID": int(activity_id),
                            "presenceConf": float(confidence),
                            "alertFrame": int(end_frame),
                            "localization": {
                                self._video_name_from_path(self.video_path):
                                            {
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
                            self._video_name_from_path(self.video_path):
                                            {
                                                str(start_frame): 1,
                                                str(end_frame): 0
                                            }    
                                    }
                    
                        }, activity_id+1
        else:
            return None, activity_id


    def _step(self):
        object_track_set = self.grab_input_using_trait('object_track_set')
        timestamp = self.grab_input_using_trait('timestamp')
        if self.is_aod:
            detected_object_set = self.grab_input_using_trait('detected_object_set')
            self.detected_object_sets[timestamp.get_frame()] = detected_object_set
        else:
            detected_object_set = None

        if len(object_track_set) > 0:
            for track in object_track_set.tracks():
                activity_annotation, self.activity_id = \
                            self._create_annotation_from_track(track, 
                                    self.activity_id, self.is_aod)
                if activity_annotation is not None:
                    self.all_activities.append(activity_annotation)
        # New video starts
        if timestamp.get_frame() == 1:
            self.video_path = self.virat_dataset.test_video_list[self.video_index]
            self.num_frames = self.virat_dataset.test_num_frames(self.video_path)
            if self._video_name_from_path(self.video_path) not in self.all_files:
                self.all_files.append(self._video_name_from_path(self.video_path))
            self.video_index += 1
            if self.is_aod:
                self.detected_object_sets = {}

         
        json_dict = {"filesProcessed": self.all_files, \
                        "activities": self.all_activities}
        with open(self.config_value("json_path"), 'w') as json_f:
            json.dump(json_dict, json_f, indent=4)
        print "Completed: {0}/{1} videos and {2}/{3} frames".format(
                self.video_index, self.num_videos, timestamp.get_frame(),
                self.num_frames )
		
        
        
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.ACTJsonWriter'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('ACTJsonWriter', 
                                'Produce NIST specified JSON file for ACT', 
                                ACTJsonWriter)

    process_factory.mark_process_module_as_loaded(module_name)
