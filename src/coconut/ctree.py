# SPDX-FileCopyrightText: Copyright (C) 2025-2026, Antoine Basset (CNES) and contributors
# SPDX-PackageSourceInfo: https://gitlab.esa.int/lisa-sgs/sys/sandbox/timeo
# SPDX-License-Identifier: Apache-2.0

from typing import Callable

import jsonpath


def scan(tree: object, agg=sum, key=None, dtype=dict):
    """
    Recursively compute the partial sums in a tree.

    For each subtree, the partial sum is computed with aggregation function ``agg``,
    and optionally stored within the subtree with key ``key`` if it is not ``None``.
    Recursion stops when it reaches a leaf or a subtree with a key already named ``key``
    (which is assumed to be the partial sum of the subtree).

    Args:
        tree:
            A nested dictionary of values,
            which the function modifies in place if ``key`` is not ``None``.
        agg:
            The aggregation function, which takes as input an iterable and returns a scalar.
        key:
            The key to store partial sums in the input tree.
        dtype:
            The ``dict``-like type which represents a subtree.
            It must implement at least ``__getitem___()`` and ``__iter__()``,
            as well as ``__setitem__()`` if ``key`` is not ``None``.

    Returns:
        The grand total.
    """
    if not isinstance(tree, dtype):
        return tree
    if key is not None and key in tree:
        return tree[key]
    total = agg(scan(tree[k], agg, key, dtype) for k in tree)
    if key is not None:
        tree[key] = total
    return total


class CTree:
    """
    Cumulative tree.

    This is a wrapper class built from function ``scan()``.

    Partial cumulative trees are accessed with bracket operator,
    in which the partial sums are stored as member ``total``:

    >>> tree = CTree({"A1": {"B": 1, "C": 2}, "A2": {"B": 4, "C": 8}})
    >>> total = tree.total  # 15
    >>> A1 = tree["A1"].total  # 3

    If the keys of the tree are strings,
    contributions which match a given JSONPath pattern can be further aggregated with function ``agg()``.

    >>> B = tree.agg("$..B")  # 5

    See ``scan()`` for more details.
    """

    def __init__(self, tree: dict, agg=sum, key=None, dtype=dict):
        self._tree = tree
        self._agg = agg
        self._key = key
        self._dtype = dtype
        self._total = self._scan(self._tree)

    @property
    def total(self):
        """
        Grand total of the tree.
        """
        return self._total

    def to_dict(self):
        """
        Convert the tree to a ``dict`` (values are copied).
        """
        return self._tree.copy()

    def _scan(self, tree):
        """
        Call ``scan()`` with the object parameters.
        """
        return scan(tree, self._agg, self._key, self._dtype)

    def __getitem__(self, key) -> CTree:
        """
        Get a cumulative subtree.
        """
        return CTree(self._tree[key], self._agg, self._key, self._dtype)

    def agg(self, pattern: str):
        """
        Aggregate the values which match a JSONPath pattern.
        """
        values = jsonpath.findall(pattern, self._tree)
        return self._agg(self._scan(v) for v in values)

    def log(self, logger, level: int = 0, tab: str = "  ", formatter: Callable = str):
        key = "TOTAL" if self._key is None else self._key.upper()
        if level == 0:
            logger.info(tab * level + f"{key}: {formatter(self.total)}")
        for k in self._tree:
            if k == self._key:
                continue
            msg = tab * (level + 1) + f"{k}: "
            v = self[k]
            if isinstance(v._tree, dict):
                logger.info(msg + formatter(v.total))
                v.log(logger, level + 1, tab, formatter)
            else:
                logger.info(msg + formatter(v.total))
