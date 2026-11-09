# SPDX-FileCopyrightText: Copyright (C) 2025-2026, Antoine Basset (CNES) and contributors
# SPDX-PackageSourceInfo: https://gitlab.esa.int/lisa-sgs/sys/sandbox/coconut
# SPDX-License-Identifier: Apache-2.0

import argparse
from pathlib import Path

from coconut import _version
from coconut.logging import logger
from coconut import process


def add_parser():

    parser = argparse.ArgumentParser(
        description=_version.__description__,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--log",
        type=str,
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level.",
    )
    parser.add_argument(
        "--datadir",
        type=Path,
        default="data",
        help="Data directory, which contains parameter data bases.",
    )

    subparsers = parser.add_subparsers(title="Commands", dest="cmd")
    version = subparsers.add_parser("version", help="Print the version.")
    version.set_defaults(func=print_version)
    process.add_parser(subparsers, "Compute the carbon footprint of some activities.")

    return parser


def print_version(args):
    logger.info(f"{_version.__title__} v{_version.__version__}")


def run():

    parser = add_parser()
    args = parser.parse_args()

    logger.setLevel(args.log)

    args.func(args)


if __name__ == "__main__":
    run()
