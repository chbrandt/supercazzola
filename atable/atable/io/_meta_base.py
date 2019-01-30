# -*- coding:utf-8 -*-

import logging

# from booq.ucd import UCD
# from astropy.units import Unit

from collections import OrderedDict
class MetaColumnBase(OrderedDict):
    '''
    '''
    # 'mt_map' stores a column's metadata: its key values.
    # It is map to allow for extra processing for each parameter;
    # for example, 'ucd' can map to booq.ucd.UCD constructor.
    #
    mt_map = {'ucd'         : None,
              'unit'        : None,
              'description' : None,
              'dtype'       : None,
              'null'        : None
              }

    def __init__(self,name):
        super(MetaColumnBase,self).__init__()

        self._name = name

        # Null-Init members
        for kw in list(self.mt_map.keys()):
            self[kw] = None

    def set_from_header(self,header):
        '''
        Get column' metadata from 'header'
        '''
        assert False, "Not implemented"

    def set_from_data(self,data):
        '''
        Get column' metadata from 'data'
        '''
        assert False, "Not implemented"


    @property
    def name(self):
        return self._name

    # UCD
    def _get_ucd(self):
        return self['ucd']

    def _set_ucd(self,ucd):
        self['ucd'] = ucd

    ucd = property(_get_ucd, _set_ucd, "Get/Set column's UCD")

    # Unit
    def _get_unit(self):
        return self['unit']

    def _set_unit(self, unit):
        self['unit'] = unit

    unit = property(_get_unit, _set_unit, "Get/Set column's unit")

    # Description
    def _get_description(self):
        return self['description']

    def _set_description(self, description):
        self['description'] = description

    description = property(_get_description, _set_description,
                           "Get/Set column's description")

    # Dtype
    def _get_dtype(self):
        return self['dtype']

    def _set_dtype(self, dtype):
        self['dtype'] = dtype

    dtype = property(_get_dtype, _set_dtype, "Get/Set column's dtype")

    # Null
    def _get_null(self):
        return self['null']

    def _set_null(self, null):
        self['null'] = null

    null = property(_get_null, _set_null, "Get/Set column's null")


class MetaBase(OrderedDict):
    '''

    '''
    mt_map = {  'NROWS' : None,
                # 'NCOLS' : None,
                'COLUMNS': None,
    }

    def __init__(self):
        super(MetaBase,self).__init__()

        # Null-Init members
        for kw in list(self.mt_map.keys()):
            self[kw] = None

        self._columns = None

    def _init_meta(self):
        assert False, "Not implemented"

    def _init_columns(self):
        assert False, "Not implemented"

    # def _set_nrows(self,N):
    #     self['NROWS'] = N
    #
    # # def _set_ncols(self,N):
    # #     self['NCOLS'] = N
    #
    # def _set_fields(self,fields):
    #     self['COLUMNS'] = [ f.strip() for f in fields ]

    def column(self,name):
        return self.columns.loc[name]

    @property
    def nrows(self):
        return self['NROWS']

    @property
    def ncols(self):
        return self['NCOLS']

    @property
    def columns(self):
        return self._columns

    @property
    def colnames(self):
        #FIXME: this is horrendous! why I need 'COLUMNS'?!!
        if not self.columns is None:
            return self.columns.index
        else:
            return self['COLUMNS']
