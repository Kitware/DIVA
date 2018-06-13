
add_subdirectory(schema_examples)
add_subdirectory(basic_experiment)
add_subdirectory(darknet_detections)
add_subdirectory(darknet_training)
add_subdirectory(C3D_training)

add_custom_target(compile_python ALL)
add_custom_command(TARGET compile_python POST_BUILD
                   COMMAND ${CMAKE_COMMAND} -DSOURCE_DIR=${CMAKE_SOURCE_DIR} 
                                            -DBINARY_DIR=${CMAKE_BINARY_DIR}
                                            -P ${DIVA_CMAKE_DIR}/python.cmake)
