
set(SOURCE "schema_examples.cpp")
include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")
include_directories("${KWIVER_INCLUDE_DIRS}")
add_executable(schema_examples ${SOURCE})
target_link_libraries(schema_examples 
                      diva_utils)

add_custom_command(TARGET schema_examples POST_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:schema_examples> ${CMAKE_INSTALL_PREFIX}/bin)
install(TARGETS schema_examples RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)

if(WIN32)
  target_compile_definitions(schema_examples PRIVATE YAML_CPP_DLL)
endif()
