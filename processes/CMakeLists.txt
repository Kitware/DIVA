add_subdirectory( diva_experiment )
# Check if the dependencies for optical flow are met
if(DIVA_ENABLE_OPTICAL_FLOW)
  add_subdirectory( optical_flow )
endif()
