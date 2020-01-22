from kwiver.sprokit.processes.kwiver_process import KwiverProcess
from kwiver.sprokit.pipeline import process
from kwiver.vital.types import BoundingBox, DetectedObjectType, DetectedObject, DetectedObjectSet

class SimpleDetectorProcess(KwiverProcess):
    def __init__(self, config):
        KwiverProcess.__init__(self, config)
        self.add_config_trait("bbox_width",
                              "bbox_width",
                              "30",
                              "Width of bbox")
        self.declare_config_using_trait("bbox_width")

        self.add_config_trait("bbox_height",
                              "bbox_height",
                              "30",
                              "Height of bbox")
        self.declare_config_using_trait("bbox_height")

        optional = process.PortFlags()
        self.declare_input_port_using_trait("image", optional)
        self.declare_input_port_using_trait("timestamp", optional)
        self.declare_input_port_using_trait("file_name", optional)
        self.declare_output_port_using_trait("detected_object_set", optional)

    def _configure(self):
        pass

    def _step(self):
        image_container = self.grab_input_using_trait("image")
        timestamp = self.grab_input_using_trait("timestamp")
        file_name = self.grab_input_using_trait("file_name")
        image = image_container.asarray()
        h, w, _ = image.shape
        bbox_x = w//2
        bbox_y = h//2
        bbox = BoundingBox( bbox_x - int(self.config_value("bbox_width"))//2,
                            bbox_y - int(self.config_value("bbox_height"))//2,
                            bbox_x + int(self.config_value("bbox_width"))//2,
                            bbox_y + int(self.config_value("bbox_height"))//2 )
        dot = DetectedObjectType("Test", 1.0)
        do = DetectedObject(bbox, 1.0, dot)
        dos = DetectedObjectSet()
        dos.add(do)
        self.push_to_port_using_trait("detected_object_set", dos)

def __sprokit_register__():
    from kwiver.sprokit.pipeline import process_factory

    module_name = 'python:kwiver.simple_detector'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('SimpleDetector',
                                'Simple detector process',
                                SimpleDetectorProcess)
