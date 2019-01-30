# -*- coding:utf-8 -*-

import logging

from ..ucd import UCD
from astropy.units import Unit

from ._meta_base import MetaColumnBase
class MetaColumn(MetaColumnBase):
    '''
    '''
    mt_map = {'ucd'         : ('TUCD',UCD),
              'unit'        : ('TUNIT',Unit),
              'description' : ('TCOMM',str),
              'dtype'       : ('TFORM',str)}


    def set_from_header(self,header):
        '''
        Get column metadata from 'header'

        Once the function knows what is the position of this column
        (after self.name) in the respective, original table, some
        metadata (for instance, UCD, unit, datatype and description)
        are collected from the FITS 'header'.
        '''
        n = search_column_in_header(header,self.name)
        assert n
        assert header.get('TTYPE'+str(n), None) # column name
        for mt,o_o in self.mt_map.items():
            hdrpfx,Inst = o_o
            hdr_kw = hdrpfx + str(n)
            self[mt] = Inst(header.get(hdr_kw, '').strip())

    def set_from_data(self,data):
        '''
        '''
        if not data is None:
            Inst = self.mt_map['dtype'][1]
            # dtype_name = data.dtype.fields[self.name][0].name
            dtype_name = data[self.name].dtype.name
            try:
                from numpy import empty
                _a = empty(shape=[1], dtype=dtype_name)
            except:
                dtype_name = ''.join( s for s in dtype_name if not s.isdigit() )
            self['dtype'] = Inst(dtype_name)


from ._meta_base import MetaBase
class Meta(MetaBase):
    '''

    '''
    def __init__(self,header,data=None):
        super(Meta,self).__init__()

        self._init_meta(header,data)

    def _init_meta(self,header,data):
        if data != None:
            logging.debug("'data' given, NROWS,NCOLS,FIELDS taken from data array.")
            self._set_nrows(len(data))
            self._set_ncols(len(data.dtype))
            self._set_fields(data.dtype.names)
        else:
            logging.debug("'data' not given, NROWS,NCOLS,FIELDS taken from header.")
            self._set_nrows(int(header.get('NAXIS1')))
            self._set_ncols(int(header.get('TFIELDS')))
            self._set_fields([ header.get(k) for k in header if 'TTYPE' in k ])
        assert len(self.columns) == self.ncols, "Number of columns and fields do not match!"

        self._init_columns(header,data)

    def _init_columns(header,data):
        _columns_dict = self._extract_columns_meta(header,data)
        self._columns = self._columns_as_dataframe(_columns_dict)
        logging.debug("Columns metadata: \n{!s}".format(self.columns))

    @staticmethod
    def _columns_as_dataframe(cols_dict):
        _mt = list(cols_dict.values())
        dat = dict(list(zip(_mt[0], list(zip(*[list(d.values()) for d in _mt ])))))
        idx = list(cols_dict.keys())
        from ..atable import ADataFrame
        df = ADataFrame(dat,index=idx)
        df.index.name = 'colnames'
        return df

    def _extract_columns_meta(self,header,data):
        from collections import OrderedDict
        cols = OrderedDict()
        logging.debug("Reading metadata for columns {}".format(self['FIELDS']))
        for colname in self['FIELDS']:
            metacolumn = MetaColumn(colname)
            metacolumn.set_from_header(header)
            metacolumn.set_from_data(data)
            cols[colname] = metacolumn
        return cols



def search_column_in_header(header,colname):
    '''
    Header keyword for column names is 'TTYPEn', where 'n' is a number

    'n', btw, is the number we lost and wanna find out here...

    Returns 'n'
    '''
    colname = colname.strip()
    logging.debug("Searching for column '{}' in header".format(colname))
    n = None
    prefix_standard = 'TTYPE'
    for kword in list(header.keys()):
        if prefix_standard in kword:
            value = header[kword]
            value = value.strip()
            if value == colname:
                n = int( kword.strip(prefix_standard) )
    return n


# def search_meta_in_header(header,n):
#     '''
#     Given the column identifier 'n', get UCD, unit and description
#
#     Returns a dictionary
#     '''
#     from collections import OrderedDict
#     logging.debug("Column index being searched: '{}'".format(n))
#     out = OrderedDict()
#     prefix_ucd = 'TUCD'
#     prefix_unit = 'TUNIT'
#     prefix_descr = 'TCOMM'
#     assert header.get('TTYPE'+str(n), None)
#     kw_ucd = prefix_ucd + str(n)
#     out['ucd'] = header.get(kw_ucd, '').strip()
#     kw_unit = prefix_unit + str(n)
#     out['unit'] = header.get(kw_unit, '').strip()
#     kw_descr = prefix_descr + str(n)
#     out['description'] = header.get(kw_descr, '').strip()
#     return out
