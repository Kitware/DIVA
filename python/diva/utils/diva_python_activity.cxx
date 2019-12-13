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
#include "diva_activity.h"

namespace py = pybind11;


using SpanVector = std::vector<std::pair<double, double>>;
PYBIND11_MAKE_OPAQUE(SpanVector);
using ActorSpanMap = std::map<size_t, std::vector<std::pair<double, double>>>;
PYBIND11_MAKE_OPAQUE(ActorSpanMap);

void diva_python_activity(py::module &m)
{
  //py::bind_vector<SpanVector>(m, "SpanVector");
  py::class_<SpanVector>(m, "SpanVector")
    .def(py::init<>())
    .def("back", (std::pair<double, double> &(SpanVector::*)()) &SpanVector::back)
    .def("__len__", [](const SpanVector &v) { return v.size(); })
    .def("__iter__", [](SpanVector &v) {
    return py::make_iterator(v.begin(), v.end());
  }, py::keep_alive<0, 1>());

  //py::bind_map<ActorSpanMap>(m, "ActorSpanMap");
  py::class_<ActorSpanMap>(m, "ActorSpanMap")
    .def(py::init<>())
    .def("__len__", [](const ActorSpanMap &v) { return v.size(); })
    .def("__iter__", [](ActorSpanMap &v) {
    return py::make_iterator(v.begin(), v.end());
  }, py::keep_alive<0, 1>());

  py::enum_<diva_activity::source>(m, "activity_source")
    .value("truth", diva_activity::source::truth)
    .value("user", diva_activity::source::user)
    .export_values();

  py::class_<diva_activity>(m, "activity")
    .def(py::init<>())
    .def("clear", &diva_activity::clear)
    .def("is_valid", &diva_activity::is_valid)
    .def("has_activity_names", &diva_activity::has_activity_names)
    .def("get_activity_names", &diva_activity::get_activity_names)
    .def("get_max_activity_name", &diva_activity::get_max_activity_name)
    .def("set_activity_names", &diva_activity::set_activity_names)
    .def("remove_activity_names", &diva_activity::remove_activity_names)
    .def("has_activity_id", &diva_activity::has_activity_id)
    .def("get_activity_id", &diva_activity::get_activity_id)
    .def("set_activity_id", &diva_activity::set_activity_id)
    .def("remove_activity_id", &diva_activity::remove_activity_id)
    .def("has_source", &diva_activity::has_source)
    .def("get_source", &diva_activity::get_source)
    .def("set_source", &diva_activity::set_source)
    .def("remove_source", &diva_activity::remove_source)
    .def("has_frame_id_span", &diva_activity::has_frame_id_span)
    .def("get_frame_id_span", (std::vector<std::pair<double, double>>&(diva_activity::*)())&diva_activity::get_frame_id_span)
    .def("add_frame_id_span", &diva_activity::add_frame_id_span)
    .def("remove_frame_id_span", &diva_activity::remove_frame_id_span)
    .def("has_frame_time_span", &diva_activity::has_frame_time_span)
    .def("get_frame_time_span", (std::vector<std::pair<double, double>>&(diva_activity::*)())&diva_activity::get_frame_time_span)
    .def("add_frame_time_span", &diva_activity::add_frame_time_span)
    .def("remove_frame_time_span", &diva_activity::remove_frame_time_span)
    .def("has_frame_absolute_time_span", &diva_activity::has_frame_absolute_time_span)
    .def("get_frame_absolute_time_span", (std::vector<std::pair<double, double>>&(diva_activity::*)())&diva_activity::get_frame_absolute_time_span)
    .def("add_frame_absolute_time_span", &diva_activity::add_frame_absolute_time_span)
    .def("remove_frame_absolute_time_span", &diva_activity::remove_frame_absolute_time_span)
    .def("has_actor_frame_id_span", &diva_activity::has_actor_frame_id_span)
    .def("get_actor_frame_id_span", (std::map<size_t, std::vector<std::pair<double, double>>>&(diva_activity::*)())&diva_activity::get_actor_frame_id_span)
    .def("add_actor_frame_id_span", &diva_activity::add_actor_frame_id_span)
    .def("remove_actor_frame_id_span", &diva_activity::remove_actor_frame_id_span)
    .def("has_actor_frame_time_span", &diva_activity::has_actor_frame_time_span)
    .def("get_actor_frame_time_span", (std::map<size_t, std::vector<std::pair<double, double>>>&(diva_activity::*)())&diva_activity::get_actor_frame_time_span)
    .def("add_actor_frame_time_span", &diva_activity::add_actor_frame_time_span)
    .def("remove_actor_frame_time_span", &diva_activity::remove_actor_frame_time_span)
    .def("has_actor_frame_absolute_time_span", &diva_activity::has_actor_frame_absolute_time_span)
    .def("get_actor_frame_absolute_time_span", (std::map<size_t, std::vector<std::pair<double, double>>>&(diva_activity::*)())&diva_activity::get_actor_frame_absolute_time_span)
    .def("add_actor_frame_absolute_time_span", &diva_activity::add_actor_frame_absolute_time_span)
    .def("remove_actor_frame_absolute_time_span", &diva_activity::remove_actor_frame_absolute_time_span)


    .def("to_string", &diva_activity::to_string)
    .def("from_string", &diva_activity::from_string);
}
