# -*- coding: utf-8 -*-
"""
Kwiver process to visualize activities on an image 

@author: Ameya Shringi
"""

#kwiver/sprokit import
from sprokit.pipeline import process, datum
from kwiver.kwiver_process import KwiverProcess
from vital.types import ImageContainer
from vital.util import VitalPIL

from PIL import Image

import os
import cv2
import numpy as np



class VisualizeProcess(KwiverProcess):
    """
    This process takes the detected object sets and show them on the image
    """
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("stride", "stride", "8", 
                                "temporal stride of the model")
        self.declare_config_using_trait("stride")
        self.add_config_trait("text_height", "text_height", "40", 
                                "height of the text")
        self.declare_config_using_trait("text_height")
        self.add_config_trait("text_width", "text_width", "90", 
                                "width of the text")
        self.declare_config_using_trait("text_width")
        # set up required flags
        required = process.PortFlags()
        required.add(self.flag_required)
        self.declare_input_port_using_trait("image", required)
        self.declare_input_port_using_trait("detected_object_set", required)
        self.declare_input_port_using_trait("timestamp", required)

        self.declare_output_port_using_trait('image', process.PortFlags())


    def _configure(self):
        self.previous_classes = []

    def _step(self):
        # Read detected object set, image and timestamp
        detected_object_set = self.grab_input_using_trait('detected_object_set')
        ts = self.grab_input_using_trait('timestamp')
        image_container = self.grab_input_using_trait('image')
        image = image_container.image().asarray().astype(np.uint8)
        # Get text attributes
        text_width = int(self.config_value("text_width")) 
        text_height = int(self.config_value("text_height"))
        font = cv2.FONT_HERSHEY_SIMPLEX

        current_classes = []
        # RC3D operates only on strided frames
        if int(ts.get_frame())%int(self.config_value("stride")) == 0:
            if len(detected_object_set) > 0:
                for i in range(len(detected_object_set)):
                    object_type = detected_object_set[i].type()
                    if len(object_type.class_names(0.0)) > 0:
                        # Get class name on the current frame
                        for class_name in object_type.class_names(0.0):
                            if class_name not in current_classes:
                                current_classes.append(class_name)
        else:
            # use class names from previously strided frames
            current_classes = self.previous_classes

        output_image = np.ascontiguousarray(image, dtype=np.uint8)
        # Render class names on the  image
        if len(current_classes) > 0:
            # Check if some text is larger then text width and height
            # if so adjust the text width and height
            for current_class in current_classes:
                text_size, _ = cv2.getTextSize(current_class, font, 1, 4)
                width, height = text_size
                if width > text_width:
                    text_width = width + 5
                if height > text_height:
                    text_height = height + 10

            # Write text on the image
            for class_index, current_class in enumerate(current_classes):
                
                cv2.putText(output_image, str(current_class), (image.shape[1]-text_width,
                            text_height*(class_index+1)), font, 1, 
                            (255, 0, 0), 4)
        
        # Pass the image to the viewer
        self.previous_classes = current_classes
        pil_image = Image.fromarray(output_image)
        vital_image = VitalPIL.from_pil(pil_image)
        image_container = ImageContainer(vital_image)
        self.push_to_port_using_trait('image', image_container)
        
        
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.VisualizeProcess'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('VisualizeProcess', 
                                'Visualize activities', 
                                VisualizeProcess)

    process_factory.mark_process_module_as_loaded(module_name)
