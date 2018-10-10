#
# DIVA Python processes
#
find_package(kwiver REQUIRED)

kwiver_create_python_plugin_init(DIVA)
kwiver_create_python_plugin_init(DIVA/processes)

# add python processes here
kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/R-C3D_process.py
  DIVA/processes
  R-C3D_process)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/nist_json_writter.py
    DIVA/processes
    nist_json_writer)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/detset_sender_process.py
    DIVA/processes
    detset_sender_process)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/detset_receiver_process.py
    DIVA/processes
    detset_receiver_process)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/visualize_process.py
    DIVA/processes
    visualize_process)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/swimlane_process.py
    DIVA/processes
    swimlane_process)
