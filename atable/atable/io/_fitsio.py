# -*- coding:utf-8 -*-
import logging

import fitsio

from . import _fits_base

from ..utils import is_number
from ..utils.data import sample
#from booq.io import recarray

FitsBase = _fits_base.FitsBase
class Fits(FitsBase):
    '''
    '''
    def __init__(self, *args, **kwargs):
        super(Fits,self).__init__(*args,**kwargs)

    def _extract_meta(self,header,data):
        from .metadata import Meta
        return Meta(header,data)

    @property
    def columns(self):
        return self.meta.columns

    @property
    def colnames(self):
        return self.columns.index


FitsHandlerBase = _fits_base.FitsHandlerBase
class FitsHandler(FitsHandlerBase):
    '''
    '''
    def _get_handler(self,ext,iterrows=False):
        if iterrows:
            iterrows = max(100000,int(iterrows))
            handler = get_handler_iterrows(self._filename, ext, iterrows)
        else:
            handler = get_handler(self._filename, ext)
        return handler

    def _get_header(self):
        header = self._handler.read_header()
        return header

    def __info(self):
        print(self._handler)
    info = property(__info, doc="Meta/general information")

    def __nrows(self):
        return self._handler.get_nrows()
    nrows = property(__nrows, doc="Number of rows in table")

    def read(self, columns=None, rows=None, ucds=None, match_ucds='any',
             filter_rows=None):
        '''
        '''
        if is_number(rows):
            logging.debug("Argument 'rows' is a number.")
            rows = sample(self.nrows,fraction=rows)
        if ucds:
            logging.info("using 'ucds' to define 'columns' to read.")
            logging.debug("'ucds' requested: {!s}".format(ucds))
            ucdcols = self.colnames_by_ucd(ucds, match=match_ucds)
            if ucdcols:
                if not columns:
                    columns = []
                columns.extend(ucdcols)
                #REVIEW: order of columns after 'set' is not guarantee
                columns = list(set(columns))
        logging.debug("'columns' to be read: {!s}".format(columns))
        data,meta = read_from_handler(self._handler, columns=columns, rows=rows, filter_rows=filter_rows)
        return Fits(data,meta,self)

# ---

# def get_ucds(handler):

def get_handler_iterrows(filename, ext=1, iterrows=1000):
    '''
    '''
    import fitsio
    hdul = fitsio.FITS(filename,iter_row_buffer=iterrows)
    handler = hdul[1]
    return handler

def get_handler(filename, ext=1):
    '''
    '''
    import fitsio
    hdul = fitsio.FITS(filename)
    handler = hdul[1]
    return handler

def read_from_handler(handler, columns=None, rows=None, metaonly=False,
                      filter_rows=None):
    '''
    '''
    import numpy as np
    # -----------------------------------------------------------------
    def read_meta_from_handler(handler):
        header = handler.read_header()
        return header

    def read_data_from_handler(handler, columns=None, rows=None, filter_rows=None):
        if rows is not None:
            rows.sort()
        if filter_rows is None:
            data = handler.read(columns=columns, rows=rows, header=False)
        else:
            # take the first as array template
            data = handler.read(rows=[0], header=False)
            datacols = data.dtype.names

            # rows have no column names, so we have to transform names into index
            def define_function(filter_rows,datacols):
                assert all(k in datacols for k in filter_rows.keys()), \
                        'Not all given columns exist in FITS being read'
                filter_inds = { datacols.index(col):foo for col,foo in filter_rows.items() }
                def select_function(row,filter_inds=filter_inds):
                    mask = [ filter_inds[i](row[i]) for i in filter_inds.keys() ]
                    return all(mask)
                return select_function
            select_function = define_function(filter_rows,datacols)

            for i,row in enumerate(handler):
                sel = select_function(row)
                if sel:
                    data = np.append(data, row)
            # remove the first line, used only as template
            data = np.delete(data,0,0)
            # keep only 'columns'
            if columns is not None:
                colindxs = [ datacols.index(c) for c in columns ]
                data = np.delete(data,colindxs,1)
        return data
    # -----------------------------------------------------------------

    header = read_meta_from_handler(handler)
    if metaonly:
        return header
    data = read_data_from_handler(handler, columns=columns, rows=rows,
                                        filter_rows=filter_rows)
    return 	(data,header)

# ---


class header(object):
    @staticmethod
    def set_columns_metadata(recarray,filename,hdu=1):
        """
        Update header keywords respective to: name, unit, ucd, description.
        """
        from astropy.io import fits as pyfits

        h_desc_pfx = 'TCOMM'
        h_unit_pfx = 'TUNIT'
        h_name_pfx = 'TTYPE'
        h_ucd_pfx = 'TUCD'

        hdul = pyfits.open(filename,memmap=True)
        h = hdul[hdu].header
        colnames = header.get_column_names(h)

        for _r in recarray:
            assert _r.name in colnames,"Column name '{}' not in colnames '{}'".format(_r.name,colnames)

        i = 0
        for _r in recarray:
            i += 1
            assert h[h_name_pfx+str(i)] == _r.name
            h[h_unit_pfx+str(i)] = _r.unit
            h[h_ucd_pfx+str(i)] = _r.ucd
            h[h_desc_pfx+str(i)] = _r.description

        hdul.writeto(filename,clobber=True)

    @staticmethod
    def get_columns_metadata(filename,hdu=1):
        """
        Return column's metadata: name, unit, description, ucd; whenever availble

        The structure returned is an ordered dictionary; keys are the column names.
        """
        from astropy.io import fits as pyfits

        h = pyfits.open(filename,memmap=True)[hdu].header
        nfields = h['TFIELDS']
        h_desc_pfx = 'TCOMM'
        h_unit_pfx = 'TUNIT'
        h_name_pfx = 'TTYPE'
        h_ucd_pfx = 'TUCD'

        out = recarray((nfields,),
                        formats='int16,a30,a20,a40,a100',
                        names='order,name,unit,ucd,description')

        for i in range(1,nfields+1):
            _name = h[h_name_pfx+str(i)]
            _unit = h.get(h_unit_pfx+str(i),'')
            _ucd = h.get(h_ucd_pfx+str(i),'')
            _desc = h.get(h_desc_pfx+str(i),'')
            out[i-1] = (i,_name,_unit,_ucd,_desc)

        return out

    @staticmethod
    def get_column_names(hdr):
        """
        """
        from collections import OrderedDict
        out = OrderedDict()

        h_name_pfx = 'TTYPE'
        nfields = hdr['TFIELDS']

        for i in range(1,nfields+1):
            out[i] = hdr[h_name_pfx+str(i)]

        return list(out.values())
