#
# DIVA Processes
#
project( diva_processes )

find_package(kwiver REQUIRED)
find_package(Boost REQUIRED COMPONENTS system chrono)
find_package(GFlags COMPONENTS static)

set( sources
  register_processes.cxx

  diva_experiment_process.cxx
  )

set( private_headers

  diva_experiment_process.h
  )

kwiver_private_header_group( ${private_headers} )

include_directories( ${CMAKE_SOURCE_DIR} ${KWIVER_INCLUDE_DIRS} ${CMAKE_BINARY_DIR} )

if(SKBUILD)
  set( KWIVER_LIBRARY_DIR "" )
endif()
kwiver_add_plugin( diva_processes
  SUBDIR           ${diva_plugin_process_subdir}
  SOURCES          ${sources}
                   ${private_headers}
  PRIVATE          sprokit_pipeline
                   diva_utils
                   kwiver_algo_ocv
                   vital vital_vpm vital_logger vital_config
                   ${OpenCV_LIBS}
                   boost_thread boost_chrono boost_system
                   gflags_static
                   "-Wl,-Bsymbolic"
)
