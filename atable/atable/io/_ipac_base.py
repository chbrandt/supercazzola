#-*- coding:utf-8 -*-
import logging


class IpacBase(object):
    '''
    '''
    def __init__(self, data, header, handler=None):
        self._data = data
        self._header = header
        self._meta = self._extract_meta(self._header,self._data)

    def __len__(self):
        return len(self._data)
    length = property(__len__, doc="Number of rows in data")

    def __width__(self):
        return len(self._data.dtype)
    width = property(__width__, doc="Number of columns in data")

    def __shape__(self):
        return (self.length,self.width)
    size = property(__shape__, doc="Shape of data")

    def __get_data(self):
        return self._data
    data = property(__get_data, doc="Returns IPAC data array")

    def __get_meta(self):
        return self._meta
    meta = property(__get_meta, doc="Returns IPAC metadata")


class HandlerBase(object):
    def read(self):
        assert None, "Not implemented, this is a base class."


class IpacHandlerBase(HandlerBase):
    '''
    '''
    def __init__(self, filename):
        from ._meta_ipac import Meta

        self._filename = filename
        self._handler = None
        self._meta = Meta(self._get_header())
        self._meta._set_nrows( count_data_rows(filename) )

    def __str__(self):
        return str(self._handler)

    def _get_handler(self):
        assert False, "This is a Base class, you should not be seeing this."

    def _get_header(self):
        assert False, "This is a Base class, you should not be seeing this."

    def __info(self):
        assert False, "This is a Base class, you should not be seeing this."

    def __nrows(self):
        return self._meta.nrows
    nrows = property(__nrows, doc="Number of rows in table")

    def __colnames(self):
        return self._meta.colnames
    colnames = property(__colnames, doc="Column names on table")

    def __ucds(self):
        return self.columns.ucd
    ucds = property(__ucds, doc="UCDs associated")

    def __units(self):
        return self.columns.unit
    units = property(__units, doc="Units associated")

    def _get_columns(self):
        return self._meta.columns
    columns = property(_get_columns, doc="Return table with columns information")

    def colnames_by_ucd(self,ucds,match='any'):
        '''
        Find out which columns correspond to given UCDs

        Returns list of column names matching 'ucds'
        Input:
         - ucds  : str, list of ucd-words or list of UCDs
                Example, ['pos','meta.id']
         - match : str
                Columns UCD should match 'all', or just 'any' one given?
        Output:
         - colnames : list of column names
        '''
        ucd = ucds
        logging.info("Match '{}' of UCDs '{}'".format(match,ucd))
        if isinstance(ucd,str):
            ucd = [ucd]
        if match == 'any':
            indx = len(self.ucds) * [False]
            for u in ucd:
                logging.debug("UCD being matched: '{!s}'".format(u))
                u = [u]
                indx |= self.ucds.apply(lambda x:x.isin(u))
        else:
            assert match == 'all', "Options for 'match' are ['all','any']"
            indx = self.ucds.apply(lambda x:x.isin(ucd))
        colnames = indx[indx].index.values.tolist()
        logging.debug("Columns got from UCDs: {}".format(colnames))
        return colnames

def count_data_rows(filename):
    '''
    '''
    fp = open(filename,'r')

    i = 0
    for line in fp.readlines():
        if not (line[0] == '\\' or line[0] == '|'):
            break
        i+=1
    counter_lines_header = i

    fp.seek(0)
    for i, line in enumerate(fp,1):
        pass
    counter_lines_data = i - counter_lines_header

    fp.close()
    logging.debug("Total number of lines on (IPAC) file '{}':{:d}".
                format(filename,counter_lines_header+counter_lines_data))
    return counter_lines_data
