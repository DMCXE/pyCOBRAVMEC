set(cobravmec_sources
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/ballooning_data.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/EQL.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/coeffs.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/obtain_theta.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/INP.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/polint.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/CP.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/general_dimensions.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/normalize_data.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/fmesh_quantities.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/get_lambda.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/obtain_field_line.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/variat_eig_full.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/TVAL.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/obtain_zeta.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/order_input.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/geteigm.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/STM.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/get_ballooning_grate.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/readin_data.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/TVECT.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/getmatrix.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/summod.f
  ${CMAKE_CURRENT_SOURCE_DIR}/Sources/summodosd.f
)

add_library(cobravmec STATIC ${cobravmec_sources})
if (SKBUILD)
  set_target_properties(cobravmec PROPERTIES POSITION_INDEPENDENT_CODE ON)
endif()
set_target_properties(cobravmec PROPERTIES Fortran_MODULE_DIRECTORY ${CMAKE_Fortran_MODULE_DIRECTORY}/cobravmec)
target_include_directories(cobravmec PUBLIC
  ${CMAKE_Fortran_MODULE_DIRECTORY}/cobravmec
  ${CMAKE_Fortran_MODULE_DIRECTORY}/libstell_mini
)
target_link_libraries(cobravmec PUBLIC libstell_mini)

add_executable(xcobravmec ${CMAKE_CURRENT_SOURCE_DIR}/Sources/cobra.f)
target_link_libraries(xcobravmec cobravmec)

install(TARGETS xcobravmec RUNTIME DESTINATION bin)
install(TARGETS cobravmec ARCHIVE DESTINATION lib)
