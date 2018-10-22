# -*- coding: utf-8 -*-
"""
Kwiver process to draw swimlane plots 

@author: Ameya Shringi
"""

#kwiver/sprokit import
from sprokit.pipeline import process, datum
from kwiver.kwiver_process import KwiverProcess
from vital.types import ImageContainer
from vital.util import VitalPIL
import _init_paths
import threading
from tdcnn.exp_config import expcfg_from_file, experiment_config
from log_to_nist import sys_to_res, generate_classes
from PIL import Image

import cv2
import numpy as np
import os


class SwimlaneProcess(KwiverProcess):
    """
    This process draws swimlane plots depicting the history of activity detection
    """
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("experiment_file_name", "experiment_file_name",
                            '.', 'experiment configuration for RC3D')
        self.declare_config_using_trait('experiment_file_name')
        self.add_config_trait("stride", "stride", "8", 
                                "temporal stride of the model")
        self.declare_config_using_trait("stride")
        self.add_config_trait("width", "width", "1920", 
                                "width of the image that is visualized")
        self.declare_config_using_trait("width")
        self.add_config_trait("text_height", "text_height", "40", 
                                "height of the text")
        self.declare_config_using_trait("text_height")
        self.add_config_trait("text_width", "text_width", "90", 
                                "width of the text")
        self.declare_config_using_trait("text_width")
        self.add_config_trait("text_buffer", "text_buffer", "5", 
                                "buffer between text")
        self.declare_config_using_trait("text_buffer")

        # set up required flags
        required = process.PortFlags()
        required.add(self.flag_required)
        self.declare_input_port_using_trait("detected_object_set", required)
        self.declare_input_port_using_trait("timestamp", required)

        self.declare_output_port_using_trait('image', process.PortFlags())
	self.lock = threading.Lock()


    def _configure(self):
        # Get class names
        expcfg_from_file(self.config_value('experiment_file_name'))
        self.classes = generate_classes(os.path.join(
                                        experiment_config.data_root,
                                        experiment_config.class_index))
        # Compute image height based on the number of classes
        self.image_height = len(self.classes) * (int(self.config_value("text_height")) + 
                            int(self.config_value("text_buffer")))
        self.image_height += int(self.config_value("text_buffer"))
        # Initialize swimlanes
        self.swimlanes = [[] for _ in range(len(self.classes))]
        

    def _step(self):
        # Read detected object set and timestamp
        detected_object_set = self.grab_input_using_trait('detected_object_set')
        ts = self.grab_input_using_trait('timestamp')

        # Setup text attributes
        font = cv2.FONT_HERSHEY_SIMPLEX
        image_width = int(self.config_value("width"))
        text_buffer = int(self.config_value("text_buffer"))
        text_height = int(self.config_value("text_height"))
        image = np.ones((self.image_height, image_width, 3), 
                        dtype=np.uint8) * 255
        largest_width = -1
        class_dict = {}

        # Compute width of the largest class and initialize swimlane value for 
        # current frame
        for value_index, value in enumerate(self.classes.values()):
                text_size, _ = cv2.getTextSize(value, font, 1, 4)
                if text_size[0] > largest_width:
                    largest_width = text_size[0]
                cv2.putText(image, str(value), (text_buffer,
                            (text_height+text_buffer)*value_index + text_height), 
                            font, 1, (0, 0, 0), 4)
                class_dict[value] = value_index
                self.swimlanes[value_index].append(0)

        # For strided frame change the swimlane of detected activity to 1
        if int(ts.get_frame())%int(self.config_value("stride")) == 0:
            if len(detected_object_set) > 0:
                for i in range(len(detected_object_set)):
                    object_type = detected_object_set[i].type()
                    if len(object_type.class_names(0.0)) > 0:
                        # Get class name and modify the swimlanes for the same
                        for class_name in object_type.class_names(0.0):
                            self.swimlanes[class_dict[class_name]][ts.get_frame()] = 1
        # Propogate swimlane value from the previous stride where RC3D executed
        else:
            for index in range(len(self.swimlanes)):
                if ts.get_frame()>=1 and self.swimlanes[index][ts.get_frame()-1] == 1:
                    self.swimlanes[index][ts.get_frame()] = 1

        # Compute total lane size and cell size
        lane_size = image_width - largest_width - 2*text_buffer
        cell_size = lane_size // len(self.swimlanes[0])
	
        # Color the lanes (Red signifies no activity and blue signifies activity)
        for index, swimlanes in enumerate(self.swimlanes):
            start_point_x = largest_width + 2*text_buffer
            start_point_y = (index+1) * text_height + index * text_buffer - 15
            end_point_y = start_point_y
            for cell_value in swimlanes:
                end_point_x = start_point_x + cell_size
                if cell_value == 0:
                    line_color = (255, 0, 0)
                elif cell_value == 1:
                    line_color = (0, 0, 255)
                else:
                    line_color = (0, 0, 0)
                cv2.line(image, (start_point_x, start_point_y), \
                                (end_point_x, end_point_y), line_color, 15)
                start_point_x = end_point_x

        # Pass the image to the image viewer
	if self.lock.acquire(False):
            pil_image = Image.fromarray(image)
            vital_image = VitalPIL.from_pil(pil_image)
            image_container = ImageContainer(vital_image)
            self.push_to_port_using_trait('image', image_container)
	    self.lock.release()
        
        
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.SwimlaneProcess'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('SwimlaneProcess', 
                                'Draw dynamic swimlanes', 
                                SwimlaneProcess)

    process_factory.mark_process_module_as_loaded(module_name)
