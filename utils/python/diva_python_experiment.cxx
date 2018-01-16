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
  py::enum_<diva_experiment::type>(m, "type")
    .value("object_detection", diva_experiment::type::object_detection)
    .value("activity_detection", diva_experiment::type::activity_detection)
    .export_values();

  py::enum_<diva_experiment::input_type>(m, "input_type")
    .value("file_list", diva_experiment::input_type::file_list)
    .value("video", diva_experiment::input_type::video)
    .export_values();

  py::enum_<diva_experiment::transport_type>(m, "transport_type")
    .value("disk", diva_experiment::transport_type::disk)
    .value("girder", diva_experiment::transport_type::girder)
    .value("rstp", diva_experiment::transport_type::rstp)
    .export_values();

  py::enum_<diva_experiment::output_type>(m, "output_type")
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
    .def("has_input_type", &diva_experiment::has_input_type)
    .def("get_input_type", &diva_experiment::get_input_type)
    .def("set_input_type", &diva_experiment::set_input_type)
    .def("remove_input_type", &diva_experiment::remove_input_type)
    .def("has_transport_type", &diva_experiment::has_transport_type)
    .def("get_transport_type", &diva_experiment::get_transport_type)
    .def("set_transport_type", &diva_experiment::set_transport_type)
    .def("remove_transport_type", &diva_experiment::remove_transport_type)
    .def("has_dataset_id", &diva_experiment::has_dataset_id)
    .def("set_dataset_id", &diva_experiment::set_dataset_id)
    .def("get_dataset_id", &diva_experiment::get_dataset_id)
    .def("remove_dataset_id", &diva_experiment::remove_dataset_id)
    .def("has_input_source", &diva_experiment::has_input_source)
    .def("set_input_source", &diva_experiment::set_input_source)
    .def("get_input_source", &diva_experiment::get_input_source)
    .def("remove_input_source", &diva_experiment::remove_input_source)
    .def("has_input_root_dir", &diva_experiment::has_input_root_dir)
    .def("set_input_root_dir", &diva_experiment::set_input_root_dir)
    .def("get_input_root_dir", &diva_experiment::get_input_root_dir)
    .def("remove_input_root_dir", &diva_experiment::remove_input_root_dir)
    .def("has_frame_rate_Hz", &diva_experiment::has_frame_rate_Hz)
    .def("set_frame_rate_Hz", &diva_experiment::set_frame_rate_Hz)
    .def("get_frame_rate_Hz", &diva_experiment::get_frame_rate_Hz)
    .def("remove_frame_rate_Hz", &diva_experiment::remove_frame_rate_Hz)
    .def("has_output_type", &diva_experiment::has_output_type)
    .def("get_output_type", &diva_experiment::get_output_type)
    .def("set_output_type", &diva_experiment::set_output_type)
    .def("remove_output_type", &diva_experiment::remove_output_type)
    .def("has_output_root_dir", &diva_experiment::has_output_root_dir)
    .def("set_output_root_dir", &diva_experiment::set_output_root_dir)
    .def("get_output_root_dir", &diva_experiment::get_output_root_dir)
    .def("remove_output_root_dir", &diva_experiment::remove_output_root_dir)
    .def("get_output_filename", &diva_experiment::get_output_prefix)
    .def("set_algorithm_parameter", &diva_experiment::set_algorithm_parameter)
    .def("get_algorithm_parameter", &diva_experiment::get_algorithm_parameter)
    ;
}
