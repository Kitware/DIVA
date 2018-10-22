# -*- coding: utf-8 -*-
"""
Kwiver process modify the size of bounding boxes based on image resolution

@author: Ameya Shringi
"""

#kwiver/sprokit import
from sprokit.pipeline import process
from kwiver.kwiver_process import KwiverProcess
from vital.types import BoundingBox, DetectedObjectSet

class ModifyBboxResolution(KwiverProcess):
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("input_image_width", "input_image_width",
                                "512", "Width of input image")
        self.declare_config_using_trait("input_image_width")
        self.add_config_trait("input_image_height", "input_image_height",
                                "512", "Height of input image")
        self.declare_config_using_trait("input_image_height")
        self.add_config_trait("output_image_width", "output_image_width",
                                "1920", "Width of output image")
        self.declare_config_using_trait("output_image_width")
        self.add_config_trait("output_image_height", "output_image_height",
                                "1080", "Height of output image")
        self.declare_config_using_trait("output_image_height")
        
        # set up required flags
        required = process.PortFlags()
        required.add(self.flag_required)
        self.declare_input_port_using_trait("detected_object_set", required)
        self.declare_output_port_using_trait("detected_object_set", process.PortFlags())

    def _configure(self):
        pass

    def _step(self):
        dos = self.grab_input_using_trait('detected_object_set')
        modified_dos = DetectedObjectSet()
        for det_index, detected_object in enumerate(dos):
            bbox = detected_object.bounding_box()
            bbox_center = bbox.center()
            width_ratio = float(self.config_value("output_image_width"))/\
                                float(self.config_value("input_image_width"))
            height_ratio = float(self.config_value("output_image_height"))/\
                                float(self.config_value("input_image_height"))
            scaled_bbox_center = (bbox_center[0]*width_ratio, 
                                    bbox_center[1]*height_ratio)
            scaled_width = bbox.width()*width_ratio
            scaled_height = bbox.height()*height_ratio
            new_xmin = scaled_bbox_center[0]-scaled_width//2
            new_ymin = scaled_bbox_center[1]-scaled_height//2
            new_xmax = scaled_bbox_center[0]+scaled_width//2
            new_ymax = scaled_bbox_center[1]+scaled_height//2
            new_bbox = BoundingBox(new_xmin, new_ymin, new_xmax, new_ymax)
            detected_object.set_bounding_box(new_bbox)
            modified_dos.add(detected_object)
        self.push_to_port_using_trait("detected_object_set", modified_dos)
        
        
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.ModifyBboxResolution'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('ModifyBboxResolution', 
        'Modify bounding box dimension based on input and output image resolution', 
        ModifyBboxResolution)

    process_factory.mark_process_module_as_loaded(module_name)
