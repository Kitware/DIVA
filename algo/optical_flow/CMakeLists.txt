find_package( OpenCV REQUIRED )
if( OpenCV_VERSION VERSION_LESS "3.0" )
  message( FATAL_ERROR "OpenCV version must be at least 3.0" )
endif()

set(SOURCE "optical_flow.cpp")
include_directories("${CMAKE_BINARY_DIR}")
include_directories("${KWIVER_INCLUDE_DIRS}")
add_executable(optical_flow ${SOURCE})
target_link_libraries(optical_flow
                      kwiversys
                      ${OpenCV_LIBS})
link_directories(${OpenCV_LIB_DIR})

add_custom_command(TARGET  optical_flow POST_BUILD
                   COMMAND ${CMAKE_COMMAND} -E copy $<TARGET_FILE:optical_flow> ${CMAKE_INSTALL_PREFIX}/bin)
install(TARGETS optical_flow RUNTIME DESTINATION ${CMAKE_INSTALL_PREFIX}/bin)

