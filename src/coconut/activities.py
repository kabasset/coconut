# SPDX-FileCopyrightText: Copyright (C) 2025-2026, Antoine Basset (CNES) and contributors
# SPDX-PackageSourceInfo: https://gitlab.esa.int/lisa-sgs/sys/sandbox/timeo
# SPDX-License-Identifier: Apache-2.0

from typing import Callable

import astropy.units as u

from timeo.ctree import CTree
from timeo.gmapping import GMapping

defaults = {
    "laptop_power_draw": 50 * u.W,  # laptop + 28" screen + docking station
    "laptop_manufacturing_carbon_intensity": 17.5 * u.g / u.h,
    "screen_manufacturing_carbon_intensity": 25 * u.g / u.h,
    "electric_mix": 250 * u.g / u.kW / u.h,
}


def eval_work_footprint(
    workers: GMapping,
    electric_mix: GMapping = GMapping({}, na=defaults["electric_mix"]),
) -> CTree:

    res = {}
    res["Laptop"] = {}

    workers.bind("electric_mix", lambda: [electric_mix[w["country"]] for w in workers])

    res["Laptop"]["Usage"] = sum(
        workers["work_time"]
        * workers["laptop_power_draw"]
        * workers["electric_mix"]
        * workers["weight_factor"]
    )
    res["Laptop"]["Manufacturing"] = sum(
        workers["work_time"]
        * (
            workers["laptop_manufacturing_carbon_intensity"]
            + workers["screen_manufacturing_carbon_intensity"]
        )
        * workers["weight_factor"]
    )

    return CTree(res, key="Total")


def eval_compute_footprint(resources: GMapping) -> CTree:

    res = {}
    res["CPU"] = {}
    res["GPU"] = {}

    res["CPU"]["Usage"] = sum(
        resources["cpu_load"]
        * resources["cpu_power_draw"]
        * resources["PUE"]
        * resources["electric_mix"],
    )
    res["CPU"]["Manufacturing"] = sum(
        resources["cpu_load"] * resources["cpu_manufacturing_carbon_intensity"]
    )

    res["GPU"]["Usage"] = sum(
        resources["gpu_load"]
        * resources["gpu_power_draw"]
        * resources["PUE"]
        * resources["electric_mix"]
    )
    res["GPU"]["Manufacturing"] = sum(
        resources["gpu_load"] * resources["gpu_manufacturing_carbon_intensity"]
    )

    return CTree(res, key="Total")


def eval_footprint_hierarchy(
    evaluator: Callable, resources: dict, *args, **kwargs
) -> CTree:
    """
    Evaluate a hierarchy of footprint:
    for each table in ``resources``, evaluate the cumulative tree with ``evaluator``,
    then structure the results according to the input hierarchy.

    Args:
        evaluator: The footprint evaluation function applied to each table.
        resources: The tree of resource tables.
        args, kwargs: Arguments forwarded to the evaluation function.
    """
    res = {}
    for k, v in resources.items():
        if isinstance(v, dict):
            res[k] = eval_footprint_hierarchy(evaluator, v, *args, **kwargs).to_dict()
        else:
            res[k] = evaluator(v, *args, **kwargs).to_dict()
    return CTree(res, key="Total")
