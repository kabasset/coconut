# SPDX-FileCopyrightText: Copyright (C) 2025-2026, Antoine Basset (CNES) and contributors
# SPDX-PackageSourceInfo: https://gitlab.esa.int/lisa-sgs/sys/sandbox/timeo
# SPDX-License-Identifier: Apache-2.0

import logging

from timeo import _version

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(_version.__title__)
