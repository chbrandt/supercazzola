from __future__ import absolute_import

import logging

from .atable import ATable
from .adataframe import ADataFrame
from .ametatable import AMetaTable

def read(filename,format=None,columns=None,rows=None,
            ucds=None,metatable=None,metaonly=False,
            **kwargs):
    """
    Return ~ATable from catalog 'filename'

    Input:
     - filename : string
     - format   : string : 'fits','ecsv','csv'
     - columns  : list of strings or integers
     - rows     : integer, float, list of integers
     - ucds     : list of strings
     - metatable : string : name of the metatable file
     - metaonly  : boolean
    """
    sample = False
    if sample is True:
        rows=0.01
    tab = ATable.read(filename,format=format,columns=columns,rows=rows,
                        ucds=ucds,metatable=metatable,metaonly=metaonly,
                        **kwargs)
    return tab

def info(filename):
    """
    (FITS only) Print the list columns and table's metadata
    """
    from .io import fits
    ft = fits.open(filename)
    print(ft.info)
    return ft

