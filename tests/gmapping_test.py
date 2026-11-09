# SPDX-FileCopyrightText: Copyright (C) 2025-2026, Antoine Basset (CNES) and contributors
# SPDX-PackageSourceInfo: https://gitlab.esa.int/lisa-sgs/sys/sandbox/timeo
# SPDX-License-Identifier: Apache-2.0

from timeo.gmapping import GMapping


def test_semantics():

    mapping = GMapping({"A": 1, "B": 2, "C": 4}, float("NaN"), "nan")
    mapping["A"] = mapping["D"]
    assert mapping["A"] == 1
    mapping["C"] = mapping["A"] + mapping["B"]  # type: ignore
    assert mapping["C"] == 4
    mapping["D"] = mapping["A"] + mapping["B"]  # type: ignore
    assert mapping["D"] == 3


class LazySpy:
    def __init__(self):
        self.count = {
            "A": {"value": "a", "get": 0, "set": 0},
            "B": {"value": "b", "get": 0, "set": 0},
        }

    def __contains__(self, item):
        return item in self.count

    def __getitem__(self, key):
        self.count[key]["get"] += 1
        return self.count[key]["value"]

    def __setitem__(self, key, value):
        if key not in self.count:
            self.count[key] = {"value": None, "get": 0, "set": 0}
        self.count[key]["set"] += 1
        self.count[key]["value"] = value


def test_lazy_eval():
    mapping = GMapping(LazySpy(), has_key="in")
    mapping.bind("B", lambda: mapping["A"])
    assert mapping.container.count["B"]["set"] == 0
    assert mapping.container.count["A"]["get"] == 0
    assert mapping["B"] == "b"
    mapping["B"] = mapping["A"]
    assert mapping.container.count["B"]["set"] == 0
    assert mapping.container.count["A"]["get"] == 1
    assert mapping["B"] == "b"
    mapping.bind("C", lambda: mapping["A"])
    assert mapping.container.count["C"]["set"] == 1
    assert mapping.container.count["A"]["get"] == 2
    assert mapping["C"] == "a"


def test_defaults():
    mapping = GMapping({}, defaults={"A": 1})
    assert mapping["A"] == 1
    assert mapping.is_na(mapping["B"])
