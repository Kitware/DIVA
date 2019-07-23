kwiver_create_python_init(diva)
kwiver_create_python_init(diva/scripts)
kwiver_create_python_init(diva/scripts/cli_helper)

kwiver_add_python_module( ${CMAKE_CURRENT_SOURCE_DIR}/generate_experiments.py
                          diva/scripts/cli_helper
                          generate_experiments )
