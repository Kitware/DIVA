###
# DIVA
###
cmake_minimum_required(VERSION 3.3)

set(CMAKE_INSTALL_PREFIX ${CMAKE_BINARY_DIR}/install CACHE PATH "Install location")
project(DIVA)

# Options
option(DIVA_SUPERBUILD  "Enable DIVA superbuild" ON)
# NOTE: Do Not Use DIVA_ENABLE_DOCUMENTATION as kwiver_create_doxygen creates a dependent
#       variable by the same name.
option(DIVA_BUILD_DOCUMENTATION "Build DIVA documentation using Doxygen and Sphinx" OFF)
option(DIVA_ENABLE_PYTHON "Build python bindings for DIVA" ON)

# Common paths include
set(DIVA_CMAKE_DIR ${DIVA_SOURCE_DIR}/CMake)
set(DIVA_STAMP_DIR ${DIVA_BINARY_DIR}/DIVA-ExternalProject-Stamps)

set(CMAKE_MODULE_PATH ${DIVA_CMAKE_DIR} ${CMAKE_MODULE_PATH})

# Option for CUDA
option(DIVA_BUILD_WITH_CUDA "Build with CUDA support" FALSE)
if (DIVA_BUILD_WITH_CUDA)
  find_package( CUDA QUIET REQUIRED )
# Option for CUDNN
  option(DIVA_BUILD_WITH_CUDNN "Build with CUDNN support" FALSE)
  if (DIVA_BUILD_WITH_CUDNN)
    set( CUDNN_TOOLKIT_ROOT_DIR "" CACHE PATH "CUDNN root folder" )
    find_package( CUDNN QUIET REQUIRED)
  endif()
elseif(DIVA_BUILD_WITH_CUDNN)
  unset(DIVA_BUILD_WITH_CUDNN CACHE)
  message(WARNING "Disabling DIVA_BUILD_WITH_CUDNN, You must have DIVA_BUILD_WITH_CUDA enabled for this to be enabled")
endif()

if(DIVA_ENABLE_PYTHON)
  set(DIVA_PYTHON_MAJOR_VERSION "3" CACHE STRING "Python version to use: 3 or 2" )
  set_property( CACHE DIVA_PYTHON_MAJOR_VERSION PROPERTY STRINGS "3" "2")
  set(KWIVER_PYTHON_MAJOR_VERSION ${DIVA_PYTHON_MAJOR_VERSION})
  set(KWIVER_ENABLE_PYTHON true)
endif()

# Superbuild
if(DIVA_SUPERBUILD)
  include(${DIVA_CMAKE_DIR}/superbuild.cmake)
  return()
endif()

if( IS_DIRECTORY ${fletch_DIR} )
  find_package( fletch CONFIG )
  if ( fletch_FOUND )
    list(APPEND CMAKE_PREFIX_PATH "${fletch_ROOT}")
  endif()
endif()

find_package(kwiver REQUIRED)
link_directories("${KWIVER_LIBRARY_DIRS}")
include(kwiver-cmake-future)
include(kwiver-utils)
include(kwiver-flags)
include(kwiver-configcheck)
set(kwiver_python_output_path  "${CMAKE_BINARY_DIR}/${python_lib_subdir}")

##
# Documentation for DIVA
if(DIVA_BUILD_DOCUMENTATION)   
    kwiver_create_doxygen( diva "${CMAKE_CURRENT_LIST_DIR}" )
    add_subdirectory( doc )    
endif()

find_package( fletch REQUIRED )


###
# Set location for process plugins
set( diva_plugin_process_subdir diva/processes )
set( diva_plugin_module_subdir  diva/modules )

# DIVA specific code (inner build)
add_subdirectory(utils)
#add_subdirectory(drivers)
add_subdirectory(external)
add_subdirectory(algo)
add_subdirectory(processes)


set(LIBRARY_PATH_VAR "LD_LIBRARY_PATH")
if( APPLE )
  set(LIBRARY_PATH_VAR "DYLD_FALLBACK_LIBRARY_PATH")
