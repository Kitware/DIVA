# We need to get OpenCV to display the frame images
find_package( OpenCV REQUIRED )
if( OpenCV_VERSION VERSION_LESS "2.4" )
  message( FATAL_ERROR "OpenCV version must be at least 2.4" )
endif()
include_directories(${OpenCV_INCLUDE_DIRS})

set(SOURCE "basic_experiment.cpp")
include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")
add_executable(basic_experiment ${SOURCE})
target_link_libraries(basic_experiment 
                      diva_utils
                      kwiver_algo_ocv
                      ${OpenCV_LIBS})
link_directories(${OpenCV_LIB_DIR})

if(WIN32)
  target_compile_definitions(basic_experiment PRIVATE YAML_CPP_DLL)
endif()
