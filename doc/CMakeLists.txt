find_package( Sphinx REQUIRED )
# Set HTML icon for the configuration
set( HTML_FAVICON "${CMAKE_CURRENT_BINARY_DIR}/favicon.ico" )

# Assuming that the plugins go to dist-packages
set(PYTHON_PROCESS_ROOT "${DIVA_BINARY_DIR}/lib/python2.7/dist-packages")

set(DOXYGEN_XML_ROOT "${CMAKE_BINARY_DIR}/doc/diva/xml")

set(SPHINX_HTML_DIR "${CMAKE_BINARY_DIR}/doc/sphinx/html")
set(SPHINX_CACHE_DIR "${CMAKE_BINARY_DIR}/doc/sphinx/_cache")

configure_file( "${DIVA_CMAKE_DIR}/templates/sphinx/conf.py.in"
                "${CMAKE_BINARY_DIR}/doc/sphinx/conf.py" 
                @ONLY )

configure_file( "${CMAKE_SOURCE_DIR}/doc/favicon.ico" 
                "${HTML_FAVICON}" 
                COPYONLY )

configure_file( "${CMAKE_SOURCE_DIR}/doc/manuals/_static/style.css" 
                "${CMAKE_BINARY_DIR}/doc/sphinx/_static/style.css" 
                COPYONLY )
configure_file( "${CMAKE_SOURCE_DIR}/doc/manuals/_templates/layout.html" 
                "${CMAKE_BINARY_DIR}/doc/sphinx/_templates/layout.html" 
                COPYONLY )

add_custom_target( sphinx-diva
    COMMAND ${SPHINX_EXECUTABLE} 
        -a -c "${CMAKE_BINARY_DIR}/doc/sphinx" 
        -d "${SPHINX_CACHE_DIR}"
        ${CMAKE_SOURCE_DIR}/doc/manuals
        ${SPHINX_HTML_DIR} )
