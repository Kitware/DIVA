# We only need to get OpenCV needed for the optional image display logic in some examples
find_package( OpenCV REQUIRED )
if( OpenCV_VERSION VERSION_LESS "2.4" )
  message( FATAL_ERROR "OpenCV version must be at least 2.4" )
endif()

find_package( GFlags COMPONENTS static )

set(SOURCE "darknet_detections.cpp")

include_directories(${OpenCV_INCLUDE_DIRS})
include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")
include_directories("${KWIVER_INCLUDE_DIRS}")
add_executable(darknet_detections ${SOURCE})
target_link_libraries(darknet_detections 
                      diva_utils
                      kwiver_algo_ocv
                      kwiver_algo_ffmpeg_impl
                      kwiversys
                      vital
                      vital_algo
                      vital_config
                      vital_logger
                      vital_util
                      vital_exceptions
                      vital_vpm
                      kpf_yaml
                      yaml-cpp
# The next 2 lines (and 'kwiver_algo_ocv' above) are needed for the optional image display logic in some examples
                      ${OpenCV_LIBS}
                      ${Boost_LIBS}
                      gflags_static)
link_directories(${OpenCV_LIB_DIR})
add_custom_command(TARGET darknet_detections POST_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:darknet_detections> ${CMAKE_INSTALL_PREFIX}/bin)

install(TARGETS darknet_detections RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)

if(WIN32)
  target_compile_definitions(darknet_detections PRIVATE YAML_CPP_DLL)
endif()
