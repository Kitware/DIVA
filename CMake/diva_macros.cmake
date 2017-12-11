#
# Common macros for DIVA
#

macro(DIVA_check_dependency)
  set(options REQUIRED)
  set(oneValueArgs PROJECT DEPENDENCY)
  set(multiValueArgs)
  cmake_parse_arguments(MY
    "${options}"
    "${oneValueArgs}"
    "${multiValueArgs}"
    ${ARGN}
    )

  if(NOT DIVA_USE_SYSTEM_${MY_DEPENDENCY})
    list(APPEND ${MY_PROJECT}_DEPENDENCIES ${MY_DEPENDENCY})
  else()
    if (MY_REQUIRED)
      find_package(${MY_DEPENDENCY} REQUIRED)
    else()
      find_package(${MY_DEPENDENCY})
    endif()
  endif()
  list(APPEND ${MY_PROJECT}_ARGS -D${MY_DEPENDENCY}_DIR:PATH=${${MY_DEPENDENCY}_DIR})
endmacro()

macro(DIVA_add_external_project)
  set(options
    REQUIRED
    )
  set(oneValueArgs
    PROJECT
    )
  set(multiValueArgs DEPENDS)

  cmake_parse_arguments(MY
    "${options}"
    "${oneValueArgs}"
    "${multiValueArgs}"
    ${ARGN}
    )

  foreach(dependency ${MY_DEPENDS})
    CMAKE_DEPENDENT_OPTION(
      DIVA_USE_SYSTEM_${dependency} "Use ${dependency} from the system" OFF
      "DIVA_SUPERBUILD" ON)

    if(NOT DIVA_USE_SYSTEM_${dependency})
      include("${DIVA_CMAKE_DIR}/add_project_${dependency}.cmake")
    endif()

    DIVA_check_dependency(PROJECT DIVA DEPENDENCY ${dependency} REQUIRED ${MY_REQUIRED})
  endforeach()
endmacro()

function(DIVA_force_install_project)
  set(options)
  set(oneValueArgs
    PROJECT
    )
  set(multiValueArgs STEPS)

  cmake_parse_arguments(MY
    "${options}"
    "${oneValueArgs}"
    "${multiValueArgs}"
    ${ARGN}
    )
  if(NOT DEFINED MY_STEPS)
    set(MY_STEPS install)
  endif()

  ExternalProject_Add_StepTargets(${MY_PROJECT} install)

  foreach(stamp_file_name ${MY_STEPS})
    set(stamp_file_root "${DIVA_STAMP_DIR}")
    if(CMAKE_CONFIGURATION_TYPES)
      set(stamp_file "${stamp_file_root}/${CMAKE_CFG_INTDIR}/${MY_PROJECT}-${stamp_file_name}")
    else()
      set(stamp_file "${stamp_file_root}/${MY_PROJECT}-${stamp_file_name}")
    endif()

    add_custom_command(TARGET ${MY_PROJECT}-install
        PRE_BUILD
        COMMAND ${CMAKE_COMMAND} -E remove "${stamp_file}"
        COMMENT "Removing file ${stamp_file}'"
      )
  endforeach()
  set_target_properties(${MY_PROJECT}-install PROPERTIES EXCLUDE_FROM_DEFAULT_BUILD True)
  set_target_properties(${MY_PROJECT}-install PROPERTIES EXCLUDE_FROM_ALL True)
endfunction()
