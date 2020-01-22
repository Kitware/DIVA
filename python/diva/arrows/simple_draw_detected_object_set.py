# ckwg +29
# Copyright 2020 by Kitware, Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#  * Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
#  * Neither name of Kitware, Inc. nor the names of any contributors may be used
#    to endorse or promote products derived from this software without specific
#    prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS ``AS IS''
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from __future__ import print_function

from kwiver.vital.algo import DrawDetectedObjectSet
from kwiver.vital.types import DetectedObjectSet, DetectedObject, BoundingBox
from kwiver.vital.types import ImageContainer

import cv2
import math

SUPPORTED_BBOX_SHAPE = ["rectangle", "circle"]

class SimpleDrawDetectedObjectSet(DrawDetectedObjectSet):
    """
    Implementation of DrawDetectedObjectSet that creates a bounding box around
    the every object in the detected object set
    """

    def __init__(self):
        DrawDetectedObjectSet.__init__(self)
        self.bbox_thickness = 5
        self.bbox_color = (255, 0, 0)
        self.font_scale = 0.6
        self.font_thickness = 2
        self.bbox_shape = "rectangle"
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def get_configuration(self):
        cfg = super(DrawDetectedObjectSet, self).get_configuration()
        cfg.set_value( "bbox_thickness", str(self.bbox_thickness))
        cfg.set_value( "bbox_color", "{0};{1};{2}".format(self.bbox_color[0],
                                                          self.bbox_color[1],
                                                          self.bbox_color[2]) )
        cfg.set_value( "font_scale", str(self.font_scale))
        cfg.set_value( "font_thickness", str(self.font_thickness))
        cfg.set_value( "bbox_shape", str(self.bbox_shape))
        return cfg

    def set_configuration( self, cfg_in ):
        cfg = self.get_configuration()
        cfg.merge_config(cfg_in)
        self.bbox_thickness = int(cfg.get_value( "bbox_thickness" ))
        self.bbox_color = tuple(map(int, cfg.get_value("bbox_color").split(";")))
        assert len(self.bbox_color)==3, "Invalid color specification"
        #RGB spec to bgr spec
        self.bbox_color = self.bbox_color[::-1]
        self.font_scale = float(cfg.get_value("font_scale"))
        self.font_thickness = int(cfg.get_value("font_thickness"))
        self.bbox_shape = cfg.get_value("bbox_shape")
        assert self.bbox_shape in SUPPORTED_BBOX_SHAPE, \
                "Unsupported bounding box shape specified"

    def check_configuration( self, cfg):
        return True

    def draw(self, detected_object_set, image):
        u_image = cv2.cvtColor(image.asarray(), cv2.COLOR_RGB2BGR)
        for detected_object in detected_object_set:
            bbox = detected_object.bounding_box()
            confidence = detected_object.confidence()
            if self.bbox_shape == "rectangle":
                u_image = cv2.rectangle(u_image,
                              (int(bbox.min_x()), int(bbox.min_y())),
                              (int(bbox.max_x()), int(bbox.max_y())),
                              self.bbox_color,
                              self.bbox_thickness)
                text_origin = (int(bbox.min_x()),int(bbox.min_y()-self.bbox_thickness))
            else:
                center = ((int(bbox.min_x()) + int(bbox.max_x()))//2,
                          (int(bbox.min_y()) + int(bbox.max_y()))//2)
                radius = int(math.sqrt(math.pow(float(bbox.max_y()) - \
                                                float(bbox.min_y()), 2) + \
                                       math.pow(float(bbox.max_x()) - \
                                                float(bbox.min_x()), 2)))
                u_image = cv2.circle(u_image, center, radius, self.bbox_color,
                                     self.bbox_thickness)
                text_origin = (center[0]-radius, center[1]-radius-self.bbox_thickness)

            types = detected_object.type()
            if types is None:
                label = "{0}".format(confidence)
            else:
                label = "{0}: {1}".format(types.get_most_likely_class(),
                                          types.get_most_likely_score())
            u_image = cv2.putText(u_image,
                        label,
                        text_origin,
                        self.font, self.font_scale, self.bbox_color, self.font_thickness)
        u_image = cv2.cvtColor(u_image, cv2.COLOR_BGR2RGB)
        image_container = ImageContainer.fromarray(u_image)
        return image_container

def __vital_algorithm_register__():
    from kwiver.vital.algo import algorithm_factory
    # Register Algorithm
    implementation_name  = "SimpleDrawDetectedObjectSet"
    if algorithm_factory.has_algorithm_impl_name(
                                SimpleDrawDetectedObjectSet.static_type_name(),
                                implementation_name):
        return
    algorithm_factory.add_algorithm( implementation_name,
        "creates a bounding box around the every object in the detected object set",
         SimpleDrawDetectedObjectSet )
    algorithm_factory.mark_algorithm_as_loaded( implementation_name )
