# atable

A table handler for astronomical catalogs

Based in Astropy's Table class, `ATable` adds more versatil I/O interface for FITS files,
and adds also a more expressive `metatable` structure, complaint with IVOA's UCD, to better 
handle catalog' columns.

## Using it

Add this directory to your `PYTHONPATH` environment variable,
```bash
# export PYTHONPATH="$PWD:$PYTHONPATH"
```
, if you are using Bash. (If you're using other shell or interpreter, adjust accordingly).

Then start a python interpreter and try:
```python
>>> import table
>>> help(atable)
```

## Install

`atable` depends on:
* astropy;
* fitsio.

Using `pip` you can install the depencies like:
```bash
# pip install astropy
# pip install fitsio
```

If you use `conda` you can use the available `environment.yml`.
```bash
# conda-env create -f environment.yml
```

/.\