endif()

configure_file(${CMAKE_SOURCE_DIR}/CMake/diva-config.cmake.in ${CMAKE_INSTALL_PREFIX}/diva-config.cmake @ONLY)
if(WIN32)
  configure_file(${DIVA_CMAKE_DIR}/start_MSVC.bat.in          ${CMAKE_BINARY_DIR}/start_MSVC.bat @ONLY)
  configure_file(${DIVA_CMAKE_DIR}/setup_DIVA.build.bat.in    ${CMAKE_BINARY_DIR}/setup_DIVA.bat @ONLY)
  configure_file(${DIVA_CMAKE_DIR}/setup_DIVA.install.bat.in  ${CMAKE_INSTALL_PREFIX}/setup_DIVA.bat @ONLY)
else()
  if(DIVA_SUPERBUILD)
    set(KWIVER_INSTALL_PATH "${CMAKE_INSTALL_PATH}")
  else()
    set(KWIVER_INSTALL_PATH "${KWIVER_DIR}")
  endif()
  configure_file(${DIVA_CMAKE_DIR}/setup_DIVA.build.sh.in     ${CMAKE_BINARY_DIR}/setup_DIVA.sh @ONLY)
  configure_file(${DIVA_CMAKE_DIR}/setup_DIVA.install.sh.in   ${CMAKE_INSTALL_PREFIX}/setup_DIVA.sh @ONLY)
endif()

configure_file(${CMAKE_SOURCE_DIR}/etc/darknet.config       ${CMAKE_BINARY_DIR}/etc/darknet.config COPYONLY)
configure_file(${CMAKE_SOURCE_DIR}/etc/image_experiment.yml ${CMAKE_BINARY_DIR}/etc/image_experiment.yml COPYONLY)
configure_file(${CMAKE_SOURCE_DIR}/etc/image_list.txt       ${CMAKE_BINARY_DIR}/etc/image_list.txt COPYONLY)
configure_file(${CMAKE_SOURCE_DIR}/etc/video_experiment.yml ${CMAKE_BINARY_DIR}/etc/video_experiment.yml COPYONLY)
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/etc/algo-out)
file(MAKE_DIRECTORY ${CMAKE_BINARY_DIR}/etc/eval-out)
file(COPY ${CMAKE_SOURCE_DIR}/etc/images   DESTINATION ${CMAKE_BINARY_DIR}/etc)
file(COPY ${CMAKE_SOURCE_DIR}/etc/ref-geom DESTINATION ${CMAKE_BINARY_DIR}/etc)
file(COPY ${CMAKE_SOURCE_DIR}/etc/video    DESTINATION ${CMAKE_BINARY_DIR}/etc)

install(FILES ${CMAKE_SOURCE_DIR}/etc/darknet.config         DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
install(FILES ${CMAKE_SOURCE_DIR}/etc/image_experiment.yml   DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
install(FILES ${CMAKE_SOURCE_DIR}/etc/image_list.txt         DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
install(FILES ${CMAKE_SOURCE_DIR}/etc/video_experiment.yml   DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
file(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX}/etc/algo-out)
file(MAKE_DIRECTORY ${CMAKE_INSTALL_PREFIX}/etc/eval-out)
file(COPY ${CMAKE_SOURCE_DIR}/etc/images   DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
file(COPY ${CMAKE_SOURCE_DIR}/etc/ref-geom DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
file(COPY ${CMAKE_SOURCE_DIR}/etc/video    DESTINATION ${CMAKE_INSTALL_PREFIX}/etc)
configure_file(${CMAKE_SOURCE_DIR}/drivers/schema_examples/schema_examples.py ${CMAKE_INSTALL_PREFIX}/python/schema_examples.py COPYONLY)
configure_file(${CMAKE_SOURCE_DIR}/drivers/system_script/diva_system.py       ${CMAKE_INSTALL_PREFIX}/python/diva_system.py COPYONLY) 
