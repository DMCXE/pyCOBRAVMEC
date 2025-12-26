module cobra_api
  use stel_kinds
  use ballooning_data
  use normalize_data
  use readin_data
  use fmesh_quantities
  use general_dimensions
  use read_wout_mod, only: read_wout_deallocate
  implicit none

contains

  subroutine cobra_run(extension, k_w_in, kth_in, l_geom_input_in, l_tokamak_input_in, &
                       init_zeta_in, init_theta_in, bsurf_in, grate_out, radios_out, ierr, &
                       lscreen_in)
    character(len=*), intent(in) :: extension
    integer, intent(in) :: k_w_in, kth_in
    logical, intent(in) :: l_geom_input_in, l_tokamak_input_in
    real(rprec), intent(in) :: init_zeta_in(:)
    real(rprec), intent(in) :: init_theta_in(:)
    integer, intent(in) :: bsurf_in(:)
    real(rprec), intent(out) :: grate_out(size(bsurf_in), size(init_theta_in), size(init_zeta_in))
    real(rprec), intent(out) :: radios_out(size(bsurf_in))
    integer, intent(out) :: ierr
    logical, intent(in), optional :: lscreen_in

    real(rprec), allocatable :: grate_tmp(:,:,:)
    real(rprec), allocatable :: radios_tmp(:)
    integer :: nsurf
    integer :: i, idx

    nsurf = size(bsurf_in)

    call cobra_run_alloc(extension, k_w_in, kth_in, l_geom_input_in, l_tokamak_input_in, &
                         init_zeta_in, init_theta_in, bsurf_in, grate_tmp, radios_tmp, ierr, &
                         lscreen_in)

    grate_out = 0._rprec
    radios_out = 0._rprec

    if (ierr .ne. 0) then
      if (allocated(grate_tmp)) deallocate(grate_tmp)
      if (allocated(radios_tmp)) deallocate(radios_tmp)
      return
    end if

    if (.not. allocated(radios_tmp)) return

    if (size(radios_tmp) .eq. nsurf) then
      grate_out = grate_tmp
      radios_out = radios_tmp
    else
      idx = 0
      do i = 1, nsurf
        if (bsurf_in(i) .gt. 1) then
          idx = idx + 1
          if (idx .le. size(radios_tmp)) then
            radios_out(i) = radios_tmp(idx)
            grate_out(i, :, :) = grate_tmp(idx, :, :)
          end if
        end if
      end do
    end if

    deallocate(grate_tmp)
    deallocate(radios_tmp)
  end subroutine cobra_run

  subroutine cobra_run_alloc(extension, k_w_in, kth_in, l_geom_input_in, l_tokamak_input_in, &
                             init_zeta_in, init_theta_in, bsurf_in, grate_out, radios_out, ierr, &
                             lscreen_in)
    character(len=*), intent(in) :: extension
    integer, intent(in) :: k_w_in, kth_in
    logical, intent(in) :: l_geom_input_in, l_tokamak_input_in
    real(rprec), intent(in) :: init_zeta_in(:)
    real(rprec), intent(in) :: init_theta_in(:)
    integer, intent(in) :: bsurf_in(:)
    real(rprec), allocatable, intent(out) :: grate_out(:,:,:)
    real(rprec), allocatable, intent(out) :: radios_out(:)
    integer, intent(out) :: ierr
    logical, intent(in), optional :: lscreen_in

    integer :: ntheta, nzeta, nsurf, nlis
    integer :: i, j
    integer, allocatable :: in_surf(:), in_idx(:), bsurf(:)
    real(rprec), allocatable :: grate(:)

    ierr = 0

    call cobra_deallocate()

    k_w = k_w_in
    kth = kth_in
    l_geom_input = l_geom_input_in
    l_tokamak_input = l_tokamak_input_in
    if (present(lscreen_in)) then
      lscreen = lscreen_in
    else
      lscreen = .false.
    end if

    ntheta = size(init_theta_in)
    nzeta = size(init_zeta_in)
    nsurf = size(bsurf_in)

    if (allocated(init_theta_v)) deallocate(init_theta_v)
    if (allocated(init_zeta_v)) deallocate(init_zeta_v)
    allocate(init_theta_v(ntheta))
    allocate(init_zeta_v(nzeta))
    init_theta_v = init_theta_in
    init_zeta_v = init_zeta_in

    allocate(in_surf(nsurf), in_idx(nsurf))
    in_surf = bsurf_in

    nlis = 0
    do i = 1, nsurf
      if (in_surf(i) .gt. 1) then
        nlis = nlis + 1
        in_idx(nlis) = in_surf(i)
      end if
    end do

    allocate(bsurf(nlis))
    if (nlis .gt. 0) then
      bsurf(1:nlis) = in_idx(1:nlis)
    end if

    call order_input(extension, nlis, bsurf, ierr)
    if (ierr .ne. 0) then
      call cobra_deallocate()
      allocate(grate_out(0, 0, 0))
      allocate(radios_out(0))
      return
    end if

    allocate(grate(ns_cob))
    if (allocated(radios)) deallocate(radios)
    allocate(radios(ns_cob))

    allocate(grate_out(nlis, ntheta, nzeta))
    allocate(radios_out(nlis))

    do j = 1, ntheta
      do i = 1, nzeta
        if (l_geom_input) then
          init_zeta = mod(init_zeta_v(i), 360._dp)
          init_theta = mod(init_theta_v(j), 360._dp)
        else
          if (l_tokamak_input) then
            init_alpha_tok = mod(init_zeta_v(i), 360._dp)
            init_thetak_tok = mod(init_theta_v(j), 360._dp)
          else
            init_zetak_st = mod(init_zeta_v(i), 360._dp)
            init_alpha_st = mod(init_theta_v(j), 360._dp)
          end if
        end if

        lfail_balloon = .false.
        call get_ballooning_grate(grate)
        if (nlis .gt. 0) then
          grate_out(:, j, i) = grate(bsurf)
        end if
      end do
    end do

    if (nlis .gt. 0) then
      radios_out = radios(bsurf)
    end if

    deallocate(grate)
    deallocate(in_surf, in_idx, bsurf)
    call cobra_deallocate()
  end subroutine cobra_run_alloc

  subroutine cobra_cleanup()
    call cobra_deallocate()
  end subroutine cobra_cleanup

  subroutine cobra_deallocate()
    call read_wout_deallocate

    if (allocated(init_theta_v)) deallocate(init_theta_v)
    if (allocated(init_zeta_v)) deallocate(init_zeta_v)

    if (allocated(list)) deallocate(list)
    if (allocated(hiota)) deallocate(hiota)
    if (allocated(hphip)) deallocate(hphip)
    if (allocated(hpres)) deallocate(hpres)
    if (allocated(xn_v)) deallocate(xn_v)
    if (allocated(xm_v)) deallocate(xm_v)
    if (allocated(xn_vnyq)) deallocate(xn_vnyq)
    if (allocated(xm_vnyq)) deallocate(xm_vnyq)
    if (allocated(lmnsh)) deallocate(lmnsh)
    if (allocated(bmnch)) deallocate(bmnch)
    if (allocated(bsupumnch)) deallocate(bsupumnch)
    if (allocated(bsupvmnch)) deallocate(bsupvmnch)
    if (allocated(lmnch)) deallocate(lmnch)
    if (allocated(bmnsh)) deallocate(bmnsh)
    if (allocated(bsupumnsh)) deallocate(bsupumnsh)
    if (allocated(bsupvmnsh)) deallocate(bsupvmnsh)

    if (allocated(iotaf)) deallocate(iotaf)
    if (allocated(phipf)) deallocate(phipf)
    if (allocated(presf)) deallocate(presf)
    if (allocated(mercierf)) deallocate(mercierf)
    if (allocated(iotapf)) deallocate(iotapf)
    if (allocated(prespf)) deallocate(prespf)
    if (allocated(radios)) deallocate(radios)

    if (allocated(rmncf)) deallocate(rmncf)
    if (allocated(zmnsf)) deallocate(zmnsf)
    if (allocated(lmnsf)) deallocate(lmnsf)
    if (allocated(bmncf)) deallocate(bmncf)
    if (allocated(bsupvmncf)) deallocate(bsupvmncf)
    if (allocated(bsupumncf)) deallocate(bsupumncf)
    if (allocated(rmncpf)) deallocate(rmncpf)
    if (allocated(zmnspf)) deallocate(zmnspf)
    if (allocated(lmnspf)) deallocate(lmnspf)
    if (allocated(bmncpf)) deallocate(bmncpf)

    if (allocated(rmnsf)) deallocate(rmnsf)
    if (allocated(zmncf)) deallocate(zmncf)
    if (allocated(lmncf)) deallocate(lmncf)
    if (allocated(bmnsf)) deallocate(bmnsf)
    if (allocated(bsupvmnsf)) deallocate(bsupvmnsf)
    if (allocated(bsupumnsf)) deallocate(bsupumnsf)
    if (allocated(rmnspf)) deallocate(rmnspf)
    if (allocated(zmncpf)) deallocate(zmncpf)
    if (allocated(lmncpf)) deallocate(lmncpf)
    if (allocated(bmnspf)) deallocate(bmnspf)
  end subroutine cobra_deallocate

end module cobra_api
