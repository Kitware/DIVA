
ExternalData_Add_Test(download_darknet_models
  NAME Download
  COMMAND 
  DATA{darknet_models.tar.gz}
  )
ExternalData_Add_Target(download_darknet_models)

add_custom_target(extract_darknet_models ALL)
add_dependencies(extract_darknet_models download_darknet_models)
add_custom_command(TARGET extract_darknet_models POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E tar xzf ${CMAKE_CURRENT_BINARY_DIR}/darknet_models.tar.gz
            WORKING_DIRECTORY ${CMAKE_INSTALL_PREFIX}/etc)
