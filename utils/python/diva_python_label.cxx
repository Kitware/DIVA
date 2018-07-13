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
#include "diva_label.h"

namespace py = pybind11;

void diva_python_label(py::module &m)
{
  py::class_<diva_label>(m, "label")
    .def(py::init<>())
    .def("clear", &diva_label::clear)
    .def("is_valid", &diva_label::is_valid)
    .def("has_track_id", &diva_label::has_track_id)
    .def("get_track_id", &diva_label::get_track_id)
    .def("set_track_id", &diva_label::set_track_id)
    .def("remove_track_id", &diva_label::remove_track_id)
    .def("has_classification", &diva_label::has_classification)
    .def("get_classification", (std::map<std::string, double>&(diva_label::*)())&diva_label::get_classification)
    .def("get_max_classification", &diva_label::get_max_classification)
    .def("add_classification", &diva_label::add_classification)
    .def("remove_classification", &diva_label::remove_classification)

    .def("to_string", &diva_label::to_string)
    .def("from_string", &diva_label::from_string);
}