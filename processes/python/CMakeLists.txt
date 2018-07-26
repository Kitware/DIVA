#
# DIVA Python processes
#
kwiver_create_python_plugin_init(DIVA)
kwiver_create_python_plugin_init(DIVA/processes)

# add python processes here
kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/R-C3D_process.py
  DIVA/processes
  R-C3D_process)
