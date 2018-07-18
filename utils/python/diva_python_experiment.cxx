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
#include "diva_experiment.h"

namespace py = pybind11;

void diva_python_experiment(py::module &m)
{
  py::enum_<diva_experiment::type>(m, "experiment_type")
    .value("object_detection", diva_experiment::type::object_detection)
    .value("activity_detection", diva_experiment::type::activity_detection)
    .export_values();

  py::enum_<diva_experiment::output_type>(m, "experiment_output_type")
    .value("file", diva_experiment::output_type::file)
    .export_values();

  py::class_<diva_experiment>(m, "experiment")
    .def(py::init<>())
    .def("clear", &diva_experiment::clear)
    .def("is_valid", &diva_experiment::is_valid)
    .def("read_experiment", &diva_experiment::read_experiment)
    .def("write_experiment", &diva_experiment::write_experiment)
    .def("has_type", &diva_experiment::has_type)
    .def("get_type", &diva_experiment::get_type)
    .def("set_type", &diva_experiment::set_type)
    .def("remove_type", &diva_experiment::remove_type)
    .def("has_input", &diva_experiment::has_input)
    .def("get_input", (diva_input&(diva_experiment::*)())&diva_experiment::get_input)
    .def("has_output_type", &diva_experiment::has_output_type)
    .def("get_output_type", &diva_experiment::get_output_type)
    .def("set_output_type", &diva_experiment::set_output_type)
    .def("remove_output_type", &diva_experiment::remove_output_type)
    .def("has_output_root_dir", &diva_experiment::has_output_root_dir)
    .def("set_output_root_dir", &diva_experiment::set_output_root_dir)
    .def("get_output_root_dir", &diva_experiment::get_output_root_dir)
    .def("remove_output_root_dir", &diva_experiment::remove_output_root_dir)
    .def("get_output_filename", &diva_experiment::get_output_prefix)
    .def("has_scoring_reference_geometry", &diva_experiment::has_scoring_reference_geometry)
    .def("set_scoring_reference_geometry", &diva_experiment::set_scoring_reference_geometry)
    .def("get_scoring_reference_geometry", &diva_experiment::get_scoring_reference_geometry)
    .def("remove_scoring_reference_geometry", &diva_experiment::remove_scoring_reference_geometry)
    .def("has_scoring_evaluation_output_dir", &diva_experiment::has_scoring_evaluation_output_dir)
    .def("set_scoring_evaluation_output_dir", &diva_experiment::set_scoring_evaluation_output_dir)
    .def("get_scoring_evaluation_output_dir", &diva_experiment::get_scoring_evaluation_output_dir)
    .def("remove_scoring_evaluation_output_dir", &diva_experiment::remove_scoring_evaluation_output_dir)
    .def("has_scoring_object_detection_reference_types", &diva_experiment::has_scoring_object_detection_reference_types)
    .def("set_scoring_object_detection_reference_types", &diva_experiment::set_scoring_object_detection_reference_types)
    .def("get_scoring_object_detection_reference_types", &diva_experiment::get_scoring_object_detection_reference_types)
    .def("remove_scoring_object_detection_reference_types", &diva_experiment::remove_scoring_object_detection_reference_types)
    .def("has_scoring_object_detection_target", &diva_experiment::has_scoring_object_detection_target)
    .def("set_scoring_object_detection_target", &diva_experiment::set_scoring_object_detection_target)
    .def("get_scoring_object_detection_target", &diva_experiment::get_scoring_object_detection_target)
    .def("remove_scoring_object_detection_target", &diva_experiment::remove_scoring_object_detection_target)
    .def("has_score_events_executable", &diva_experiment::has_score_events_executable)
    .def("set_score_events_executable", &diva_experiment::set_score_events_executable)
    .def("get_score_events_executable", &diva_experiment::get_score_events_executable)
    .def("remove_score_events_executable", &diva_experiment::remove_score_events_executable)
    .def("has_scoring_object_detection_iou", &diva_experiment::has_scoring_object_detection_iou)
    .def("set_scoring_object_detection_iou", &diva_experiment::set_scoring_object_detection_iou)
    .def("get_scoring_object_detection_iou", &diva_experiment::get_scoring_object_detection_iou)
    .def("remove_scoring_object_detection_iou", &diva_experiment::remove_scoring_object_detection_iou)
    .def("has_scoring_object_detection_time_window", &diva_experiment::has_scoring_object_detection_time_window)
    .def("set_scoring_object_detection_time_window", &diva_experiment::set_scoring_object_detection_time_window)
    .def("get_scoring_object_detection_time_window", &diva_experiment::get_scoring_object_detection_time_window)
    .def("remove_scoring_object_detection_time_window", &diva_experiment::remove_scoring_object_detection_time_window)
    .def("has_algorithm_executable", &diva_experiment::has_algorithm_executable)
    .def("set_algorithm_executable", &diva_experiment::set_algorithm_executable)
    .def("get_algorithm_executable", &diva_experiment::get_algorithm_executable)
    .def("remove_algorithm_executable", &diva_experiment::remove_algorithm_executable)
    .def("set_algorithm_parameter", &diva_experiment::set_algorithm_parameter)
    .def("get_algorithm_parameter", &diva_experiment::get_algorithm_parameter)

      .def("to_string", &diva_experiment::to_string);
    ;
}
