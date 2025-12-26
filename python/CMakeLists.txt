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

# Disable all RPATH handling to avoid duplicate LC_RPATH issues on macOS
set_target_properties(${f2py_module_name} PROPERTIES
  SKIP_BUILD_RPATH TRUE
  BUILD_WITH_INSTALL_RPATH TRUE
  INSTALL_RPATH ""
  INSTALL_RPATH_USE_LINK_PATH FALSE
)
if (APPLE)
  set_target_properties(${f2py_module_name} PROPERTIES
    MACOSX_RPATH OFF
  )
endif()

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

# Create a Python script to fix duplicate rpaths on macOS (more portable than bash)
if (APPLE)
  set(FIX_RPATH_SCRIPT "${CMAKE_CURRENT_BINARY_DIR}/fix_rpath.py")
  file(WRITE ${FIX_RPATH_SCRIPT} "#!/usr/bin/env python3
import subprocess
import sys
import os

def fix_duplicate_rpaths(so_file):
    if not os.path.exists(so_file):
        return
    try:
        result = subprocess.run(['otool', '-l', so_file], capture_output=True, text=True, check=True)
        lines = result.stdout.split('\\n')
        rpaths = []
        for i, line in enumerate(lines):
            if 'cmd LC_RPATH' in line:
                for j in range(i + 1, min(i + 5, len(lines))):
                    if 'path ' in lines[j]:
                        path = lines[j].split('path ')[1].split(' (offset')[0].strip()
                        rpaths.append(path)
                        break
        seen = set()
        for rpath in rpaths:
            if rpath in seen:
                subprocess.run(['install_name_tool', '-delete_rpath', rpath, so_file],
                               capture_output=True, check=False)
                print(f'Removed duplicate RPATH: {rpath}')
            else:
                seen.add(rpath)
    except Exception as e:
        print(f'Warning: Failed to fix rpaths: {e}')

if __name__ == '__main__':
    if len(sys.argv) > 1:
        fix_duplicate_rpaths(sys.argv[1])
")
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

# Fix duplicate rpaths after build on macOS
if (APPLE)
  add_custom_command(TARGET ${f2py_module_name} POST_BUILD
    COMMAND ${Python_EXECUTABLE} ${FIX_RPATH_SCRIPT} "$<TARGET_FILE:${f2py_module_name}>"
    COMMENT "Fixing duplicate RPATH entries"
  )
endif()

install(FILES ${python_mod_file} DESTINATION python/cobravmec)
install(FILES ${CMAKE_CURRENT_SOURCE_DIR}/cobravmec/__init__.py
              ${CMAKE_CURRENT_SOURCE_DIR}/cobravmec/api.py
        DESTINATION python/cobravmec)
install(TARGETS ${f2py_module_name} DESTINATION python/cobravmec)
