from astropy.table import QTable
import astropy.units as u
import numpy as np

from coconut import activities
from coconut.gmapping import GMapping


def test_work_footprint():
    work_time = [35, 28] * u.h
    country = ["FR" for _ in range(len(work_time))]
    t = QTable([work_time, country], names=["work_time", "country"])
    defaults = activities.defaults | {"weight_factor": 1}
    m = GMapping(t, defaults=defaults)
    f = activities.eval_work_footprint(m)
    total = f.total.to(u.kg)  # type: ignore
    print(total)
    assert total > 0  # type: ignore


def test_compute_footprint():
    cpu = [1000, 2000] * u.h
    gpu = [100, 0] * u.h
    pue = [2, 1.2]
    mix = [44.18, 287.53] * u.g / u.kW / u.h
    t = QTable(
        [cpu, gpu, pue, mix],
        names=["cpu_load", "gpu_load", "PUE", "electric_mix"],
    )
    defaults = activities.defaults | {
        "cpu_power_draw": activities.defaults["laptop_power_draw"],
        "cpu_manufacturing_carbon_intensity": activities.defaults[
            "laptop_manufacturing_carbon_intensity"
        ],
        "gpu_power_draw": activities.defaults["laptop_power_draw"] * 100,
        "gpu_manufacturing_carbon_intensity": activities.defaults[
            "laptop_manufacturing_carbon_intensity"
        ]
        * 1000,
    }
    m = GMapping(t, defaults=defaults, na=np.nan, is_na="nan")
    f = activities.eval_compute_footprint(m)
    total = f.total.to(u.kg)  # type: ignore
    print(total)
    assert total > 0
