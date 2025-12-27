from __future__ import print_function, absolute_import, division
import _cobravmec
import f90wrap.runtime
import logging
import numpy

class Cobra_Api(f90wrap.runtime.FortranModule):
    """
    Module cobra_api
    
    
    Defined at \
        /Users/dmcxe/Downloads/pyCOBRAVMEC/pyCOBRAVMEC/python/fortran_src/cobra_api.f90 \
        lines 1-442
    
    """
    @staticmethod
    def cobra_run(extension, k_w_in, kth_in, l_geom_input_in, l_tokamak_input_in, \
        init_zeta_in, init_theta_in, bsurf_in, grate_out, radios_out, \
        lscreen_in=None):
        """
        ierr = cobra_run(extension, k_w_in, kth_in, l_geom_input_in, l_tokamak_input_in, \
            init_zeta_in, init_theta_in, bsurf_in, grate_out, radios_out[, lscreen_in])
        
        
        Defined at \
            /Users/dmcxe/Downloads/pyCOBRAVMEC/pyCOBRAVMEC/python/fortran_src/cobra_api.f90 \
            lines 39-84
        
        Parameters
        ----------
        extension : str
        k_w_in : int
        kth_in : int
        l_geom_input_in : bool
        l_tokamak_input_in : bool
        init_zeta_in : float array
        init_theta_in : float array
        bsurf_in : int array
        grate_out : float array
        radios_out : float array
        lscreen_in : bool
        
        Returns
        -------
        ierr : int
        
        """
        ierr = _cobravmec.f90wrap_cobra_api__cobra_run(extension=extension, \
            k_w_in=k_w_in, kth_in=kth_in, l_geom_input_in=l_geom_input_in, \
            l_tokamak_input_in=l_tokamak_input_in, init_zeta_in=init_zeta_in, \
            init_theta_in=init_theta_in, bsurf_in=bsurf_in, grate_out=grate_out, \
            radios_out=radios_out, lscreen_in=lscreen_in)
        return ierr
    
    @staticmethod
    def cobra_cleanup():
        """
        cobra_cleanup()
        
        
        Defined at \
            /Users/dmcxe/Downloads/pyCOBRAVMEC/pyCOBRAVMEC/python/fortran_src/cobra_api.f90 \
            lines 174-175
        
        
        """
        _cobravmec.f90wrap_cobra_api__cobra_cleanup()
    
    @staticmethod
    def cobra_deallocate():
        """
        cobra_deallocate()
        
        
        Defined at \
            /Users/dmcxe/Downloads/pyCOBRAVMEC/pyCOBRAVMEC/python/fortran_src/cobra_api.f90 \
            lines 177-223
        
        
        """
        _cobravmec.f90wrap_cobra_api__cobra_deallocate()
    
    @staticmethod
    def cobra_run_from_data(extension, k_w_in, kth_in, l_geom_input_in, \
        l_tokamak_input_in, init_zeta_in, init_theta_in, bsurf_in, grate_out, \
        radios_out, ns_in, nfp_in, mnmax_in, mnmax_nyq_in, aspect_in, rmax_in, \
        rmin_in, betaxis_in, lasym_in, version_in, iotas_in, pres_in, phip_in, \
        dmerc_in, xm_in, xn_in, xm_nyq_in, xn_nyq_in, rmnc_in, zmns_in, lmns_in, \
        bmnc_in, bsupumnc_in, bsupvmnc_in, lscreen_in=None):
        """
        ierr = cobra_run_from_data(extension, k_w_in, kth_in, l_geom_input_in, \
            l_tokamak_input_in, init_zeta_in, init_theta_in, bsurf_in, grate_out, \
            radios_out, ns_in, nfp_in, mnmax_in, mnmax_nyq_in, aspect_in, rmax_in, \
            rmin_in, betaxis_in, lasym_in, version_in, iotas_in, pres_in, phip_in, \
            dmerc_in, xm_in, xn_in, xm_nyq_in, xn_nyq_in, rmnc_in, zmns_in, lmns_in, \
            bmnc_in, bsupumnc_in, bsupvmnc_in[, lscreen_in])
        
        
        Defined at \
            /Users/dmcxe/Downloads/pyCOBRAVMEC/pyCOBRAVMEC/python/fortran_src/cobra_api.f90 \
            lines 273-330
        
        Parameters
        ----------
        extension : str
        k_w_in : int
        kth_in : int
        l_geom_input_in : bool
        l_tokamak_input_in : bool
        init_zeta_in : float array
        init_theta_in : float array
        bsurf_in : int array
        grate_out : float array
        radios_out : float array
        ns_in : int
        nfp_in : int
        mnmax_in : int
        mnmax_nyq_in : int
        aspect_in : float
        rmax_in : float
        rmin_in : float
        betaxis_in : float
        lasym_in : bool
        version_in : float
        iotas_in : float array
        pres_in : float array
        phip_in : float array
        dmerc_in : float array
        xm_in : float array
        xn_in : float array
        xm_nyq_in : float array
        xn_nyq_in : float array
        rmnc_in : float array
        zmns_in : float array
        lmns_in : float array
        bmnc_in : float array
        bsupumnc_in : float array
        bsupvmnc_in : float array
        lscreen_in : bool
        
        Returns
        -------
        ierr : int
        
        """
        ierr = _cobravmec.f90wrap_cobra_api__cobra_run_from_data(extension=extension, \
            k_w_in=k_w_in, kth_in=kth_in, l_geom_input_in=l_geom_input_in, \
            l_tokamak_input_in=l_tokamak_input_in, init_zeta_in=init_zeta_in, \
            init_theta_in=init_theta_in, bsurf_in=bsurf_in, grate_out=grate_out, \
            radios_out=radios_out, ns_in=ns_in, nfp_in=nfp_in, mnmax_in=mnmax_in, \
            mnmax_nyq_in=mnmax_nyq_in, aspect_in=aspect_in, rmax_in=rmax_in, \
            rmin_in=rmin_in, betaxis_in=betaxis_in, lasym_in=lasym_in, \
            version_in=version_in, iotas_in=iotas_in, pres_in=pres_in, phip_in=phip_in, \
            dmerc_in=dmerc_in, xm_in=xm_in, xn_in=xn_in, xm_nyq_in=xm_nyq_in, \
            xn_nyq_in=xn_nyq_in, rmnc_in=rmnc_in, zmns_in=zmns_in, lmns_in=lmns_in, \
            bmnc_in=bmnc_in, bsupumnc_in=bsupumnc_in, bsupvmnc_in=bsupvmnc_in, \
            lscreen_in=lscreen_in)
        return ierr
    
    _dt_array_initialisers = []
    

cobra_api = Cobra_Api()

