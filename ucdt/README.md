# UCD

Unified Content Descriptor is a low-level data descriptor for
astronomical data.
UCDs are used to describe data sets using a specific dictionary and
grammatic in such a way that UCDs can be understand by machines.

This package implements an interface to store and relate UCDs to
data sets

Suppose we have a table which we want to query for "columns containing
photometric" data.
There are many specifications of "photometric measurements", in the
physical world as well as in the UCDs.
This package provides the interface to such query, which would retrieve
*all* columns related to "photometry" somehow.

The UCDs here are organized in a tree structure,
respecting their semantics:
```
(Photometry)
phot
- flux
 - density
- mag
```

This package is also implemented to extend IVOA's official UCDs
dictionary.
Also, the interface may use a *translator* given by the user so that
queries like "Main positional columns" are retrieved when there is
more the one pair of columns with coordinate information.


## Tools

Module `utils`:
* To help on describing your dataset with appropriate UCDs,
you'll find in this module the function `ucd_from_description` which
returns the usual UCDs for a given description.

If you're trying to enrich your dataset with UCDs to make a better
use of it as well as to share/publish a higher quality data, this
module is here to to you.
