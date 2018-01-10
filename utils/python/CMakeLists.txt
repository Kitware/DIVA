

set(PYBIND11_PYTHON_VERSION 2.7 CACHE STRING "")
find_package(pybind11 CONFIG REQUIRED)

include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")

set( sources
  diva_python_experiment.cxx
  diva_python_geometry.cxx
  diva_python_label.cxx
  diva_python_activity.cxx
)

set( public_headers
)

set( private_headers
)

pybind11_add_module(diva_python_utils SHARED NO_EXTRAS
  ${sources}
  ${public_headers}
  ${private_sources}
)


target_include_directories(diva_python_utils PRIVATE ${CMAKE_BINARY_DIR})

target_link_libraries( diva_python_utils
  PRIVATE              diva_utils
)


if(WIN32)
  target_compile_definitions(diva_utils PRIVATE YAML_CPP_DLL)
endif()
