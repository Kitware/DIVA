#include <pybind11/pybind11.h>
#include "diva_label.h"

namespace py = pybind11;

PYBIND11_MODULE(diva, m) {
  py::class_<diva_label>(m, "diva_label")
    .def(py::init<>())
    .def("clear", &diva_label::clear)
    .def("is_valid", &diva_label::is_valid)
    .def("has_track_id", &diva_label::has_track_id)
    .def("get_track_id", &diva_label::get_track_id)
    .def("set_track_id", &diva_label::set_track_id)
    .def("remove_track_id", &diva_label::remove_track_id);
}