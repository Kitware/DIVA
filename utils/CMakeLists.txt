if(fletch_ENABLED_YAMLCPP) #KWIVER_ENABLE_KPF)
  find_package( yaml-cpp REQUIRED )
  find_package( Boost REQUIRED )#Until yaml's next release..
else()
  message(FATAL_ERROR "DIVA requires the KWIVER KPF arrow, please enable it and rebuild kwiver")
endif()


set( DIVA_BUILD_PYTHON_BINDINGS ON CACHE PATH "Generate Python Bindings" )

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

target_link_libraries( diva_utils
  PRIVATE              vital
                       vital_algo
                       vital_config
                       vital_logger
                       vital_util
                       kwiversys
                 yaml-cpp kpf_yaml
)

add_custom_command(TARGET diva_utils POST_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:diva_utils> ${CMAKE_INSTALL_PREFIX}/lib)
install(TARGETS diva_utils DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)


if(WIN32)
  target_compile_definitions(diva_utils PRIVATE YAML_CPP_DLL)
endif()

add_subdirectory(python)
