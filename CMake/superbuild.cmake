###
# Superbuild.cmake
###

# General superbuild variables
include(ExternalProject)
include(CMakeDependentOption)

set(DIVA_DEPENDENCIES)

# Git
find_package(Git REQUIRED)

set( fletch_DIR "" CACHE PATH "Path to FLETCH" )
set( kwiver_DIR "" CACHE PATH "Path to KWIVER" )
#set( kwant_DIR "" CACHE PATH "Path to KWANT" )

set( kwiver_FOUND FALSE)
if(kwiver_DIR)
  ## Make sure this is a good kwiver dir
  if ( IS_DIRECTORY ${kwiver_DIR} )
    message(STATUS "Looking for your kwiver...")
    # if we find it, we want to use the fletch_DIR used by kwiver
    # so cache off what we have, and unset it, so we get it in our scope
    set(user_fletch_DIR ${fletch_DIR})
    unset( fletch_DIR CACHE)
    find_package( kwiver NO_MODULE NO_POLICY_SCOPE)
    if ( kwiver_FOUND )
      message(STATUS "I found your kwiver!")
      message(STATUS "It uses this fletch ${fletch_DIR}")
      if(user_fletch_DIR)
        message(STATUS "You provided a fletch_DIR and a kwiver_DIR, I am going to ignore this fletch_DIR and use the fletch_DIR used to build kwiver")
      endif()
    else()
     message(STATUS "I could not find your kwiver!")
     # restore the user fletch dir since we failed to find the provided kwiver
     set( fletch_DIR ${user_fletch_DIR} CACHE PATH "Path to FLETCH" )
    endif()
  else()
    message(STATUS "I could not find your kwiver!")
    set( kwiver_FOUND FALSE)
  endif()
endif()

if(NOT kwiver_FOUND)
  set( kwiver_DIR "" CACHE PATH "Path to KWIVER" )
  
  set( fletch_FOUND FALSE)
  if(fletch_DIR)
    ## Make sure this is a good fletch directory
    if ( IS_DIRECTORY ${fletch_DIR} )
      message(STATUS "Looking for your fletch...")
      find_package( fletch NO_MODULE )
      if ( fletch_FOUND )
        message(STATUS "I found your fletch!")
      else()
        message(STATUS "I could not find your fletch!")
      endif()
    else()
      message(STATUS "I could not find your fletch!")
      set( fletch_FOUND FALSE)
    endif()
  endif()
  
  if(NOT fletch_FOUND)
    set( fletch_DIR "" CACHE PATH "Path to FLETCH" )
    include(CMake/add_project_fletch.cmake)
  endif()
  include(CMake/add_project_kwiver.cmake)
endif()

include(CMake/add_project_kwant.cmake)

# Support ccache
if( CMAKE_VERSION VERSION_LESS 3.4 )
  set( CMAKE_CXX_COMPILER_LAUNCHER_FLAG )
  set( CMAKE_C_COMPILER_LAUNCHER_FLAG )
else()
  set( CMAKE_CXX_COMPILER_LAUNCHER_FLAG
    -DCMAKE_CXX_COMPILER_LAUNCHER:FILEPATH=${CMAKE_CXX_COMPILER_LAUNCHER} )
  set( CMAKE_C_COMPILER_LAUNCHER_FLAG
    -DCMAKE_C_COMPILER_LAUNCHER:FILEPATH=${CMAKE_C_COMPILER_LAUNCHER} )
endif()

# DIVA
set(DIVA_INNER_DIR ${DIVA_BINARY_DIR}/DIVA-build)

ExternalProject_Add(DIVA
  PREFIX DIVA
  DEPENDS ${DIVA_DEPENDENCIES}
  SOURCE_DIR ${DIVA_SOURCE_DIR}
  BINARY_DIR ${DIVA_INNER_DIR}
  STAMP_DIR ${DIVA_STAMP_DIR}
  CMAKE_CACHE_ARGS
    -Dkwiver_DIR:PATH=${kwiver_DIR}
    -DBUILD_SHARED_LIBS:BOOL=ON
    -DDIVA_SUPERBUILD:BOOL=OFF
    -DCMAKE_PREFIX_PATH:STRING=${CMAKE_PREFIX_PATH}
    -DCMAKE_INSTALL_PREFIX:STRING=${CMAKE_INSTALL_PREFIX}
    -DCMAKE_BUILD_TYPE:STRING=${CMAKE_BUILD_TYPE}
    -DCMAKE_CXX_COMPILER:FILEPATH=${CMAKE_CXX_COMPILER}
    -DCMAKE_CXX_FLAGS:STRING=${ep_common_cxx_flags}
    -DCMAKE_C_COMPILER:FILEPATH=${CMAKE_C_COMPILER}
    -DCMAKE_C_FLAGS:STRING=${ep_common_c_flags}
     ${CMAKE_CXX_COMPILER_LAUNCHER_FLAG}
     ${CMAKE_C_COMPILER_LAUNCHER_FLAG}
    -DCMAKE_EXE_LINKER_FLAGS:STRING=${CMAKE_EXE_LINKER_FLAGS}
    -DCMAKE_SHARED_LINKER_FLAGS:STRING=${CMAKE_SHARED_LINKER_FLAGS}
    -DADDITIONAL_C_FLAGS:STRING=${ADDITIONAL_C_FLAGS}
    -DADDITIONAL_CXX_FLAGS:STRING=${ADDITIONAL_CXX_FLAGS}
  INSTALL_COMMAND cmake -E echo "Skipping install step."
)
