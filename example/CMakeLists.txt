# The intent of this CMakeLists.txt is for you to reuse it for your own program sources
cmake_minimum_required(VERSION 3.3)# You can change this to any verision you wish
project(simple_example)

# This variable tells cmake where it can find the DIVA-config.cmake file
# You need to have unzipped the DIVA install archive to the /opt directory
set(DIVA_DIR "/opt/kitware/DIVA" CACHE PATH "Path to DIVA package")
# Have CMake load the config file and set up all necessary build variables
# Note this will include getting the KWIVER and Fletch packages for you
find_package(DIVA REQUIRED)
# Add DIVA build variables to our project build variables
include_directories("${DIVA_INCLUDE_DIRS}")
link_directories(${DIVA_LIBRARY_DIRS})

# Part of the DIVA config also includes getting Fletch build variables
# This will inform CMake where to find all of the libraries Fletch built
# So we can just find the package with out haveing to define where the
# package config file is (Fletch will tell CMake)
# NOTE the code for this sample project does NOT use OpenCV
# This is an example of what you need to do to bring in a external
# library into your CMake project
find_package( OpenCV REQUIRED )
if( OpenCV_VERSION VERSION_LESS "2.4" )
  message( FATAL_ERROR "OpenCV version must be at least 2.4" )
endif()
# Add this package build variables to our project build variables
link_directories(${OpenCV_LIB_DIR})
include_directories(${OpenCV_INCLUDE_DIRS})

# For this example, we will reuse one of the drivers as our source.
# These drivers are simple and have a main function, so it a good example.
# You can replace this with your source and name the executable to what you want
set(SOURCE "../drivers/schema_examples/schema_examples.cpp")
add_executable(simple_example ${SOURCE})

# Link to the diva_utils library to use the provided API
# The other 
target_link_libraries(simple_example 
# These few libraries are the minimal libraries
# you need to use the DIVA API and access kwiver functionality
# such as the diva_input class image_container
                      diva_utils
                      kwiversys
                      vital
                      vital_algo
                      vital_config
                      vital_logger
                      vital_util
                      vital_vpm
# These next libraries are here to demonstrate
# linking to a particulare arrow and its dependent libraries
# It is not necessary if you are not using OpenCV
# note you are not required to use the arrow, if you 
# want to just use the straight 3rd party libraries
                      kwiver_algo_ocv
                      ${OpenCV_LIBS})
