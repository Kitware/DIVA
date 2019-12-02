find_package(fletch REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_package(kwiver REQUIRED)
find_package(GFlags COMPONENTS static)

include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")
include_directories(${pybind11_INCLUDE_DIR})
include_directories(${KWIVER_INCLUDE_DIR})

kwiver_add_python_library(utils
  utils
  diva_python_utils.cxx
  diva_python_packet.cxx
  diva_python_label.cxx
  diva_python_geometry.cxx
  diva_python_activity.cxx
  diva_python_experiment.cxx
  diva_python_input.cxx
)

target_link_libraries(python-utils-utils
  PUBLIC ${PYTHON_LIBRARIES}
  PRIVATE diva_utils
          vital_config
          kpf_yaml
          yaml-cpp
          gflags_static
          "-Wl,-Bsymbolic")

if(WIN32)
  target_compile_definitions(python-utils-utils PRIVATE YAML_CPP_DLL)
endif()
