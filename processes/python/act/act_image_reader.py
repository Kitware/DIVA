# -*- coding: utf-8 -*-
"""
Kwiver process to read rgb and optical flow images 

@author: Ameya Shringi
"""

#kwiver/sprokit import
from sprokit.pipeline import process, datum
from kwiver.kwiver_process import KwiverProcess
from vital.types import ImageContainer, TimeStamp
from vital.util import VitalPIL

from exp_config import experiment_config, expcfg_from_file
from virat_dataset import ViratDataset

import cv2
from PIL import Image
import os

class ACTImageReader(KwiverProcess):
    """
    This process reads an RGB and an optical flow image based on configuration file
    """
    def __init__(self, conf):
        KwiverProcess.__init__(self, conf)
        # Experiment configuration
        self.add_config_trait("exp", "exp", \
                                "experiment.yml",
                                "path to experiment configuration")
        self.declare_config_using_trait('exp')
        required = process.PortFlags()
        required.add(self.flag_required)
        if os.path.exists(self.config_value("exp")):
            expcfg_from_file(self.config_value("exp"))
        self.add_port_trait("rgb_image", "image", "rgb image used by ACT")
        for i in range(experiment_config.test.number_flow):
            self.add_port_trait("flow_image_" + str(i+1), "image", 
                                    "flow image used by ACT")
            self.declare_output_port_using_trait("flow_image_" + str(i+1),
                                        process.PortFlags())
        self.declare_output_port_using_trait("rgb_image", process.PortFlags() )
        self.declare_output_port_using_trait("timestamp", process.PortFlags() )
        #self.declare_output_port_using_trait("video_file_name", process.PortFlags() )


    def _configure(self):
        self.virat_dataset = ViratDataset(experiment_config.data.data_root, 
                                    experiment_config.data.frames_root, 
                                    experiment_config.data.flow_root,
                                    experiment_config.data.train_annotation_dirs,
                                    experiment_config.data.test_annotation_dirs,
                                    experiment_config.data.class_index, 
                                    experiment_config.data.save_directory,
                                    experiment_config.train.kpf_mode,
                                    experiment_config.train.json_mode,
                                    experiment_config.data.save_prefix)
        self.all_videos_list = self.virat_dataset.test_video_list
        self.video_index = 0
        self.frame_index = 0
        
    def _get_image_name(self, image_number):
        return str(image_number).zfill(5) + "." + experiment_config.data.img_extension

    def _step(self):
        if self.frame_index == self.virat_dataset.test_num_frames(
                                    self.all_videos_list[self.video_index]):
            self.video_index += 1
            self.frame_index = 0
            
        if self.video_index == len(self.all_videos_list):
            from sprokit.pipeline import datum
            self.mark_process_as_complete()
            self.push_datum_to_port("rgb_image", datum.complete())
            for i in range(experiment_config.test.number_flow):
                self.push_datum_to_port("flow_image_" + str(i+1), datum.complete())
            self.push_datum_to_port("timestamp", datum.complete())
            
        rgb_image = cv2.imread(self.virat_dataset.imfile(self.
                                    all_videos_list[self.video_index],
                                    self._get_image_name(self.frame_index+1)))
        flow_images = []
        for flow_index in range(experiment_config.test.number_flow):
            flow_images.append(cv2.imread(self.virat_dataset.flowfile(self.
                                    all_videos_list[self.video_index],
                                    self._get_image_name(
                                     min(self.virat_dataset.test_num_frames(
                                        self.all_videos_list[self.video_index]),  
                                        self.frame_index+1+\
                                          flow_index)))))
        rgb_image = cv2.resize(rgb_image, (experiment_config.train.imgsize, 
                                experiment_config.train.imgsize))
        flow_images= [cv2.resize(flow_image, (experiment_config.train.imgsize,
                                experiment_config.train.imgsize))
                                for flow_image in flow_images]
        rgb_image = Image.fromarray(rgb_image)
        rgb_image = VitalPIL.from_pil(rgb_image)
        rgb_container = ImageContainer(rgb_image)
        self.push_to_port_using_trait("rgb_image", rgb_container)
        for i in range(experiment_config.test.number_flow):
            flow_image = Image.fromarray(flow_images[i])
            flow_image = VitalPIL.from_pil(flow_image)
            flow_container = ImageContainer(flow_image)
            self.push_to_port_using_trait("flow_image_" + str(i+1), flow_container)
        self.frame_index += 1
        tstamp = TimeStamp()
        tstamp.set_frame(self.frame_index)
        self.push_to_port_using_trait("timestamp", tstamp)
            
        
def __sprokit_register__():
    from sprokit.pipeline import process_factory

    module_name = 'python:kwiver.ACTImageReader'

    if process_factory.is_process_module_loaded(module_name):
        return

    process_factory.add_process('ACTImageReader', 
                                'Image Reader for ACT', 
                                ACTImageReader)

    process_factory.mark_process_module_as_loaded(module_name)
