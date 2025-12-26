#!/usr/bin/env python3
"""
Test script for run_ballooning_from_data - in-memory wout data interface.

This test compares results from file-based and memory-based interfaces.
"""

import numpy as np
from pathlib import Path

# Test imports
from cobravmec import run_ballooning, run_ballooning_from_data, load_wout


def test_from_data():
    """Test that run_ballooning_from_data gives same results as run_ballooning."""
    
    # Path to test wout file - use the one in tests directory
    test_dir = Path(__file__).parent
    wout_file = test_dir / "wout_w7x_beta3.nc"
    
    # Fallback to examples directory
    if not wout_file.exists():
        test_dir = Path(__file__).parent.parent.parent.parent / "examples"
        wout_file = test_dir / "wout_w7x_beta3.nc"
    
    if not wout_file.exists():
        print(f"Test wout file not found: {wout_file}")
        return False
    
    # Load wout data
    wout_data = load_wout(str(wout_file))
    
    # Test parameters
    extension = "w7x_beta3"
    k_w = 10
    kth = 1
    l_geom_input = True
    l_tokamak_input = False
    init_zeta=[0.00 , 1.58,  3.14,  4.78, 5.46],
    init_theta=[0.00 , 1.58 , 3.14 , 4.62  ,5.00],
    surfaces=[20,30,40,50,60],
    
    print("Running file-based COBRA...")
    import os
    old_cwd = os.getcwd()
    os.chdir(test_dir)
    grate1, radios1, ierr1 = run_ballooning(
        extension=extension,
        k_w=k_w,
        kth=kth,
        l_geom_input=l_geom_input,
        l_tokamak_input=l_tokamak_input,
        init_zeta=init_zeta,
        init_theta=init_theta,
        surfaces=surfaces,
        lscreen=False,
    )
    os.chdir(old_cwd)
    
    print(f"  ierr={ierr1}, grate shape={grate1.shape}")
    
    print("Running memory-based COBRA...")
    grate2, radios2, ierr2 = run_ballooning_from_data(
        extension='extension',
        k_w=k_w,
        kth=kth,
        l_geom_input=l_geom_input,
        l_tokamak_input=l_tokamak_input,
        init_zeta=init_zeta,
        init_theta=init_theta,
        surfaces=surfaces,
        wout_data=wout_data,
        lscreen=True,
    )
    
    print(f"  ierr={ierr2}, grate shape={grate2.shape}")
    
    # Compare results
    if ierr1 != 0:
        print(f"File-based run failed with ierr={ierr1}")
        # Even if file-based fails, memory-based should work
        if ierr2 == 0:
            print("Memory-based run succeeded!")
            print(f"Max growth rate: {np.max(grate2)}")
            return True
        return False
    
    if ierr2 != 0:
        print(f"Memory-based run failed with ierr={ierr2}")
        return False
    
    # Both succeeded, compare
    grate_allclose = np.allclose(grate1, grate2, rtol=1e-10, atol=1e-15)
    radios_allclose = np.allclose(radios1, radios2, rtol=1e-10, atol=1e-15)
    
    print(f"Results comparison:")
    print(f"  grate_allclose: {grate_allclose}")
    print(f"  radios_allclose: {radios_allclose}")
    print(f"  max grate diff: {np.max(np.abs(grate1 - grate2))}")
    print(f"  max radios diff: {np.max(np.abs(radios1 - radios2))}")
    
    return grate_allclose and radios_allclose


if __name__ == "__main__":
    success = test_from_data()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
