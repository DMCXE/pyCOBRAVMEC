from cobravmec import CobraRunner, CobraPlotter
import numpy as np

def load_cobra_grate(path, surfaces, ntheta, nzeta):
    surfaces = np.asarray(surfaces, dtype=int)
    nlis = surfaces.size
    grate = np.zeros((nlis, ntheta, nzeta), dtype=float)
    radios = np.zeros(nlis, dtype=float)
    with open(path, "r", encoding="ascii") as handle:
        lines = iter(handle.readlines())
        for j in range(ntheta):
            for i in range(nzeta):
                header = next(lines).split()
                nlis_line = int(header[2])
                if nlis_line != nlis:
                    raise ValueError(f"Mismatch nlis {nlis_line} vs expected {nlis}")
                for s_idx in range(nlis):
                    surf_line = next(lines).split()
                    surf = int(surf_line[0])
                    radio = float(surf_line[1])
                    grate_val = float(surf_line[2])
                    if surf != surfaces[s_idx]:
                        raise ValueError(
                            f"Surface order mismatch at block (theta={j}, zeta={i}): {surf} vs {surfaces[s_idx]}"
                        )
                    if j == 0 and i == 0:
                        radios[s_idx] = radio
                    else:
                        if not np.isclose(radios[s_idx], radio):
                            raise ValueError(
                                f"Radio mismatch for surface {surf}: {radio} vs {radios[s_idx]} at block (theta={j}, zeta={i})"
                            )
                    grate[s_idx, j, i] = grate_val
    return grate, radios


runner = CobraRunner(
    k_w=10,
    kth=1,
    l_geom_input=True,
    l_tokamak_input=False,
    init_zeta=[0.00 , 1.58,  3.14,  4.78, 5.46],
    init_theta=[0.00 , 1.58 , 3.14 , 4.62  ,5.00],
    surfaces=[20,30,40,50,60],
    lscreen=True
)
results = runner.run(extension="w7x_beta3")
runner.write_output()  # uses stored configuration/results

file_grate, file_radios = load_cobra_grate(
    "cobra_grate.w7x_beta3",
    surfaces=runner.surfaces,
    ntheta=len(runner.init_theta),
    nzeta=len(runner.init_zeta),
)
max_abs_diff = np.max(np.abs(results.grate - file_grate))
radios_diff = np.max(np.abs(results.radios - file_radios))
print("grate shape", results.grate.shape)
print("max_abs_diff", max_abs_diff)
print("radios_diff", radios_diff)
print("grate_allclose", np.allclose(results.grate, file_grate, atol=1e-9))
print("radios_allclose", np.allclose(results.radios, file_radios, atol=1e-9))

plotter = CobraPlotter(results=results)
plotter.plot_max_growth()
plotter.plot_growth_map(surface=60)
