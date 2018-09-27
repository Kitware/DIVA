"""
Minimal eg to test detset
@author: Ameya Shringi
Kwiver process that makes dummy detected object set
"""


# kwiver/sprokit imports
from sprokit.pipeline import process
from kwiver.kwiver_process import KwiverProcess
from vital.types import DetectedObjectSet, BoundingBox, DetectedObject, DetectedObjectType

def dummy_func(image):
    print image.shape
    return image

class DetectedSetSenderProcess(KwiverProcess):
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        self.add_config_trait("experiment_file_name", "experiment_file_name",
                            '.', 'experiment configuration')
        self.declare_config_using_trait('experiment_file_name')
        required = process.PortFlags()
        required.add(self.flag_required)
        self.declare_input_port_using_trait('image', required)
        self.declare_output_port_using_trait('detected_object_set', process.PortFlags())
        self.declare_input_port_using_trait('timestamp', required )

    def _configure(self):
        pass

    def _step(self):
        ts = self.grab_input_using_trait('timestamp')
        in_img_c = self.grab_input_using_trait('image')
        dummy_func(in_img_c.image().asarray())
        det_set = DetectedObjectSet()
        box = BoundingBox(0, 0, 0, 0)
        dot = DetectedObjectType(["Opening"], [1.0])
        print dot.all_class_names()
        det_set.add(DetectedObject(box, 0.0, dot))

        self.push_to_port_using_trait('detected_object_set', det_set)

def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.DetsetSenderProcesss'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('DetsetSenderProcess', 
                                'Pass dummy detection set over a pipeline',
                                DetectedSetSenderProcess)

    process_factory.mark_process_module_as_loaded(module_name)
