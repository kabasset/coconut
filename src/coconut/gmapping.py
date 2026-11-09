# SPDX-FileCopyrightText: Copyright (C) 2025-2026, Antoine Basset (CNES) and contributors
# SPDX-PackageSourceInfo: https://gitlab.esa.int/lisa-sgs/sys/sandbox/timeo
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Iterator

from dataclasses import dataclass


@dataclass
class GMapping:
    """
    Wrapper to enable grow-only semantics on top of a mapping.

    Only GET and ADD operations are available.
    Other operations, like SET, are silently ignored.

    Semantics are as follows:
    * Getting an element with a key which does not exist returns some "not available" sentinel (NA).
    * Setting an element with a key which already exists does nothing.
    * Adding an element with value NA does nothing.

    The wrapped container must implement bracket operators
    for getting (``__getitem__()``) and adding values (``__setitem__()``).

    For example:

    >>> mapping = GMapping({"A": 1, "B": 2, "C": 3}, pandas.NA)  # Wraps a dict
    >>> mapping["A"] = pandas.NA  # Does not assign: NA is ignored
    >>> mapping["A"] = mapping["D"]  # Does not assign: "D" is not a key thus mapping["D"] is NA
    >>> mapping["C"] = mapping["A"] + mapping["B"]  # Does not assign: "C" already exists
    >>> mapping["D"] = mapping["A"] + mapping["C"]  # Adds item ("D", 4)

    If the right-hand side does not support lazy evaluation and performance is a concern,
    function ``bind()`` delays evaluation such that no computation is performed if the key already exists:

    >>> mapping.bind("C", lambda: mapping["A"] + mapping["B"])  # The lambda is not even evaluated

    Default key-values can also be specified, in which case, if the mapping does not contain a key:
    * If the key has a default value, it is returned instead of NA;
    * Otherwise, NA is returned.

    >>> mapping = GMapping({}, defaults={"A": 1})
    >>> assert mapping["A"] == 1
    >>> assert mapping.is_na(mapping["B"])

    Args:
        container:
            The wrapped container which implements ``__getitem__()`` and ``__setitem__()``.
        na:
            The "not available" value, e.g. ``None``, ``float("NaN")``, ``numpy.nan`` or ``pandas.NA``.
        is_na:
            The predicate which tests value availability,
            or string ``"is"`` for testing object equality with ``na``,
            or string ``"eq"`` for testing value equality with ``na``,
            or string ``"nan"`` for testing inequality with itself.
            By definition, ``is_na(na)`` must return ``True``.
        has_key:
            The predicate which tests key presence,
            or string ``"in"`` for testing with container's ``__contains__()``,
            or string ``"keys()"`` for testing with container's ``keys().__contains__()``.
        is_key:
            The predicate which tests whether the argument of ``__getitem__()`` and ``__setitem__()`` is a key,
            or any type (e.g. ``str``) to test based on the argument type only.
    """

    def __init__(
        self,
        container,
        na=None,
        is_na="is",
        has_key="keys()",
        is_key=str,
        defaults: dict = {},
    ):
        self.container = container
        self.defaults = defaults
        self.na = na

        if not isinstance(is_na, str):
            assert callable(is_na)
            self.is_na = is_na
        if is_na == "is":
            self.is_na = lambda x: x is self.na
        elif is_na == "eq":
            self.is_na = lambda x: x == self.na
        elif is_na == "nan":
            self.is_na = lambda x: x != x
        else:
            raise ValueError(f"Unknown value for is_na: {is_na}")
        if not self.is_na(self.na):
            raise ValueError(f"is_na(na) must return True.")

        if not isinstance(has_key, str):
            assert callable(has_key)
            self.has_key = has_key
        elif has_key == "in":
            self.has_key = lambda k: k in self.container
        elif has_key == "keys()":
            # This is part of Python's Data Model;
            # It works with dict, pandas.DataFrame and astropy.Table.
            self.has_key = lambda k: k in self.container.keys()
        else:
            raise ValueError(f"Unknown value for has_key: {has_key}")

        if not isinstance(is_key, type):
            assert callable(is_key)
            self.is_key = is_key
        else:
            self.is_key = lambda k: isinstance(k, is_key)

    def __len__(self) -> int:
        """
        Get the container length.
        """
        return len(self.container)

    def __iter__(self) -> Iterator:
        """
        Iterate over the container.
        """
        return iter(self.container)

    def __getitem__(self, key) -> Any:
        """
        Get ``container[key]`` if it is available, or ``na`` otherwise.

        If ``key`` is not a key as defined by ``is_key``, the call is simply forwarded to the container.
        """
        if not self.is_key(key):
            return self.container[key]
        if self.has_key(key):
            return self.container[key]
        if key in self.defaults:
            return self.defaults[key]
        return self.na

    def __setitem__(self, key, value):
        """
        Add ``container[key] = value`` if the value is not ``na``.

        If ``key`` is not a key as defined by ``is_key``, the call is simply forwarded to the container.
        """
        if not self.is_key(key):
            self.container[key] = value
        if self.is_na(value) or self.has_key(key):
            return
        self.container[key] = value

    def bind(self, key, func):
        """
        Add ``container[key] = func()`` if the function does not return ``na``.

        If the key already exists, then the function is not evaluated.
        """
        if self.has_key(key):
            return
        value = func()
        if not self.is_na(value):
            self.container[key] = value
