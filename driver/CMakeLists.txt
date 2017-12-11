
set(SOURCE "main.cpp"
)

include_directories("${CMAKE_BINARY_DIR}")
include_directories("${CMAKE_SOURCE_DIR}/utils")
add_executable(diva_driver ${SOURCE})
target_link_libraries(diva_driver 
                      diva_utils)

if(WIN32)
  target_compile_definitions(diva_driver PRIVATE YAML_CPP_DLL)
endif()