

set(PYBIND11_PYTHON_VERSION 2.7 CACHE STRING "")
find_package(pybind11 CONFIG REQUIRED)

include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")

set( sources
  diva_python_utils.cxx
  diva_python_packet.cxx
  diva_python_label.cxx
  diva_python_geometry.cxx
  diva_python_activity.cxx
  diva_python_experiment.cxx
)

set( public_headers
)

set( private_headers
)

pybind11_add_module(diva_python_utils MODULE NO_EXTRAS
  ${sources}
  ${public_headers}
  ${private_sources}
)

set_target_properties( diva_python_utils
    PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin"
    LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib"
)

target_include_directories(diva_python_utils PRIVATE ${CMAKE_BINARY_DIR})

message(STATUS "Pylibs : ${pybind11_LIBRARIES}")
target_link_libraries( diva_python_utils
  PRIVATE              diva_utils pybind11::embed
)


add_custom_command(TARGET diva_python_utils POST_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:diva_python_utils> ${CMAKE_INSTALL_PREFIX}/lib)
install(TARGETS diva_python_utils DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)

if(WIN32)
  target_compile_definitions(diva_utils PRIVATE YAML_CPP_DLL)
endif()
