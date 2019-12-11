# We need to get OpenCV to display the frame images
find_package( OpenCV REQUIRED )
if( OpenCV_VERSION VERSION_LESS "2.4" )
  message( FATAL_ERROR "OpenCV version must be at least 2.4" )
endif()
include_directories(${OpenCV_INCLUDE_DIRS})

set(SOURCE "basic_experiment.cpp")
include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")
include_directories("${KWIVER_INCLUDE_DIRS}")
add_executable(basic_experiment ${SOURCE})
target_link_libraries(basic_experiment 
                      diva_utils
                      kwiver_ocv_image_container
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
                      ${OpenCV_LIBS})
link_directories(${OpenCV_LIB_DIR})

add_custom_command(TARGET basic_experiment POST_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:basic_experiment> ${CMAKE_INSTALL_PREFIX}/bin)
install(TARGETS basic_experiment RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)

if(WIN32)
  target_compile_definitions(basic_experiment PRIVATE YAML_CPP_DLL)
endif()
