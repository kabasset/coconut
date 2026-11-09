import astropy.units as u
import math

from coconut.ctree import CTree


def test_ctree_floats():
    tree = {"A": 1, "B": {"B1": 2, "B2": 4}}
    ctree = CTree(tree)
    assert ctree.total == 7
    assert ctree["A"].total == 1
    assert ctree["B"].total == 6
    assert ctree["B"]["B1"].total == 2
    assert ctree["B"]["B2"].total == 4


def test_ctree_product():
    tree = {"A": 1, "B": {"B1": 2, "B2": 4}}
    ctree = CTree(tree, agg=math.prod, key="PROD")
    assert ctree.total == 8
    assert ctree["A"].total == 1
    assert ctree["B"].total == 8
    assert ctree["B"]["B1"].total == 2
    assert ctree["B"]["B2"].total == 4


def test_ctree_quantities():
    tree = {"A": 1 * u.g, "B": {"B1": 2 * u.g, "B2": 4 * u.g}}
    ctree = CTree(tree)
    assert ctree.total == 7 * u.g
    assert ctree["A"].total == 1 * u.g
    assert ctree["B"].total == 6 * u.g
    assert ctree["B"]["B1"].total == 2 * u.g
    assert ctree["B"]["B2"].total == 4 * u.g


def test_ctree_agg():
    tree = {"A1": {"B": 1 * u.kg, "C": 2 * u.kg}, "A2": {"B": 4 * u.kg, "C": 8 * u.kg}}
    ctree = CTree(tree)
    assert ctree.total == 15 * u.kg
    assert ctree.agg("$") == ctree.total
    assert ctree.agg("$..B") == 5 * u.kg
    assert ctree.agg("$..C") == 10 * u.kg
