# -*- coding: utf-8 -*-
"""
Kwiver process to visualize act predictions

@author: Ameya Shringi
"""

#kwiver/sprokit import
from sprokit.pipeline import process
from kwiver.kwiver_process import KwiverProcess
from vital.types import ImageContainer, DetectedObjectType, ObjectTrackSet
from vital.util import VitalPIL

# ACT imports
from exp_config import experiment_config, expcfg_from_file
from virat_dataset import ViratDataset

import threading
import os
import cv2
import numpy as np
import json
from PIL import Image

# Global colours for 19 activities
ACTIVITY_COLORS = [
                    (51, 0, 0),
                    (153, 0, 0),
                    (102, 51, 0),
                    (200, 0, 0),
                    (51, 51, 0),
                    (25, 51, 0),
                    (16, 148, 46),
                    (119, 124, 57),
                    (0, 102, 51),
                    (0, 102, 102),
                    (0, 76, 153),
                    (0, 0, 204),
                    (25, 0, 51),
                    (0, 0, 153),
                    (102, 0, 204),
                    (102, 0, 102),
                    (153, 0, 76),
                    (88, 10, 49),
                    (31, 96,119)
                ]

class ACTVisualizer(KwiverProcess):
    """
    Render ``track_object_set`` from ACT and ``detected_object_set`` from object 
    detector on an image
    
    .. note::
        The tracks visualized are intermediate tracks and not the final track.

    * Input Ports:
        * ``image`` Input RGB image used by ACT (Required)
        * ``timestamp`` Timestamp associated with the image (Required)
        * ``object_track_set`` Tracks obtained from ACT (Required)
        * ``detected_object_set`` Detections obtained from object detector (Optional)

    * Output Ports:
        * ``image`` Output image with bounding box representing spatial localization of an activity

    * Configuration:
        * ``exp`` Experiment configuration for ACT (Eg. `exp.yml`_)
        * ``is_aod`` Flag to specify the task for which ACT is used (Default=False)
        
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
        Constructor for ACT visualizer
        :param conf: Configuration for ACT visualizer
        :return None
        """
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("exp", "exp", "experiment.yml", 
                                    "experiment configuration")
        self.declare_config_using_trait("exp")
        self.add_config_trait("is_aod", "is_aod", "False",
                        "Flag to specify if AD/AOD annotation are generated")
        self.declare_config_using_trait("is_aod")
        
        # set up required flags
        required = process.PortFlags()
        required.add(self.flag_required)
        optional = process.PortFlags()
        self.declare_input_port_using_trait("image", required)
        self.declare_input_port_using_trait("timestamp", required)
        self.declare_input_port_using_trait("object_track_set", required)
        self.is_aod = self._parse_bool(self.config_value("is_aod"))
        self.declare_input_port_using_trait("detected_object_set", optional)
        self.declare_output_port_using_trait("image", optional)
        self.object_track_set = ObjectTrackSet()

    def _configure(self):
        """
        Configure ACT process
        """
        expcfg_from_file(self.config_value("exp"))
        self.virat_dataset = ViratDataset(
                                    experiment_config.data.frame_roots, 
                                    experiment_config.data.flow_roots,
                                    experiment_config.data.train_annotation_dirs,
                                    experiment_config.data.test_annotation_dirs,
                                    experiment_config.data.class_index, 
                                    experiment_config.data.save_directory,
                                    experiment_config.train.kpf_mode,
                                    experiment_config.train.json_mode,
                                    experiment_config.data.save_prefix)

    def _draw_trajectory(self, image, detection):
        """
        Helper function to draw small circle at center of detection on a image
        :param image: Input image
        :param detection: Input detection
        :return Image with small circle computed using the detection
        """
        x_coor = detection.bounding_box().max_x()
        y_coor = float(detection.bounding_box().min_y() + \
                        detection.bounding_box().max_y())/2
        cv2.circle(image, tuple(map(int,(x_coor, y_coor))), 2, (255, 0, 0) )
        return image

    def _draw_detection(self, image, detection, is_activity):
        """
        Helper function to draw activity and object detection on an image
        :param image: Input image
        :param detection: Instance of detection (Activity/object)
        :param is_activity: flag to specify is the detection is from an activity
        :return Image with bounding box rendered
        """
        if is_activity:
            label_id = int(detection.type().get_most_likely_class())
            label = self.virat_dataset.labels.keys()[self.\
                    virat_dataset.labels.values().index(label_id)]
            color = ACTIVITY_COLORS[label_id-1]
        else:
            label = detection.type().get_most_likely_class()
            color = (32, 32, 32)
        cv2.rectangle(image, tuple(map(int, (detection.bounding_box().min_x(), 
                                detection.bounding_box().max_y()))),
                             tuple(map(int, (detection.bounding_box().max_x(), 
                                 detection.bounding_box().min_y()))), color, 3)
        font = cv2.FONT_HERSHEY_SIMPLEX
        label += " ({:4.4f})".format(detection.confidence())
        text_size, _ = cv2.getTextSize(label, font, 0.5, 1)
        text_width, text_height = text_size
        label_top = detection.bounding_box().max_x() - text_width - 2, \
                        detection.bounding_box().min_y() - text_height - 2
        if label_top[0] > 0 and label_top[1] > 0:
            # draw the other box
            cv2.rectangle(image, tuple(map(int, label_top)), tuple(map(int, 
                ( label_top[0] + text_width + 2, label_top[1] + text_height + 2 ))), 
                color, cv2.FILLED)
            cv2.putText(image, label, tuple(map(int, (label_top[0]+1, 
                        label_top[1]+text_height+1))), font, 0.5, (255, 255, 255), 1)
        return image

    def _draw_track(self, image, track):
        """
        Draw activity track on an image
        :param image: Input image
        :param track: Instance of track
        :return Image with track rendered
        """
        label_id = int(track[track.last_frame].detection.type().get_most_likely_class())
        if label_id == 0:
            return image
        if track.size > 1:
            for track_id in range(track.first_frame, track.last_frame):
                image = self._draw_trajectory(image, track[track_id].detection)
        image = self._draw_detection(image, track[track.last_frame].detection, True)
        return image

    def _step(self):
        """
        Step function for the visualizer
        """
        object_track_set = self.grab_input_using_trait('object_track_set')
        timestamp = self.grab_input_using_trait('timestamp')
        image = self.grab_input_using_trait('image').image().asarray().astype(np.uint8)
        image = cv2.resize(image, (1920, 1080))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if self.is_aod:
            detected_object_set = self.grab_input_using_trait('detected_object_set')
        else:
            detected_object_set = None

        # Draw tracks
        
        if len(object_track_set) > 0 and timestamp.get_frame() > 1:
            for track in object_track_set.tracks():
                image = self._draw_track(image, track)
                self.object_track_set = object_track_set
        elif len(object_track_set) == 0 and timestamp.get_frame() > 1:
            for track in self.object_track_set.tracks():
                image = self._draw_track(image, track)
        
        # Draw detected object set
        if self.is_aod:
            if len(detected_object_set) > 0:
                for detected_object in detected_object_set:
                    image = self._draw_detection(image, detected_object, False)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(image)
        vital_image = VitalPIL.from_pil(pil_image)
        image_container = ImageContainer(vital_image)
        self.push_to_port_using_trait("image", image_container)
        
        
def __sprokit_register__():
    """
    Sprokit registration for the process
    """
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.ACTVisualizer'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('ACTVisualizer', 
                                'Visualize predictions from ACT and Object detector', 
                                ACTVisualizer)

    process_factory.mark_process_module_as_loaded(module_name)
