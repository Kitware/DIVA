# -*- coding: utf-8 -*-
"""
Kwiver process to receive Detected Object Set

@author: Ameya Shringi
"""

#kwiver/sprokit import
from sprokit.pipeline import process, datum
from kwiver.kwiver_process import KwiverProcess
from vital.types import DetectedObjectSet, BoundingBox, DetectedObject, DetectedObjectType

class DetectedSetReceiveProcess(KwiverProcess):
    
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        required = process.PortFlags()
        required.add(self.flag_required)
        self.declare_input_port_using_trait("detected_object_set", required)
        self.declare_input_port_using_trait('timestamp', required )

    def _configure(self):
        pass

    def _step(self):
        detected_object_set = self.grab_input_using_trait('detected_object_set')
        ts = self.grab_input_using_trait('timestamp')
        if len(detected_object_set) > 0:
            for i in range(len(detected_object_set)):
                print "Detected set: " + str(detected_object_set[i].type().all_class_names())


def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.DetsetReceiverProcess'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('DetsetReceiverProcess', 
                                'Receive dummy detection set over a pipeline', 
                                DetectedSetReceiveProcess)

    process_factory.mark_process_module_as_loaded(module_name)
