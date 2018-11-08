# -*- coding: utf-8 -*-
"""
Kwiver process to visualize activities on an image 

@author: Ameya Shringi
"""

# kwiver/sprokit import
from sprokit.pipeline import process, datum
from kwiver.kwiver_process import KwiverProcess
from vital.types import ImageContainer
from vital.util import VitalPIL

# RC3D imports
from tdcnn.exp_config import expcfg_from_file, experiment_config
from log_to_nist import sys_to_res, generate_classes, generate_classes_from_json

from PIL import Image

import threading
import os
import cv2
import numpy as np
import copy

class VisualizeProcess(KwiverProcess):
    """
    This process takes the detected object sets and show them on the image
    """
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("experiment_file_name", "experiment_file_name",
                            '.', 'experiment configuration for RC3D')
        self.declare_config_using_trait('experiment_file_name')
        self.add_config_trait("stride", "stride", "8", 
                                "temporal stride of the model")
        self.declare_config_using_trait("stride")

        # Legend related parameters
        self.add_config_trait("legend_text_height", "legend_text_height", "10", 
                                "text height for legend")
        self.declare_config_using_trait("legend_text_height")
        self.add_config_trait("legend_text_width", "legend_text_width", "40", 
                                "text width for the legend")
        self.declare_config_using_trait("legend_text_width")
        self.add_config_trait("legend_text_buffer", "legend_text_buffer", "4", 
                                "text buffer for the legend")
        self.declare_config_using_trait("legend_text_buffer")
        self.add_config_trait("legend_text_font_scale", "legend_text_font_scale",
                                "0.8",  "font scale for the legend")
        
        
        self.declare_config_using_trait("legend_text_font_scale")
        
        # Swimlane related parameters
        self.add_config_trait("swimlane_text_height", "swimlane_text_height", "15", 
                                "height of the text")
        self.declare_config_using_trait("swimlane_text_height")
        self.add_config_trait("swimlane_text_width", "swimlane_text_width", "40", 
                                "width of the text")
        self.declare_config_using_trait("swimlane_text_width")
        self.add_config_trait("swimlane_text_buffer", "swimlane_text_buffer", "2",
                                "buffer between text")
        self.declare_config_using_trait("swimlane_text_buffer")
        self.add_config_trait("swimlane_text_font_scale", "swimlane_text_font_scale", "0.5",
                                "font scale used by swimlane")
        self.declare_config_using_trait("swimlane_text_font_scale")
        self.add_config_trait("num_swimlane_cells", "num_swimlane_cells", "500",
                                "Number of cells used in swimlane")
        self.declare_config_using_trait("num_swimlane_cells")
        self.add_config_trait("confidence_threshold", "confidence_threshold",
                                "0.2", "lower bound of confidence")
        self.declare_config_using_trait("confidence_threshold")

        # Input image parameters TODO: Check if these are redundant
        self.add_config_trait("image_width", "image_width", "1920",
                                "Overall image width")
        self.declare_config_using_trait("image_width")
        self.add_config_trait("image_height", "image_height", "1080",
                                "Overall image height")
        self.declare_config_using_trait("image_height")

        # set up required flags
        required = process.PortFlags()
        required.add(self.flag_required)
        self.declare_input_port_using_trait("image", required)
        self.declare_input_port_using_trait("detected_object_set", required)
        self.declare_input_port_using_trait("timestamp", required)

        self.declare_output_port_using_trait('image', process.PortFlags())
        self.frame_number = 1
	self.lock = threading.Lock()

    def _find_largest_class_width(self, classes, font_scale):
        text_size, _ = cv2.getTextSize(classes[0], self.font, font_scale, 1)
        largest_width = text_size[0]
        for value_index, value in enumerate(self.classes.values()):
            text_size, _ = cv2.getTextSize(value, self.font, font_scale, 1)
            if text_size[0] > largest_width:
                largest_width = text_size[0]
        return largest_width

    def _configure(self):
        expcfg_from_file(self.config_value('experiment_file_name'))
        if experiment_config.json:
            self.classes = generate_classes_from_json(os.path.join(
                                        experiment_config.data_root,
                                        experiment_config.class_index))
        else:
            self.classes = generate_classes(os.path.join(
                                        experiment_config.data_root,
                                        experiment_config.class_index))
        
        self.font = cv2.FONT_HERSHEY_SIMPLEX

        # Compute swimlane height based on the number of classes
        swimlane_font_height = cv2.getTextSize(self.classes[0], self.font, 
                    float(self.config_value("swimlane_text_font_scale")),1)[0][1]
                            
        self.swimlane_height = len(self.classes) * \
                        (max(swimlane_font_height, 
                            int(self.config_value("swimlane_text_height"))) + 
                            int(self.config_value("swimlane_text_buffer")) + 1)
        self.swimlane_height += int(self.config_value("swimlane_text_buffer"))
        self.swimlane_width = int(self.config_value("image_width"))
        # Compute legend based width and height based on number of classes
        self.legend_width = self._find_largest_class_width(self.classes,
                            float(self.config_value("legend_text_font_scale"))) + \
                            2*int(self.config_value("legend_text_buffer"))

        legend_font_height = cv2.getTextSize(self.classes[0], self.font, 
                            float(self.config_value("legend_text_font_scale")), 1)[0][1]
        self.legend_height = len(self.classes) * \
                        (max(legend_font_height,
                            int(self.config_value("legend_text_height"))) + 
                                        int(self.config_value("legend_text_buffer")))
        self.legend_height += int(self.config_value("legend_text_buffer"))
        # Compute image height
        self.image_width = int(self.config_value("image_width")) - \
                                    self.legend_width
        self.image_height = int(self.config_value("image_height")) - \
                                    self.swimlane_height
        
        # Adjust legend height based on availability of space
        self.legend_height = max(self.legend_height, self.image_height)
        # Initialize swimlanes
        self.swimlanes = {class_name: [] for class_name in self.classes.values()}
        # Initialize classes for legends
        self.previous_classes = []


    def _create_legend(self, legend_width, legend_height, legend_buffer, classes):
        #TODO take text buffer into account
        text_height = (legend_height - legend_buffer)/len(self.classes)
        legend_img = np.ones((legend_height, legend_width, 3), dtype=np.uint8) * 255
        for class_index, class_name in self.classes.iteritems():
            # Skip background
            if class_index == 0:
                continue
            if class_name in classes:
                color = (0, 255, 0)
            else:
                color = (0, 0, 0)
            # TODO: fix this
            cv2.putText(legend_img, class_name, ( legend_buffer,
                        text_height * class_index), 
                        self.font, float(self.config_value("legend_text_font_scale")), 
                        color, 2)
        return legend_img
        
    def _create_swimlane(self, swimlane_width, swimlane_height, swimlane_buffer, 
                            classes, num_swimlane_cells):
        #TODO take text buffer into account
        text_height = (swimlane_height - swimlane_buffer)/len(self.classes)
        text_scale  = float(self.config_value("swimlane_text_font_scale"))
        swimlane_img = np.ones((swimlane_height,swimlane_width, 3), dtype=np.uint8) * 255
        text_width = self._find_largest_class_width(self.classes, text_scale) + \
                            2*swimlane_buffer
        cell_size = float(swimlane_width - text_width)/num_swimlane_cells
        text_offset = text_width + 2*swimlane_buffer
        class_index = 1
        for class_name, swimlane in self.swimlanes.iteritems():
            if class_name == "Background":
                continue
            cv2.putText(swimlane_img, class_name, 
                        (swimlane_buffer,
                        text_height*class_index), 
                        self.font, text_scale, (0, 0, 0), 1)

            if len(swimlane) > num_swimlane_cells:
                # get last num_swimlane values of the cells
                cells  = swimlane[-num_swimlane_cells:]
            else:
                # partially rendered swimlane
                cells = swimlane[:]
                 
            start_point_x = text_offset 
            for cell_index, cell in enumerate(cells):
                end_point_x = int(text_offset + cell_size * (cell_index + 1))
                point_y = int((text_height)*class_index - 5)
                if cell == 0:
                    line_color = (171, 43, 16)
                elif cell == 1:
                    line_color = (0, 255, 0)
                else:
                    line_color = (0, 0, 0)
                cv2.line(swimlane_img, (start_point_x, point_y), 
                        (end_point_x, point_y), line_color, 5)
                start_point_x = end_point_x
            class_index += 1
        return swimlane_img        

    def _step(self):
        # Read detected object set, image and timestamp
        detected_object_set = self.grab_input_using_trait('detected_object_set')
        ts = self.grab_input_using_trait('timestamp')
        image_container = self.grab_input_using_trait('image')
        image = image_container.image().asarray().astype(np.uint8)
        
        # Intialize images
        op_img_width = int(self.config_value("image_width"))
        op_img_height = int(self.config_value("image_height"))
        output_image = np.ones((op_img_height, op_img_width, 3), dtype=np.uint8)*255
        
        # Initialize swimlanes
        for class_name in self.swimlanes.keys():
            self.swimlanes[class_name].append(0)

        current_classes = []
        # RC3D operates only on strided frames
        if int(self.frame_number)%int(self.config_value("stride")) == 0:
            if len(detected_object_set) > 0:
                for i in range(len(detected_object_set)):
                    object_type = detected_object_set[i].type()
                    if len(object_type.class_names(
                            float(self.config_value("confidence_threshold")))) > 0:
                        # Get class name on the current frame
                        for class_name in object_type.class_names(
                                    float(self.config_value("confidence_threshold"))):
                            self.swimlanes[class_name][self.frame_number] = 1
                            if class_name not in current_classes:
                                current_classes.append(class_name)
            self.previous_classes = copy.deepcopy(current_classes)
        else:
            for class_name in self.swimlanes.keys():
                if self.frame_number>=1 and self.swimlanes[class_name][self.frame_number-1] == 1:
                    self.swimlanes[class_name][self.frame_number] = 1
            # use class names from previously strided frames
            current_classes = self.previous_classes
        
        # Render legend image
        legend_text_buffer = int(self.config_value("legend_text_buffer"))
        legend_image = self._create_legend(self.legend_width, self.legend_height,
                                            legend_text_buffer, current_classes)

        # Render swimlane image
        swimlane_image = self._create_swimlane(self.swimlane_width, self.swimlane_height, 
                                    int(self.config_value("swimlane_text_buffer")),
                                    current_classes, 
                                    int(self.config_value("num_swimlane_cells")))

        image = cv2.resize(image, (self.image_width, self.image_height))
        output_image[:self.image_height, :self.image_width, :] = image
        output_image[:self.image_height, \
                self.image_width:self.image_width + self.legend_width, :] = legend_image
        output_image[self.image_height:, :, :] = swimlane_image
        
        # Pass the image to the viewer
	if (self.lock.acquire(False)):
	    pil_image = Image.fromarray(output_image)
	    vital_image = VitalPIL.from_pil(pil_image)
	    image_container = ImageContainer(vital_image)
	    self.push_to_port_using_trait('image', image_container)
	    self.lock.release()
        self.frame_number += 1
		
        
        
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.VisualizeProcess'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('VisualizeProcess', 
                                'Visualize activities', 
                                VisualizeProcess)

    process_factory.mark_process_module_as_loaded(module_name)
