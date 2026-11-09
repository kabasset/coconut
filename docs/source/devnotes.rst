Developer notes
===============


Grow-only mapping
-----------------

In order to cope with a variety of input granularities, it was decided to implement on-demand computations.
Let's take the example of the human resource daily work footprint estimation,
a computation which depends on the electric mix.
If the input table contains a specific column `electric_mix`, its values will be used.
Otherwise, we fall back to the `electric_mix` of the country as specified in some mix-by-country table.
Finally, if no such table is provided, the footprint will rely on the default electric mix.

We implemented this on-demand computation with a structure known as a grow-only table:
instead of manually computing a new column from existing columns,
the user of this structure specifies the formula only.
If the resulting column already exists, no computation is performed.
Otherwise, the formula is used to create the new column.
A column which exists is never overwritten and columns cannot be removed,
such that the table only grows!

This behavior is implemented through class `GMapping`.


Cumulative tree
---------------

Footprint evaluations are nested.
For example, the overall computation footprint of a project may be the sum of country-wise contributions,
themselves made of storage, CPU and GPU footprints.
The users may want to access the footprint estimates at different levels (e.g. French contribution or French storage footprint),
and to perform aggregations between various contributions (e.g. overall GPU footprint).

To this end, we implemented `CTree`, a labeled tree in which:

* leaves are labeled with their individual footprint,
* nodes are labeled with the aggregation of their children's labels.

The class also supports transversal aggregation based on the node selection syntax `JSONPath`.
