/*ckwg +29
* Copyright 2017 by Kitware, Inc.
* All rights reserved.
*
* Redistribution and use in source and binary forms, with or without
* modification, are permitted provided that the following conditions are met:
*
*  * Redistributions of source code must retain the above copyright notice,
*    this list of conditions and the following disclaimer.
*
*  * Redistributions in binary form must reproduce the above copyright notice,
*    this list of conditions and the following disclaimer in the documentation
*    and/or other materials provided with the distribution.
*
*  * Neither name of Kitware, Inc. nor the names of any contributors may be used
*    to endorse or promote products derived from this software without specific
*    prior written permission.
*
* THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
* IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
* ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHORS OR CONTRIBUTORS BE LIABLE FOR
* ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
* DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
* SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
* CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
* OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
* OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

#include <pybind11/pybind11.h>
#include <pybind11/stl_bind.h>
#include "diva_geometry.h"

namespace py = pybind11;

using PolygonVector = std::vector<std::pair<size_t, size_t>>;
using ClassificationMap = std::map<std::string, double>;
PYBIND11_MAKE_OPAQUE(PolygonVector);
PYBIND11_MAKE_OPAQUE(ClassificationMap);

void diva_python_geometry(py::module &m)
{
  //py::bind_vector<std::vector<std::pair<size_t, size_t>>>(m, "PolygonVector");
  py::class_<PolygonVector>(m, "PolygonVector")
    .def(py::init<>())
    .def("back", (std::pair<size_t, size_t> &(PolygonVector::*)()) &PolygonVector::back)
    .def("__len__", [](const PolygonVector &v) { return v.size(); })
    .def("__iter__", [](PolygonVector &v) {
    return py::make_iterator(v.begin(), v.end());
  }, py::keep_alive<0, 1>());

  //py::bind_map<std::map<std::string, double>>(m, "ClassificationMap");
  py::class_<ClassificationMap>(m, "ClassificationMap")
    .def(py::init<>())
    .def("__len__", [](const ClassificationMap &v) { return v.size(); })
    .def("__iter__", [](ClassificationMap &v) {
    return py::make_iterator(v.begin(), v.end());
  }, py::keep_alive<0, 1>());

  py::class_<diva_geometry::bounding_box_pixels>(m, "bounding_box")
    .def(py::init<>())
    .def("get_x1", &diva_geometry::bounding_box_pixels::get_x1)
    .def("get_y1", &diva_geometry::bounding_box_pixels::get_y1)
    .def("get_x2", &diva_geometry::bounding_box_pixels::get_x2)
    .def("get_y2", &diva_geometry::bounding_box_pixels::get_y2);

  py::enum_<diva_geometry::source>(m, "geometry_source")
    .value("truth", diva_geometry::source::truth)
    .export_values();

  py::enum_<diva_geometry::evaluation>(m, "geometry_evaluation")
    .value("true_positive", diva_geometry::evaluation::true_positive)
    .value("false_positive", diva_geometry::evaluation::false_positive)
    .value("false_alarm", diva_geometry::evaluation::false_alarm)
    .export_values();

  py::enum_<diva_geometry::keyframe>(m, "geometry_keyframe")
    .value("yes", diva_geometry::keyframe::yes)
    .value("no", diva_geometry::keyframe::no)
    .export_values();

  py::enum_<diva_geometry::occlusion>(m, "geometry_occlusion")
    .value("partially", diva_geometry::occlusion::partially)
    .value("mostly", diva_geometry::occlusion::mostly)
    .export_values();

  py::class_<diva_geometry>(m, "geometry")
    .def(py::init<>())
    .def("clear", &diva_geometry::clear)
    .def("is_valid", &diva_geometry::is_valid)
    .def("has_detection_id", &diva_geometry::has_detection_id)
    .def("get_detection_id", &diva_geometry::get_detection_id)
    .def("set_detection_id", &diva_geometry::set_detection_id)
    .def("remove_detection_id", &diva_geometry::remove_detection_id)
    .def("has_track_id", &diva_geometry::has_track_id)
    .def("get_track_id", &diva_geometry::get_track_id)
    .def("set_track_id", &diva_geometry::set_track_id)
    .def("remove_track_id", &diva_geometry::remove_track_id)
    .def("has_frame_id", &diva_geometry::has_frame_id)
    .def("get_frame_id", &diva_geometry::get_frame_id)
    .def("set_frame_id", &diva_geometry::set_frame_id)
    .def("remove_frame_id", &diva_geometry::remove_frame_id)
    .def("has_frame_time", &diva_geometry::has_frame_time)
    .def("get_frame_time", &diva_geometry::get_frame_time)
    .def("set_frame_time", &diva_geometry::set_frame_time)
    .def("remove_frame_time", &diva_geometry::remove_frame_time)
    .def("has_frame_absolute_time", &diva_geometry::has_frame_absolute_time)
    .def("get_frame_absolute_time", &diva_geometry::get_frame_absolute_time)
    .def("set_frame_absolute_time", &diva_geometry::set_frame_absolute_time)
    .def("remove_frame_absolute_time", &diva_geometry::remove_frame_absolute_time)
    .def("has_confidence", &diva_geometry::has_confidence)
    .def("get_confidence", &diva_geometry::get_confidence)
    .def("set_confidence", &diva_geometry::set_confidence)
    .def("remove_confidence", &diva_geometry::remove_confidence)
    .def("has_bounding_box_pixels", &diva_geometry::has_bounding_box_pixels)
    .def("get_bounding_box_pixels", &diva_geometry::get_bounding_box_pixels)
    .def("set_bounding_box_pixels", &diva_geometry::set_bounding_box_pixels)
    .def("remove_bounding_box_pixels", &diva_geometry::remove_bounding_box_pixels)
    .def("has_source", &diva_geometry::has_source)
    .def("get_source", &diva_geometry::get_source)
    .def("set_source", &diva_geometry::set_source)
    .def("remove_source", &diva_geometry::remove_source)
    .def("has_evaluation", &diva_geometry::has_evaluation)
    .def("get_evaluation", &diva_geometry::get_evaluation)
    .def("set_evaluation", &diva_geometry::set_evaluation)
    .def("remove_evaluation", &diva_geometry::remove_evaluation)
    .def("has_occlusion", &diva_geometry::has_occlusion)
    .def("get_occlusion", &diva_geometry::get_occlusion)
    .def("set_occlusion", &diva_geometry::set_occlusion)
    .def("remove_occlusion", &diva_geometry::remove_occlusion)
    .def("has_keyframe", &diva_geometry::has_keyframe)
    .def("get_keyframe", &diva_geometry::get_keyframe)
    .def("set_keyframe", &diva_geometry::set_keyframe)
    .def("remove_keyframe", &diva_geometry::remove_keyframe)
    .def("has_classification", &diva_geometry::has_classification)
    .def("get_classification", (std::map<std::string, double>&(diva_geometry::*)())&diva_geometry::get_classification)
    .def("add_classification", &diva_geometry::add_classification)
    .def("remove_classification", &diva_geometry::remove_classification)
    .def("has_polygon", &diva_geometry::has_polygon)
    .def("add_polygon_point", &diva_geometry::add_polygon_point)
    .def("get_polygon", (std::vector<std::pair<size_t, size_t>>&(diva_geometry::*)()) &diva_geometry::get_polygon)
    .def("remove_polygon", &diva_geometry::remove_polygon)

    .def("to_string", &diva_geometry::to_string)
    .def("from_string", &diva_geometry::from_string);
}