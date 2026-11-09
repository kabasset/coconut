# SPDX-FileCopyrightText: Copyright (C) 2025-2026, Antoine Basset (CNES) and contributors
# SPDX-PackageSourceInfo: https://gitlab.esa.int/lisa-sgs/sys/sandbox/timeo
# SPDX-License-Identifier: Apache-2.0

from dataclasses import dataclass
import pandas as pd
from pathlib import Path

from timeo.logging import logger


@dataclass
class HumanResources:
    commute: pd.DataFrame | None = None  #: Home-workplace commuting
    hardware: pd.DataFrame | None = None  #: Hardware (laptops, screens, heating...)
    videoconferencing: pd.DataFrame | None = None  #: Audio/videoconferencing
    travel: pd.DataFrame | None = None  #: Travel transportation (car, train, plane...)


@dataclass
class ComputingResources:
    cpu: pd.DataFrame | None = None
    gpu: pd.DataFrame | None = None
    ram: pd.DataFrame | None = None
    storage: pd.DataFrame | None = None


def load(cls: type, workdir: Path) -> "cls":
    res = cls()
    logger.debug(f"Load data: {cls.__name__}")
    for field in res.__dataclass_fields__:
        path = workdir / (field + ".csv")
        if path.is_file():
            data = pd.read_csv(path)
            setattr(res, field, data)
            logger.info(f"Loaded field: {field}")
        else:
            logger.warning(f"Cannot load field: {field}")
    return res
