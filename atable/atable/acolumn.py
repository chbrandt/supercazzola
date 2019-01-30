import logging

from astropy.table import MaskedColumn,Column

from .ucd import UCD


class AColumn(Column):
    '''
    Overload ~astropy.table.Column to include UCD support
    '''
    def __new__(cls,*args,**kwargs):
        '''
        If 'meta' dict is given, take 'ucd' key/value and set as property

        Default UCD (if nothing is given) is '' (null string)
        '''
        logging.debug("Arguments: {}\n{}".format(args,kwargs))

        meta = kwargs.get('meta',None)

        if meta:
            for k in ['unit','dtype','description']:
                kwargs[k] = meta.pop(k,None)

        self = super(AColumn,cls).__new__(cls,*args,**kwargs)
        return self

    def _get_ucd(self):
        '''
        Return current UCD
        '''
        from .ucd import UCD
        return UCD(self.meta.get('ucd',None))

    def _set_ucd(self,ucd):
        '''
        If a valid UCD, set it to column
        '''
        from .ucd import UCD
        _ucd = UCD(ucd)
        #REVIEW: what is a valid UCD?
        self.meta['ucd'] = _ucd
        # if _ucd.is_valid():
        #     self._ucd = _ucd
        # else:
        #     logging.warning("Not a valid UCD: {!r}".format(_ucd))

    ucd = property(_get_ucd, _set_ucd, doc="Get/Set column's UCD")


    def _get_null(self):
        '''
        Return NULL value
        '''
        return self.meta.get('null',None)

    def _set_null(self,null):
        '''
        If a valid NULL value, set it to column
        '''
        _null = null
        self.meta['null'] = _null

    null = property(_get_null, _set_null, doc="Get/Set column's NULL")
