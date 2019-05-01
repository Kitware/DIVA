
find_package(fletch REQUIRED)
find_package(pybind11 CONFIG REQUIRED)
find_package(kwiver REQUIRED)

include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")
include_directories(${pybind11_INCLUDE_DIR})
include_directories(${KWIVER_INCLUDE_DIR})

kwiver_add_python_library(utils
  diva
  diva_python_utils.cxx
  diva_python_packet.cxx
  diva_python_label.cxx
  diva_python_geometry.cxx
  diva_python_activity.cxx
  diva_python_experiment.cxx
  diva_python_input.cxx
)

kwiver_create_python_init(diva)


target_link_libraries(python-diva-utils
  PUBLIC ${PYTHON_LIBRARIES}
  PRIVATE diva_utils )

if(WIN32)
  target_compile_definitions(python-diva-utils PRIVATE YAML_CPP_DLL)
endif()
