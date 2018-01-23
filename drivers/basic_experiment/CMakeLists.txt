
set(SOURCE "basic_experiment.cpp")
include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")
add_executable(basic_experiment ${SOURCE})
target_link_libraries(basic_experiment 
                      diva_utils)

if(WIN32)
  target_compile_definitions(basic_experiment PRIVATE YAML_CPP_DLL)
endif()
