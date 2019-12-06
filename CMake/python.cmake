# Compile python files and copy them into the build directory

if(DIVA_PYTHON_MAJOR_VERSION STREQUAL "2")
  find_package(PythonInterp 2)
elseif(DIVA_PYTHON_MAJOR_VERSION STREQUAL "3")
  find_package(PythonInterp 3)
else()
  find_package(PythonInterp)
endif()

function(py_compile filename rel_path)
  message(STATUS "Compiling python file ${f} with ${PYTHON_EXECUTABLE} -m py_compile ${SOURCE_DIR}/${rel_path}/${filename}")
  execute_process(COMMAND ${PYTHON_EXECUTABLE} -m py_compile ${SOURCE_DIR}/${rel_path}/${filename})
  file(MAKE_DIRECTORY "${BINARY_DIR}/${rel_path}")
  if(EXISTS "${BINARY_DIR}/${rel_path}/${filename}c")
    file(REMOVE "${BINARY_DIR}/${rel_path}/${filename}c")
  endif()
  get_filename_component(basename "${filename}" NAME_WE)
  file(RENAME "${SOURCE_DIR}/${rel_path}/__pycache__/${basename}.cpython-35.pyc" "${BINARY_DIR}/${rel_path}/${filename}c")
endfunction()

py_compile(schema_examples.py "drivers/schema_examples")
py_compile(diva_system.py "drivers/system_script")
