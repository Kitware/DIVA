#
# DIVA Processes
#
project( diva_processes )

set( sources
  register_processes.cxx

  diva_experiment_process.cxx
  )

set( private_headers

  diva_experiment_process.h
  )

kwiver_private_header_group( ${private_headers} )

include_directories( ${CMAKE_SOURCE_DIR} ${KWIVER_INCLUDE_DIRS} ${CMAKE_BINARY_DIR} )

kwiver_add_plugin( diva_processes
  SUBDIR           processes
  SOURCES          ${sources}
                   ${private_headers}
  PRIVATE          sprokit_pipeline
                   diva_utils
                   vital vital_vpm vital_logger vital_config
)
