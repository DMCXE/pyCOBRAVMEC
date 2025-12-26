set(Python_FIND_STRATEGY LOCATION)
find_package(Python REQUIRED COMPONENTS Interpreter Development.Module NumPy)
find_program(F2PY_EXECUTABLE NAMES f2py${PYTHON_VERSION_MAJOR} f2py)
find_package(F90Wrap REQUIRED)
find_package(PythonExtensions REQUIRED)

execute_process(
  COMMAND "${PYTHON_EXECUTABLE}"
  -c "import numpy; print(numpy.get_include())"
  OUTPUT_VARIABLE NumPy_INCLUDE_DIRS
  OUTPUT_STRIP_TRAILING_WHITESPACE
)
execute_process(
  COMMAND "${PYTHON_EXECUTABLE}"
  -c "import numpy.f2py; print(numpy.f2py.get_include())"
  OUTPUT_VARIABLE F2PY_INCLUDE_DIRS
  OUTPUT_STRIP_TRAILING_WHITESPACE
)

set(fortran_src_files ${CMAKE_CURRENT_SOURCE_DIR}/fortran_src/cobra_api.f90)
set(kind_map_file ${CMAKE_CURRENT_SOURCE_DIR}/kind_map)
set(python_mod_name cobravmec)
set(python_mod_file ${CMAKE_CURRENT_BINARY_DIR}/${python_mod_name}.py)

set(f90wrap_output_files
  ${CMAKE_CURRENT_BINARY_DIR}/f90wrap_cobra_api.f90
)

add_custom_command(OUTPUT ${python_mod_file} ${f90wrap_output_files}
  COMMAND "${F90Wrap_EXECUTABLE}" -m "${python_mod_name}" ${fortran_src_files} -k "${kind_map_file}"
  DEPENDS ${fortran_src_files} ${kind_map_file}
  COMMENT "Executing f90wrap for" ${fortran_src_files}
  VERBATIM
)

add_custom_target("${python_mod_name}_pymod"
  DEPENDS ${python_mod_file} ${f90wrap_output_files}
)

set(f2py_module_name "_${python_mod_name}")
set(f2py_module_c "${f2py_module_name}module.c")

add_custom_command(
  OUTPUT "${CMAKE_CURRENT_BINARY_DIR}/${f2py_module_c}"
  COMMAND ${F2PY_EXECUTABLE}
          -m "${f2py_module_name}"
          --build-dir ${CMAKE_CURRENT_BINARY_DIR}
          --lower
          "${f90wrap_output_files}"
  DEPENDS ${fortran_src_files} ${f90wrap_output_files}
  WORKING_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}
  COMMAND_EXPAND_LISTS
)

add_library(${f2py_module_name} MODULE
  "${f2py_module_c}"
  "${F2PY_INCLUDE_DIRS}/fortranobject.c"
  ${fortran_src_files}
  ${f90wrap_output_files}
)

target_include_directories(${f2py_module_name} PUBLIC
  ${F2PY_INCLUDE_DIRS}
  ${NumPy_INCLUDE_DIRS}
  ${PYTHON_INCLUDE_DIRS}
  ${CMAKE_Fortran_MODULE_DIRECTORY}
  ${CMAKE_Fortran_MODULE_DIRECTORY}/cobravmec
  ${CMAKE_Fortran_MODULE_DIRECTORY}/libstell_mini
)

target_link_libraries(${f2py_module_name} cobravmec)
set_target_properties(${f2py_module_name} PROPERTIES SUFFIX "${PYTHON_EXTENSION_MODULE_SUFFIX}")
set_target_properties(${f2py_module_name} PROPERTIES PREFIX "")

if (UNIX)
  if (APPLE)
    set_target_properties(${f2py_module_name} PROPERTIES
      LINK_FLAGS  "-Wl,-dylib,-undefined,dynamic_lookup"
    )
  else()
    set_target_properties(${f2py_module_name} PROPERTIES
      LINK_FLAGS  "-Wl,--allow-shlib-undefined"
    )
  endif()
endif()

add_custom_command(TARGET ${f2py_module_name} POST_BUILD
  COMMAND ${CMAKE_COMMAND} -E copy_if_different
          "$<TARGET_FILE:${f2py_module_name}>"
          "${CMAKE_CURRENT_SOURCE_DIR}/cobravmec"
  COMMAND ${CMAKE_COMMAND} -E copy_if_different
          "${python_mod_file}"
          "${CMAKE_CURRENT_SOURCE_DIR}/cobravmec/cobravmec.py"
  COMMENT "Copying _cobravmec and cobravmec.py into source package for editable use"
)

install(FILES ${python_mod_file} DESTINATION python/cobravmec)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/cobravmec/__init__.py
              ${CMAKE_CURRENT_SOURCE_DIR}/cobravmec/api.py
        DESTINATION python/cobravmec)
install(TARGETS ${f2py_module_name} DESTINATION python/cobravmec)
