kwiver_create_python_init(diva)
kwiver_create_python_init(diva/scripts)
kwiver_create_python_init(diva/scripts/cli_helpers)

kwiver_add_python_module( ${CMAKE_CURRENT_SOURCE_DIR}/generate_experiments.py
                          diva/scripts/cli_helpers
                          generate_experiments )

kwiver_add_python_module( ${CMAKE_CURRENT_SOURCE_DIR}/merge_videos.py
                          diva/scripts/cli_helpers
                          merge_videos )

kwiver_add_python_module( ${CMAKE_CURRENT_SOURCE_DIR}/cleanup_experiment.py
                          diva/scripts/cli_helpers
                          cleanup_experiment )

kwiver_add_python_module( ${CMAKE_CURRENT_SOURCE_DIR}/cleanup_chunk.py
                          diva/scripts/cli_helpers
                          cleanup_chunk )
