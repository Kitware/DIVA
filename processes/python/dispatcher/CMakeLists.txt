# TODO: find celery

# Add python modules

find_package(kwiver REQUIRED)

kwiver_create_python_plugin_init(DIVA/processes/dispatcher)

kwiver_add_python_module( ${CMAKE_CURRENT_SOURCE_DIR}/celery_config.py
                            DIVA/processes/dispatcher
                            celery_config )

kwiver_add_python_module( ${CMAKE_CURRENT_SOURCE_DIR}/tasks.py
                            DIVA/processes/dispatcher
                            tasks )

kwiver_add_python_module( ${CMAKE_CURRENT_SOURCE_DIR}/dispatcher.py
                            DIVA/processes/dispatcher
                            dispatcher )
