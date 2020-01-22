kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/__init__.py
                         ""
                         __init__)

add_subdirectory(utils)
add_subdirectory(arrows)
add_subdirectory(processes)
