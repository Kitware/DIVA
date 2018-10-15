# -*- coding: utf-8 -*-
"""
Kwiver process to test image reader

@author: Ameya Shringi
"""

#kwiver/sprokit import
from sprokit.pipeline import process, datum
from kwiver.kwiver_process import KwiverProcess

from PIL import Image

import threading
import os
import cv2
import numpy as np



class TestReader(KwiverProcess):
    """
    This process takes the detected object sets and show them on the image
    """
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        # set up required flags
        required = process.PortFlags()
        required.add(self.flag_required)
        self.declare_input_port_using_trait("object_track_set", required)

    def _configure(self):
        pass

    def _step(self):
        # Read detected object set, image and timestamp
        self.grab_input_using_trait('object_track_set')
        pass
		
        
        
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.TestReader'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('TestReader', 
                                'test image reader for ACT', 
                                TestReader)

    process_factory.mark_process_module_as_loaded(module_name)
