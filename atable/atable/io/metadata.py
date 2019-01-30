# -*- coding:utf-8 -*-

import logging

from ..ucd import UCD
from astropy.units import Unit

from collections import OrderedDict
class MetaColumn(OrderedDict):
    '''
    '''
    mt_map = {'ucd'         : ('TUCD',UCD),
              'unit'        : ('TUNIT',Unit),
              'description' : ('TCOMM',str),
              'dtype'       : ('TFORM',str)}

    def __init__(self,name):
        super(MetaColumn,self).__init__()

        self._name = name

        # Null-Init members
        for kw in list(self.mt_map.keys()):
            self[kw] = None

    def set_from_header(self,header):
        '''
        Given the column number, get UCD, unit and description
        '''
        n = search_column_in_header(header,self.name)
        assert n
        assert header.get('TTYPE'+str(n), None) # column name
        for mt,o_o in self.mt_map.items():
            hdrpfx,Inst = o_o
            hdr_kw = hdrpfx + str(n)
            try:
                _inst = Inst(header.get(hdr_kw, '').strip())
                self[mt] = _inst
            except:
                continue

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



    @property
    def name(self):
        return self._name

    @property
    def ucd(self):
        return self['ucd']

    @property
    def unit(self):
        return self['unit']

    @property
    def description(self):
        return self['description']

    @property
    def dtype(self):
        return self['dtype']

class Meta(OrderedDict):
    '''
    '''
    def __init__(self,header,data=None):
        super(Meta,self).__init__()
        if not data is None:
            logging.debug("'data' given, NROWS,NCOLS,FIELDS taken from data array.")
            self['NROWS'] = len(data)
            self['NCOLS'] = len(data.dtype)
            self['FIELDS'] = data.dtype.names
        else:
            logging.debug("'data' not given, NROWS,NCOLS,FIELDS taken from header.")
            self['NROWS'] = int(header.get('NAXIS1'))
            self['NCOLS'] = int(header.get('TFIELDS'))
            self['FIELDS'] = [ header.get(k).strip() for k in header if 'TTYPE' in k ]
        _columns_dict = self._extract_columns_meta(header,data)
        self['columns'] = self._columns_as_dataframe(_columns_dict)
        logging.debug("Columns metadata: \n{!s}".format(self['columns']))

    @staticmethod
    def _columns_as_dataframe(cols_dict):
        _mt = list(cols_dict.values())
        dat = dict(list(zip(_mt[0], list(zip(*[list(d.values()) for d in _mt ])))))
        idx = list(cols_dict.keys())
        from ..adataframe import ADataFrame
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

    def column(self,name):
        return self.columns.loc[name]

    @property
    def columns(self):
        return self['columns'].copy()

    @property
    def colnames(self):
        return self.columns.index



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


def search_meta_in_header(header,n):
    '''
    Given the column identifier 'n', get UCD, unit and description

    Returns a dictionary
    '''
    from collections import OrderedDict
    logging.debug("Column index being searched: '{}'".format(n))
    out = OrderedDict()
    prefix_ucd = 'TUCD'
    prefix_unit = 'TUNIT'
    prefix_descr = 'TCOMM'
    assert header.get('TTYPE'+str(n), None)
    kw_ucd = prefix_ucd + str(n)
    out['ucd'] = header.get(kw_ucd, '').strip()
    kw_unit = prefix_unit + str(n)
    out['unit'] = header.get(kw_unit, '').strip()
    kw_descr = prefix_descr + str(n)
    out['description'] = header.get(kw_descr, '').strip()
    return out
