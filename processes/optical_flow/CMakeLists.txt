#
# Optical Flow Processes
#
project( optical_flow_processes )

find_package(kwiver REQUIRED)

set( sources
  register_processes.cxx

  optical_flow_process.cxx
  )

set( private_headers
  optical_flow_process.h
  )

kwiver_private_header_group( ${private_headers} )

include_directories( ${CMAKE_SOURCE_DIR} ${KWIVER_INCLUDE_DIRS} ${CMAKE_BINARY_DIR} )

find_package( OpenCV REQUIRED )
if( OpenCV_VERSION VERSION_LESS "3.0" )
    message( FATAL_ERROR "OpenCV version must be at least 3.0" )
endif()

kwiver_add_plugin( diva_optical_flow 
  SUBDIR           ${diva_plugin_process_subdir}
  SOURCES          ${sources}
                   ${private_headers}
  PRIVATE          sprokit_pipeline
                   diva_utils
                   vital vital_vpm vital_logger vital_config
                   kwiver_algo_ocv
                   ${OpenCV_LIBS}

)

