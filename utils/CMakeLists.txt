if(fletch_ENABLED_YAMLCPP) #KWIVER_ENABLE_KPF)
  find_package( yaml-cpp REQUIRED )
  find_package( Boost REQUIRED )#Until yaml's next release..
else()
  message(FATAL_ERROR "DIVA requires the KWIVER KPF arrow, please enable it and rebuild kwiver")
endif()


set( sources
  diva_exceptions.cxx
  diva_packet.cxx
  diva_experiment.cxx
  diva_geometry.cxx
  diva_label.cxx
  diva_activity.cxx
)

set( public_headers
  diva_exceptions.h
  diva_packet.h
  diva_experiment.h
  diva_geometry.h
  diva_label.h
  diva_activity.h
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
  PRIVATE        vital
                 vital_logger
                 vital_util
                 yaml-cpp kpf_yaml
)


if(WIN32)
  target_compile_definitions(diva_utils PRIVATE YAML_CPP_DLL)
endif()
