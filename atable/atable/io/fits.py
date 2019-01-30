#-*- coding:utf-8 -*-
import logging

from . import _fitsio
__FITSLIB = 'fitsio'
# try:
#     import _fitsio
#     __FITSLIB = 'fitsio'
# except ImportError,e:
#     import _astropy
#     __FITSLIB = 'astropy'


def open(filename, iterrows=False, lib='fitsio'):
    '''
    Input:
     - filename : str
            FITS filename
     - ext : int
            FITS extension
     - lib : string, options are ['fitsio','astropy']
            Force the use of specified 'lib'

    Output:
     - ~FitsHandler to access metadata and eventually load data
    '''
    if __FITSLIB == 'fitsio' and lib == 'fitsio':
        logging.debug("FitsIO being used.")
        handler = _fitsio.FitsHandler(filename,iterrows=iterrows)
    else:
        logging.debug("Astropy being used.")
        handler = _astropy.FitsHandler(filename)
    return handler
