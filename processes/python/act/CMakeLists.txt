#
# DIVA ACT Python processes
#
find_package(kwiver REQUIRED)
kwiver_create_python_plugin_init(DIVA/processes/act)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/act_detector.py
    DIVA/processes/act
    act_detector)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/merge_tubes.py
    DIVA/processes/act
    merge_tubes)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/act_json_writer.py
    DIVA/processes/act
    act_json_writer)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/modify_bbox_resolution.py
    DIVA/processes/act
    modify_bbox_resolution)

kwiver_add_python_module(${CMAKE_CURRENT_SOURCE_DIR}/act_visualizer.py
    DIVA/processes/act
    act_visualizer)
