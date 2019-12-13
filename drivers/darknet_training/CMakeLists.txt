find_package( OpenCV REQUIRED )
if( OpenCV_VERSION VERSION_LESS "2.4" )
  message( FATAL_ERROR "OpenCV version must be at least 2.4" )
endif()

set(SOURCE "darknet_training.cpp")
include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")
include_directories("${KWIVER_INCLUDE_DIRS}")
add_executable(darknet_training ${SOURCE})
target_link_libraries(darknet_training
                      diva_utils
                      kwiversys
                      kpf_yaml
                      ${OpenCV_LIBS})
link_directories(${OpenCV_LIB_DIR})

add_custom_command(TARGET darknet_training POST_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:darknet_training> ${CMAKE_INSTALL_PREFIX}/bin)
install(TARGETS darknet_training RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)

if(WIN32)
  target_compile_definitions(darknet_training PRIVATE YAML_CPP_DLL)
endif()
