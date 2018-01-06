
set(SOURCE "schema_examples.cpp")
include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")
add_executable(schema_examples ${SOURCE})
target_link_libraries(schema_examples 
                      diva_utils)

if(WIN32)
  target_compile_definitions(schema_examples PRIVATE YAML_CPP_DLL)
endif()