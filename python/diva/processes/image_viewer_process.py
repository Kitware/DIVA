from kwiver.vital.types import ImageContainer

import cv2
import time
from kwiver.sprokit.processes.kwiver_process import KwiverProcess
from kwiver.sprokit.pipeline import process, DatumType

class ImageViewerProcess(KwiverProcess):
    def __init__(self, config):
        KwiverProcess.__init__(self, config)
        self.add_config_trait("pause_time", "pause_time", "1",
                              "Time between pauses(in ms)")
        self.declare_config_using_trait("pause_time")

        self.add_config_trait("title", "title", "Test",
                              "Title of the window")
        self.declare_config_using_trait("title")

        optional = process.PortFlags()
        self.declare_input_port_using_trait("image", optional)

    def _configure(self):
        pass

    def _step(self):
        image_container = self.grab_input_using_trait("image")
        cv2.imshow(self.config_value("title"),
                   cv2.cvtColor(image_container.asarray(), cv2.COLOR_RGB2BGR))
        cv2.waitKey(int(self.config_value("pause_time")))
        time.sleep(float(self.config_value("pause_time"))/1000.)

    def _reset(self):
        cv2.destroyAllWindows()


def __sprokit_register__():
    from kwiver.sprokit.pipeline import process_factory
    module_name = 'python:kwiver.visualize'
    if process_factory.is_process_module_loaded(module_name):
        return
    process_factory.add_process('ImageViewer',
                                'Visualize images using opencv',
                                ImageViewerProcess)
