# -*- coding: utf-8 -*-
"""
Kwiver process to render ``detected_object_set`` from RC3D on the input image and
show temporal history of detections using swimlanes

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

class RC3DVisualizer(KwiverProcess):
    """
    Render ``detected_object_set`` from RC3D on image and show temporal history 
    of detections using swimlanes

    * Input Ports:
        * ``detected_object_set`` Detected object set obtained from RC3D (Required)
        * ``timestamp`` timestamp associated with the input from which the detected object set was obtained from (Required)
        * ``image`` RGB image obtained from input source (Required)

    * Output Ports:
        * ``image`` RGB image with activity detections and swimlane

    * Configuration:
        * ``experiment_file_name`` Experiment configuration used by RC3D (Eg. `experiment.yml`_)
        * ``stride`` Temporal stride for RC3D (default=8)
        * Legend Configuration Parameters: Configuration parameters associated iwith legend
            * ``legend_text_height`` Height of the legend text (default=10)
            * ``legend_text_width`` Width of the legend text (default=40)
            * ``legend_text_buffer`` Space between legend text (default=4)
            * ``legend_font_scale`` Scale of the font used in legend (default=0.8)
        * Swimlane Configuration Parameters: Configuration parameters associated with swimlane
            * ``swimlane_text_height`` Height of the swimlane text (default=15)
            * ``swimlane_text_width`` Width of the swimlane text (default=40)
            * ``swimlane_text_buffer`` Space between the text in swimlane (default=2)
            * ``swimlane_text_font_scale`` Scale of the fonts used in swimlane (default=0.5) 
        * ``image_width`` Width of rendering area (default=1920)
        * ``image_height`` Height of the rendering area (default=1080)
        * ``confidence_threshold`` Lower bound on confidence to render an activiy (default=0.2)

    .. Repo links:
    .. _experiment.yml: https://gitlab.kitware.com/kwiver/R-C3D/tree/master/experiments/virat/experiment.yml
    """
    def __init__(self, conf):
        """
        Constructor for RC3D visualizer
        :param conf: Process configuration
        :return: None
        """
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
                                "0.02", "lower bound of confidence")
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
        """
        Helper function to determine upper bound of text width associated with the 
        classes based on the font scale
        :param classes: Dictionary with class names as values
        :param font scale: font scale used by opencv
        :return Upperbound of text width for rendering all classes
        """
        text_size, _ = cv2.getTextSize(classes[0], self.font, font_scale, 1)
        largest_width = text_size[0]
        for value_index, value in enumerate(self.classes.values()):
            text_size, _ = cv2.getTextSize(value, self.font, font_scale, 1)
            if text_size[0] > largest_width:
                largest_width = text_size[0]
        return largest_width

    def _configure(self):
        """
        Configure RC3D visualizer
        """
        expcfg_from_file(self.config_value('experiment_file_name'))
        if experiment_config.json:
            self.classes = generate_classes_from_json(experiment_config.class_index)
        else:
            self.classes = generate_classes(experiment_config.class_index)
        
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
        self.previous_frame = 0


    def _create_legend(self, legend_width, legend_height, legend_buffer, classes):
        """
        Helper function to render legend on an image with all the class names
        :param legend_width: Width of the legend
        :param legend_height: Height of the legend
        :param legend_buffer: Space between text of the legend
        :param classes: Dictionary with class names as values
        :return An image with all class names rendered vertically
        """
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
        """
        Helper function to render swimlane with every class being represented as 
        a single row
        :param swimlane_width: Width of the swimlane
        :param swimlane_height: Height of the swimlane
        :param swimlane_buffer: Space between text of the swimlane
        :param classes: Dictionary with class names as values
        :param num_swimlane_cells: Number of cells in the swimlane 
        :return An image with swimlane
        """
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
        """
        Step function for the visualizer
        """
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
            while len(self.swimlanes[class_name]) <= ts.get_frame():
                if self.previous_frame == 0:
                    self.swimlanes[class_name].append(0)
                else:
                    self.swimlanes[class_name].append(0)

        if (self.lock.acquire()):
            current_classes = []
            print "Frame: " + str(ts.get_frame())
            # RC3D operates only on strided frames
            if int(ts.get_frame())%int(self.config_value("stride")) == 0:
                if len(detected_object_set) > 0:
                    for i in range(len(detected_object_set)):
                        object_type = detected_object_set[i].type()
                        if len(object_type.class_names(
                                float(self.config_value("confidence_threshold")))) > 0:
                            # Get class name on the current frame
                            for class_name in object_type.class_names(
                                        float(self.config_value("confidence_threshold"))):
                                self.swimlanes[class_name][ts.get_frame()] = 1
                                if class_name not in current_classes:
                                    current_classes.append(class_name)
                self.previous_classes = copy.deepcopy(current_classes)
            else:
                for class_name in self.swimlanes.keys():
                    for frame in range(self.previous_frame+1, ts.get_frame()+1):
                        if ts.get_frame()>=1 and self.swimlanes[class_name][self.previous_frame] == 1:
                            self.swimlanes[class_name][frame] = 1
                        else:
                            self.swimlanes[class_name][frame] = 0
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
            pil_image = Image.fromarray(output_image)
            vital_image = VitalPIL.from_pil(pil_image)
            image_container = ImageContainer(vital_image)
            self.push_to_port_using_trait('image', image_container)
            self.lock.release()
        self.previous_frame = ts.get_frame()
        self.frame_number += 1
		
        
        
def __sprokit_register__():
    """
    Sprokit registration for the process
    """
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.RC3DVisualizer'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('RC3DVisualizer', 
                                'Visualize detected_object_set from RC3D', 
                                RC3DVisualizer)

    process_factory.mark_process_module_as_loaded(module_name)
