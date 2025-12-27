!> @brief Initialize COBRA from in-memory wout data instead of reading from file
!> @details This subroutine provides an alternative to order_input that accepts
!>          wout data directly from memory, avoiding file I/O. This is useful
!>          for integration with Python wrappers where wout data is already
!>          available in memory (e.g., from simsopt's Vmec object).
!>
!> @param[in] extension      File extension for output file naming (e.g., "test_case")
!> @param[in] nl             Number of surfaces to analyze
!> @param[in] bsurf          Array of surface indices
!> @param[out] ierr          Error code (0 = success)
!> @param[in] ns_in          Number of radial surfaces
!> @param[in] nfp_in         Number of field periods
!> @param[in] mnmax_in       Number of Fourier modes
!> @param[in] mnmax_nyq_in   Number of Nyquist Fourier modes
!> @param[in] aspect_in      Aspect ratio
!> @param[in] rmax_in        Maximum R
!> @param[in] rmin_in        Minimum R  
!> @param[in] betaxis_in     Beta on axis
!> @param[in] lasym_in       Asymmetry flag
!> @param[in] version_in     VMEC version number
!> @param[in] iotas_in       Iota on half mesh (ns)
!> @param[in] pres_in        Pressure on half mesh (ns)
!> @param[in] phip_in        Toroidal flux derivative (ns)
!> @param[in] Dmerc_in       Mercier criterion (ns)
!> @param[in] xm_in          Poloidal mode numbers (mnmax)
!> @param[in] xn_in          Toroidal mode numbers (mnmax)
!> @param[in] xm_nyq_in      Nyquist poloidal mode numbers (mnmax_nyq)
!> @param[in] xn_nyq_in      Nyquist toroidal mode numbers (mnmax_nyq)
!> @param[in] rmnc_in        R cosine coefficients (mnmax, ns)
!> @param[in] zmns_in        Z sine coefficients (mnmax, ns)
!> @param[in] lmns_in        Lambda sine coefficients (mnmax, ns)
!> @param[in] bmnc_in        |B| cosine coefficients (mnmax_nyq, ns)
!> @param[in] bsupumnc_in    B^u cosine coefficients (mnmax_nyq, ns)
!> @param[in] bsupvmnc_in    B^v cosine coefficients (mnmax_nyq, ns)
!> @param[in] rmns_in        R sine coefficients for asymmetric (optional)
!> @param[in] zmnc_in        Z cosine coefficients for asymmetric (optional)
!> @param[in] lmnc_in        Lambda cosine coefficients for asymmetric (optional)
!> @param[in] bmns_in        |B| sine coefficients for asymmetric (optional)
!> @param[in] bsupumns_in    B^u sine coefficients for asymmetric (optional)
!> @param[in] bsupvmns_in    B^v sine coefficients for asymmetric (optional)

subroutine order_input_from_data(extension, nl, bsurf, ierr, &
    ns_in, nfp_in, mnmax_in, mnmax_nyq_in, &
    aspect_in, rmax_in, rmin_in, betaxis_in, lasym_in, version_in, &
    iotas_in, pres_in, phip_in, Dmerc_in, &
    xm_in, xn_in, xm_nyq_in, xn_nyq_in, &
    rmnc_in, zmns_in, lmns_in, bmnc_in, bsupumnc_in, bsupvmnc_in, &
    rmns_in, zmnc_in, lmnc_in, bmns_in, bsupumns_in, bsupvmns_in)

  use stel_kinds
  use normalize_data
  use readin_data
  use fmesh_quantities, only: rmncf, zmnsf, mercierf, rmnsf, zmncf
  use vparams, only: mu0
  use general_dimensions
  implicit none

  !-----------------------------------------------
  !   D u m m y   A r g u m e n t s
  !-----------------------------------------------
  character(len=*), intent(in) :: extension
  integer, intent(in) :: nl
  integer, intent(out) :: ierr
  integer, dimension(nl), intent(in) :: bsurf

  ! Scalar inputs from wout
  integer, intent(in) :: ns_in, nfp_in, mnmax_in, mnmax_nyq_in
  real(rprec), intent(in) :: aspect_in, rmax_in, rmin_in, betaxis_in, version_in
  logical, intent(in) :: lasym_in

  ! 1D array inputs from wout
  real(rprec), dimension(ns_in), intent(in) :: iotas_in, pres_in, phip_in, Dmerc_in
  real(rprec), dimension(mnmax_in), intent(in) :: xm_in, xn_in
  real(rprec), dimension(mnmax_nyq_in), intent(in) :: xm_nyq_in, xn_nyq_in

  ! 2D array inputs from wout (symmetric)
  real(rprec), dimension(mnmax_in, ns_in), intent(in) :: rmnc_in, zmns_in, lmns_in
  real(rprec), dimension(mnmax_nyq_in, ns_in), intent(in) :: bmnc_in, bsupumnc_in, bsupvmnc_in

  ! 2D array inputs from wout (asymmetric, optional)
  real(rprec), dimension(mnmax_in, ns_in), intent(in), optional :: rmns_in, zmnc_in, lmnc_in
  real(rprec), dimension(mnmax_nyq_in, ns_in), intent(in), optional :: bmns_in, bsupumns_in, bsupvmns_in

  !-----------------------------------------------
  !   L o c a l   V a r i a b l e s
  !-----------------------------------------------
  integer :: lk, i, j, k
  integer, dimension(:), allocatable :: plist
  real(rprec) :: r0max_v, r0min_v, betaxis_v, aspect_v
  logical, allocatable, dimension(:) :: lballoon

  !-----------------------------------------------
  ierr = 0

  ! Store scalar values
  nfp_v = nfp_in
  ns_cob = ns_in
  aspect_v = aspect_in
  r0max_v = rmax_in
  r0min_v = rmin_in
  betaxis_v = betaxis_in
  mnmax_v = mnmax_in
  mnmax_vnyq = mnmax_nyq_in
  lasym_v = lasym_in

  ! Allocate and fill half-mesh arrays
  k = 0
  if (.not. allocated(hiota)) allocate(hiota(ns_cob), stat=k)
  if (k .ne. 0) stop 'Allocation error 1 in order_input_from_data'
  if (.not. allocated(hpres)) allocate(hpres(ns_cob), stat=k)
  if (k .ne. 0) stop 'Allocation error 1 in order_input_from_data'
  if (.not. allocated(hphip)) allocate(hphip(ns_cob), stat=k)
  if (k .ne. 0) stop 'Allocation error 1 in order_input_from_data'
  if (.not. allocated(mercierf)) allocate(mercierf(ns_cob), stat=k)
  if (k .ne. 0) stop 'Allocation error 1 in order_input_from_data'

  hiota = iotas_in(1:ns_cob)
  if (version_in .gt. 6.0_rprec) then
    hpres = mu0 * pres_in(1:ns_cob)
  else
    hpres = pres_in(1:ns_cob)
  end if
  hphip = phip_in(1:ns_cob)
  mercierf = Dmerc_in(1:ns_cob)

  ! Compute normalization parameters
  r0 = (r0max_v + r0min_v) / 2
  amin = r0 / aspect_v
  beta0 = betaxis_v
  if (beta0 .le. 0._rprec) then
    beta0 = epsilon(beta0)
    hpres = beta0 * (/(1 - (j - 1) / real(ns_cob - 1, rprec), j = 1, ns_cob)/)
  end if
  b0_v = sqrt((2._dp / beta0) * (1.5_dp * hpres(2) - 0.5_dp * hpres(3)))

  ! Allocate and fill mode number arrays
  k = 0
  if (.not. allocated(xm_v)) allocate(xm_v(mnmax_v), stat=k)
  if (k .ne. 0) stop 'Allocation error 2 in order_input_from_data'
  if (.not. allocated(xn_v)) allocate(xn_v(mnmax_v), stat=k)
  if (k .ne. 0) stop 'Allocation error 2 in order_input_from_data'
  if (.not. allocated(xm_vnyq)) allocate(xm_vnyq(mnmax_vnyq), stat=k)
  if (k .ne. 0) stop 'Allocation error 2 in order_input_from_data'
  if (.not. allocated(xn_vnyq)) allocate(xn_vnyq(mnmax_vnyq), stat=k)
  if (k .ne. 0) stop 'Allocation error 2 in order_input_from_data'
  if (.not. allocated(plist)) allocate(plist(ns_cob), stat=k)
  if (k .ne. 0) stop 'Allocation error 2 in order_input_from_data'

  xm_v = xm_in(1:mnmax_v)
  xn_v = xn_in(1:mnmax_v)
  xm_vnyq = xm_nyq_in(1:mnmax_vnyq)
  xn_vnyq = xn_nyq_in(1:mnmax_vnyq)

  mndim = ns_cob * mnmax_v
  mndim_nyq = ns_cob * mnmax_vnyq

  ! Allocate Fourier coefficient arrays (symmetric)
  k = 0
  if (.not. allocated(rmncf)) allocate(rmncf(mndim), stat=k)
  if (k .ne. 0) stop 'Allocation error 3 in order_input_from_data'
  if (.not. allocated(zmnsf)) allocate(zmnsf(mndim), stat=k)
  if (k .ne. 0) stop 'Allocation error 3 in order_input_from_data'
  if (.not. allocated(lmnsh)) allocate(lmnsh(mndim), stat=k)
  if (k .ne. 0) stop 'Allocation error 3 in order_input_from_data'
  if (.not. allocated(bmnch)) allocate(bmnch(mndim_nyq), stat=k)
  if (k .ne. 0) stop 'Allocation error 3 in order_input_from_data'
  if (.not. allocated(bsupumnch)) allocate(bsupumnch(mndim_nyq), stat=k)
  if (k .ne. 0) stop 'Allocation error 3 in order_input_from_data'
  if (.not. allocated(bsupvmnch)) allocate(bsupvmnch(mndim_nyq), stat=k)
  if (k .ne. 0) stop 'Allocation error 3 in order_input_from_data'

  zmnsf = 0
  rmncf = 0
  lmnsh = 0
  bmnch = 0
  bsupvmnch = 0
  bsupumnch = 0

  ! Allocate asymmetric arrays if needed
  if (lasym_v) then
    k = 0
    if (.not. allocated(rmnsf)) allocate(rmnsf(mndim), stat=k)
    if (k .ne. 0) stop 'Allocation error 4 in order_input_from_data'
    if (.not. allocated(zmncf)) allocate(zmncf(mndim), stat=k)
    if (k .ne. 0) stop 'Allocation error 4 in order_input_from_data'
    if (.not. allocated(lmnch)) allocate(lmnch(mndim), stat=k)
    if (k .ne. 0) stop 'Allocation error 4 in order_input_from_data'
    if (.not. allocated(bmnsh)) allocate(bmnsh(mndim_nyq), stat=k)
    if (k .ne. 0) stop 'Allocation error 4 in order_input_from_data'
    if (.not. allocated(bsupumnsh)) allocate(bsupumnsh(mndim_nyq), stat=k)
    if (k .ne. 0) stop 'Allocation error 4 in order_input_from_data'
    if (.not. allocated(bsupvmnsh)) allocate(bsupvmnsh(mndim_nyq), stat=k)
    if (k .ne. 0) stop 'Allocation error 4 in order_input_from_data'
    zmncf = 0
    rmnsf = 0
    lmnch = 0
    bmnsh = 0
    bsupvmnsh = 0
    bsupumnsh = 0
  end if

  ! Fill Fourier coefficient arrays (reshape 2D -> 1D)
  do k = 1, ns_cob
    lk = (k - 1) * mnmax_v
    rmncf(lk + 1:lk + mnmax_v) = rmnc_in(1:mnmax_v, k)
    zmnsf(lk + 1:lk + mnmax_v) = zmns_in(1:mnmax_v, k)
    lmnsh(lk + 1:lk + mnmax_v) = lmns_in(1:mnmax_v, k)
    if (lasym_v) then
      if (present(rmns_in)) rmnsf(lk + 1:lk + mnmax_v) = rmns_in(1:mnmax_v, k)
      if (present(zmnc_in)) zmncf(lk + 1:lk + mnmax_v) = zmnc_in(1:mnmax_v, k)
      if (present(lmnc_in)) lmnch(lk + 1:lk + mnmax_v) = lmnc_in(1:mnmax_v, k)
    end if
  end do

  do k = 1, ns_cob
    lk = (k - 1) * mnmax_vnyq
    bmnch(lk + 1:lk + mnmax_vnyq) = bmnc_in(1:mnmax_vnyq, k)
    bsupvmnch(lk + 1:lk + mnmax_vnyq) = bsupvmnc_in(1:mnmax_vnyq, k)
    bsupumnch(lk + 1:lk + mnmax_vnyq) = bsupumnc_in(1:mnmax_vnyq, k)
    if (lasym_v) then
      if (present(bmns_in)) bmnsh(lk + 1:lk + mnmax_vnyq) = bmns_in(1:mnmax_vnyq, k)
      if (present(bsupvmns_in)) bsupvmnsh(lk + 1:lk + mnmax_vnyq) = bsupvmns_in(1:mnmax_vnyq, k)
      if (present(bsupumns_in)) bsupumnsh(lk + 1:lk + mnmax_vnyq) = bsupumns_in(1:mnmax_vnyq, k)
    end if
  end do

  ! Identify wanted surfaces
  allocate(lballoon(ns_cob), stat=k)
  lballoon = .false.
  do i = 1, nl
    lballoon(bsurf(i)) = .true.
  end do

  ! Check for feasibility of ballooning calculation
  nlist = 0
  do i = 2, ns_cob - 1  ! exclude Boundary (i=ns)
    if (lballoon(i)) then
      nlist = nlist + 1
      plist(nlist) = i
    end if
  end do

  ! Store NLIST surfaces where calculation can be done
  if (.not. allocated(list)) allocate(list(nlist), stat=k)
  list(1:nlist) = plist(1:nlist)
  deallocate(plist, lballoon)

end subroutine order_input_from_data
