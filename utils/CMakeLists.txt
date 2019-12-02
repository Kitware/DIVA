if(fletch_ENABLED_YAMLCPP) #KWIVER_ENABLE_KPF)
  find_package( yaml-cpp REQUIRED )
  find_package( Boost REQUIRED )#Until yaml's next release..
else()
  message(FATAL_ERROR "DIVA utils requires yaml cpp and boost")
endif()
find_package( kwiver REQUIRED)
find_package( Eigen3 REQUIRED )

if(NOT fletch_ENABLED_OpenCV)
  message(FATAL_ERROR "DIVA input requires opencv, please enable it and rebuild kwiver")
endif()
find_package( OpenCV REQUIRED )

set( DIVA_BUILD_PYTHON_BINDINGS ON CACHE PATH "Generate Python Bindings" )
include_directories(${KWIVER_INCLUDE_DIRS})
set( sources
  diva_exceptions.cxx
  diva_experiment.cxx
  diva_input.cxx
  diva_packet.cxx
  diva_geometry.cxx
  diva_label.cxx
  diva_activity.cxx
)

set( public_headers
  diva_exceptions.h
  diva_experiment.h
  diva_input.h
  diva_packet.h
  diva_geometry.h
  diva_label.h
  diva_activity.h
)

kwiver_install_headers(
   ${public_headers}
 )

 kwiver_install_headers(
   ${CMAKE_CURRENT_BINARY_DIR}/diva_utils_export.h
   NOPATH
   SUBDIR   utils
 )
 

set( private_headers
)
kwiver_add_library( diva_utils
  ${sources}
  ${public_headers}
  ${private_sources}
)

target_include_directories(diva_utils PRIVATE ${CMAKE_BINARY_DIR})
target_include_directories(diva_utils PRIVATE ${YAML_CPP_INCLUDE_DIR})
target_include_directories(diva_utils PRIVATE ${Boost_INCLUDE_DIR})
target_include_directories(diva_utils PRIVATE ${KWIVER_INCLUDE_DIR})
target_include_directories(diva_utils PRIVATE ${EIGEN3_INCLUDE_DIR})

target_link_libraries( diva_utils
  PRIVATE              kwiver_ocv_image_container
                       kwiver_algo_ffmpeg_impl
                       vital_klv
                       vital
                       vital_logger
                       vital_util
                       vital_exceptions
                       kwiversys
                       yaml-cpp
                       kpf_yaml
                       ${OpenCV_LIBS}
)

if(NOT EXISTS ${CMAKE_INSTALL_PREFIX}/lib)
  file(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX}/lib)
endif()
add_custom_command(TARGET diva_utils POST_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:diva_utils> ${CMAKE_INSTALL_PREFIX}/lib)
install(TARGETS diva_utils DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)


if(WIN32)
  target_compile_definitions(diva_utils PRIVATE YAML_CPP_DLL)
endif()
