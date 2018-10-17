#
# DIVA Python processes
#
find_package(kwiver REQUIRED)

kwiver_create_python_plugin_init(DIVA)
kwiver_create_python_plugin_init(DIVA/processes)

kwiver_create_python_plugin_init(DIVA/processes/act)
kwiver_create_python_plugin_init(DIVA/processes/rc3d)

add_subdirectory(act)
add_subdirectory(rc3d)
