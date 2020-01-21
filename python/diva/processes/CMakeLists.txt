kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/image_viewer_process.py
                         processes
                         image_viewer_process)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/simple_detector_process.py
                         processes
                         simple_detector_process)

 kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/__init__.py
                         processes
                         __init__)
