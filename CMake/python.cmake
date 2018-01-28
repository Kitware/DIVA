# Compile python files and copy them into the build directory

find_package(PythonInterp 2.7)

function(py_compile filename rel_path)
  message(STATUS "Compiling python file ${f} with ${PYTHON_EXECUTABLE} -m py_compile ${SOURCE_DIR}/${rel_path}/${filename}")
  execute_process(COMMAND ${PYTHON_EXECUTABLE} -m py_compile ${SOURCE_DIR}/${rel_path}/${filename})
  file(MAKE_DIRECTORY "${BINARY_DIR}/${rel_path}")
  if(NOT EXISTS "${BINARY_DIR}/${rel_path}/${filename}c")
    file(REMOVE "${BINARY_DIR}/${rel_path}/${filename}c")
  endif()
  file(RENAME "${SOURCE_DIR}/${rel_path}/${filename}c" "${BINARY_DIR}/${rel_path}/${filename}c")
endfunction()

py_compile(schema_examples.py "drivers/schema_examples/")
py_compile(diva_system.py "drivers/system_script/")
