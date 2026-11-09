# SPDX-FileCopyrightText: Copyright (C) 2025-2026, Antoine Basset (CNES) and contributors
# SPDX-PackageSourceInfo: https://gitlab.esa.int/lisa-sgs/sys/sandbox/timeo
# SPDX-License-Identifier: Apache-2.0

import argparse
from astropy.table import QTable
import astropy.units as u
from pathlib import Path

from timeo import activities
from timeo.logging import logger


def add_parser(subparsers, help):

    parser = subparsers.add_parser(
        "process",
        help=help,
        description=("Compute the carbon footprint of some activities."),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "workdir",
        type=Path,
        help="Working directory, which contains input tables.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default="footprint.json",
        help="Output file path.",
    )

    parser.set_defaults(func=run)


def run(args):
    resources = QTable.read(args.workdir / "resources.ecsv")
    footprint = activities.eval_footprint_hierarchy(
        activities.eval_compute_footprint,
        {"FR": {"CNES": resources, "IN2P3": resources}},
    )
    footprint.log(logger, formatter=lambda v: str(v.to(u.kg)))
    logger.info(f"CPU: {footprint.agg("$..CPU").to(u.kg)}")
    logger.info(f"GPU: {footprint.agg("$..GPU").to(u.kg)}")
