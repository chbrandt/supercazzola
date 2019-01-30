#-*- coding:utf-8 -*-

from astropy.io import fits

from ._fits_base import FitsBase
class Fits(FitsBase):
    def __init__(self, *args, **kwargs):
        super(Fits,self).__init__(args,kwargs)


from ._fits_base import FitsHandlerBase
class FitsHandler(FitsHandlerBase):
    '''
    '''
    def read(self, columns=None, rows=None):
        '''
        '''
        data,meta = __read_astropy(self._filename, ext=self._ext, metaonly=False,
                                    columns=columns, rows=rows)
        return Fits(data,meta)


# ---

def __read_astropy(filename, columns=None, rows=None, metaonly=False, ext=1):
    '''
    '''
    header = __read_astropy_meta(filename, ext=ext)
    if metaonly:
        return header
    data = __read_astropy_data(filename, columns=columns, rows=rows)
    return 	(data,header)


def __read_astropy_meta(filename, ext=1):
    '''
    '''
    table = __read_astropy_table(filename, ext=ext)
    header = table.header
    return header

def __read_astropy_data(filename, columns=None, rows=None, ext=1):
    '''
    '''
    table = __read_astropy_table(filename, ext=ext)
    data = table.data
    if rows:
        data = data[rows]
    return data

def __read_astropy_table(filename, ext=1):
    '''
    '''
    hdul = fits.open(filename, memmap=True, ignore_missing_end=True)
    table = hdul[ext]
    return table
