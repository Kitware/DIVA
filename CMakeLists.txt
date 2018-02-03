###
# DIVA
###

cmake_minimum_required(VERSION 3.3)
project(DIVA)

# Options
option(DIVA_SUPERBUILD  "Enable DIVA superbuild" ON)

# Common paths include
set(DIVA_CMAKE_DIR ${DIVA_SOURCE_DIR}/CMake)
set(DIVA_STAMP_DIR ${DIVA_BINARY_DIR}/DIVA-ExternalProject-Stamps)

set(CMAKE_MODULE_PATH ${DIVA_CMAKE_DIR} ${CMAKE_MODULE_PATH})
set(CMAKE_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/install CACHE PATH "Install location")

# CMake flags
if(APPLE)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11 -stdlib=libc++")
elseif(WIN32)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /EHsc")
elseif(UNIX)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++11")
endif()

# Superbuild
if(DIVA_SUPERBUILD)
  include(${DIVA_CMAKE_DIR}/superbuild.cmake)
  return()
endif()

find_package(kwiver REQUIRED)
include_directories("${KWIVER_INCLUDE_DIRS}")
link_directories("${KWIVER_LIBRARY_DIRS}")
include(kwiver-cmake-future)
include(kwiver-utils)
include(kwiver-flags)
include(kwiver-configcheck)
find_package(fletch REQUIRED)
# DIVA specific code (inner build)
add_subdirectory(utils)
add_subdirectory(drivers)

set(LIBRARY_PATH_VAR "LD_LIBRARY_PATH")
if( APPLE )
  set(LIBRARY_PATH_VAR "DYLD_FALLBACK_LIBRARY_PATH")
endif()
configure_file(${DIVA_CMAKE_DIR}/setup_DIVA.sh.in  ${CMAKE_INSTALL_PREFIX}/setup_DIVA.sh @ONLY)
configure_file(${DIVA_CMAKE_DIR}/setup_DIVA.bat.in ${CMAKE_INSTALL_PREFIX}/setup_DIVA.bat @ONLY)
configure_file(${DIVA_CMAKE_DIR}/start_MSVC.bat.in   ${CMAKE_INSTALL_PREFIX}/start_MSVC.bat @ONLY)

configure_file(${CMAKE_SOURCE_DIR}/drivers/data/darknet.config.in       ${CMAKE_INSTALL_PREFIX}/drivers/darknet_detections/darknet.config @ONLY)
configure_file(${CMAKE_SOURCE_DIR}/drivers/data/image_experiment.yml.in ${CMAKE_INSTALL_PREFIX}/drivers/image_experiment.yml @ONLY)
configure_file(${CMAKE_SOURCE_DIR}/drivers/data/image_list.txt.in       ${CMAKE_INSTALL_PREFIX}/drivers/image_list.txt @ONLY)
configure_file(${CMAKE_SOURCE_DIR}/drivers/data/video_experiment.yml.in ${CMAKE_INSTALL_PREFIX}/drivers/video_experiment.yml @ONLY)
file(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX}/drivers/darknet_detections/algo-out)
file(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX}/drivers/darknet_detections/eval-out)

