###
# DIVA
###
cmake_minimum_required(VERSION 3.3)

set(CMAKE_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/install CACHE PATH "Install location")
project(DIVA)

# Options
option(DIVA_SUPERBUILD  "Enable DIVA superbuild" ON)

# Common paths include
set(DIVA_CMAKE_DIR ${DIVA_SOURCE_DIR}/CMake)
set(DIVA_STAMP_DIR ${DIVA_BINARY_DIR}/DIVA-ExternalProject-Stamps)

set(CMAKE_MODULE_PATH ${DIVA_CMAKE_DIR} ${CMAKE_MODULE_PATH})

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
configure_file(${DIVA_CMAKE_DIR}/setup_DIVA.sh.in  ${CMAKE_BINARY_DIR}/setup_DIVA.sh @ONLY)
configure_file(${DIVA_CMAKE_DIR}/setup_DIVA.bat.in ${CMAKE_BINARY_DIR}/setup_DIVA.bat @ONLY)
configure_file(${DIVA_CMAKE_DIR}/start_MSVC.bat.in   ${CMAKE_BINARY_DIR}/start_MSVC.bat @ONLY)
if(WIN32)
  install(FILES ${CMAKE_BINARY_DIR}/setup_DIVA.bat DESTINATION ${CMAKE_INSTALL_PREFIX})
  install(FILES ${CMAKE_BINARY_DIR}/start_MSVC.bat DESTINATION ${CMAKE_INSTALL_PREFIX})
else()
  install(FILES ${CMAKE_BINARY_DIR}/setup_DIVA.sh DESTINATION ${CMAKE_INSTALL_PREFIX})
endif()

configure_file(${CMAKE_SOURCE_DIR}/etc/darknet.config       ${CMAKE_BINARY_DIR}/etc/darknet.config COPYONLY)
configure_file(${CMAKE_SOURCE_DIR}/etc/image_experiment.yml ${CMAKE_BINARY_DIR}/etc/image_experiment.yml COPYONLY)
configure_file(${CMAKE_SOURCE_DIR}/etc/image_list.txt       ${CMAKE_BINARY_DIR}/etc/image_list.txt COPYONLY)
configure_file(${CMAKE_SOURCE_DIR}/etc/video_experiment.yml ${CMAKE_BINARY_DIR}/etc/video_experiment.yml COPYONLY)
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/etc/algo-out)
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/etc/eval-out)

install(FILES ${CMAKE_SOURCE_DIR}/etc/darknet.config         DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
install(FILES ${CMAKE_SOURCE_DIR}/etc/image_experiment.yml   DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
install(FILES ${CMAKE_SOURCE_DIR}/etc/image_list.txt         DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
install(FILES ${CMAKE_SOURCE_DIR}/etc/video_experiment.yml   DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
file(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX}/etc/algo-out)
file(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX}/etc/eval-out)


