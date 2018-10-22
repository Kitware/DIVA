#
# DIVA RC3D Python processes
#
find_package(kwiver REQUIRED)
kwiver_create_python_plugin_init(DIVA/processes/rc3d)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/R-C3D_process.py
  DIVA/processes/rc3d
  R-C3D_process)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/rc3d_json_writter.py
    DIVA/processes/rc3d
    rc3d_json_writer)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/visualize_process.py
    DIVA/processes/rc3d
    visualize_process)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/swimlane_process.py
    DIVA/processes/rc3d
    swimlane_process)

