#
# Setup and define DIVA sphinx support
#
find_package(Sphinx)

function(diva_create_sphinx)
   add_custom_target(sphinx-diva
     COMMAND ${SPHINX_EXECUTABLE} -D breathe_projects.diva="${CMAKE_BINARY_DIR}/doc/diva/xml" ${CMAKE_SOURCE_DIR}/doc/manuals ${CMAKE_BINARY_DIR}/doc/sphinx
  )

endfunction(diva_create_sphinx)
