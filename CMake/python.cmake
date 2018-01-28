# Compile python files and copy them into the build directory

find_package(PythonInterp 2.7)

function(py_compile filename src dst)
  message(STATUS "Compiling python file ${f} with ${PYTHON_EXECUTABLE} -m py_compile ${src}/${filename}")
  execute_process(COMMAND ${PYTHON_EXECUTABLE} -m py_compile ${src}/${filename})
  file(MAKE_DIRECTORY "${dst}")
  if(NOT EXISTS "${dst}/${filename}c")
    file(REMOVE "${dst}/${filename}c")
  endif()
  file(RENAME "${src}/${filename}c" "${dst}/${filename}c")
endfunction()

py_compile(schema_examples.py "${CMAKE_SOURCE_DIR}/drivers/schema_examples/" "${CMAKE_BINARY_DIR}/drivers/schema_examples/")
py_compile(diva_system.py "${CMAKE_SOURCE_DIR}/drivers/system_script/" "${CMAKE_BINARY_DIR}/drivers/system_script/")
