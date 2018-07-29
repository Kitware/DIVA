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
#include "diva_input.h"

namespace py = pybind11;

void diva_python_input(py::module &m)
{
  py::enum_<diva_input::type>(m, "input_type")
    .value("none", diva_input::type::none)
    .value("image_list", diva_input::type::image_list)
    .value("video_file", diva_input::type::video_file)
    .value("rstp", diva_input::type::rstp)
    .export_values();

  py::class_<diva_input, std::shared_ptr<diva_input>>(m, "input")
    .def(py::init<>())
    .def("clear", &diva_input::clear)
    .def("is_valid", &diva_input::is_valid)
    .def("has_dataset_id", &diva_input::has_dataset_id)
    .def("set_dataset_id", &diva_input::set_dataset_id)
    .def("get_dataset_id", &diva_input::get_dataset_id)
    .def("remove_dataset_id", &diva_input::remove_dataset_id)
    .def("has_frame_rate_Hz", &diva_input::has_frame_rate_Hz)
    .def("set_frame_rate_Hz", &diva_input::set_frame_rate_Hz)
    .def("get_frame_rate_Hz", &diva_input::get_frame_rate_Hz)
    .def("remove_frame_rate_Hz", &diva_input::remove_frame_rate_Hz)
    .def("has_source", &diva_input::has_source)
    .def("get_source", &diva_input::get_source)
    .def("get_image_list_file", &diva_input::get_image_list_file)
    .def("get_image_list_source_dir", &diva_input::get_image_list_source_dir)
    .def("set_image_list_source", &diva_input::set_image_list_source)
    .def("get_video_file_source", &diva_input::get_video_file_source)
    .def("get_video_file_source_dir", &diva_input::get_video_file_source_dir)
    .def("set_video_file_source", &diva_input::set_video_file_source)
    .def("set_rstp_source", &diva_input::set_rstp_source)
    .def("get_rstp_source", &diva_input::get_rstp_source)
    .def("has_next_frame", &diva_input::has_next_frame)
    .def("get_next_frame", &diva_input::get_next_frame);
}
