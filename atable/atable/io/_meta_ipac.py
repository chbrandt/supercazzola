# -*- coding:utf-8 -*-
import logging

from booq.ucd import UCD
from astropy.units import Unit

from ._meta_base import MetaColumnBase
class MetaColumn(MetaColumnBase):
    '''
    '''
    mt_map = {'ucd'         : (None,UCD),
              'description' : (0,str), # because if there is no description, column name will be used
              'dtype'       : (1,str),
              'unit'        : (2,Unit),
              'null'        : (3,str)
              }


    def set_from_header(self,vals):
        '''
        Get column metadata from 'header'

        'vals' is supposed to be a list of lists, in this order:
        - names
        - types
        - units
        - nulls

        The IPAC header is composed by all the lines before data block.
        Metadata is disposed as formally defined by IRSA in
        "http://irsa.ipac.caltech.edu/applications/DDGEN/Doc/ipac_tbl.html":
        \keyword = value                                                  Keywords (optional)
        \ Comment                                                         Comments (optional)
        |  column1  |  column2  | column3 |  column4 |    column5       | Column Names (required)
        |   double  |   double  |   int   |   real   |     char         | Data Types (standard)
        |   unit    |   unit    |   unit  |   unit   |     unit         | Data Units (optional)
        |   null    |   null    |   null  |   null   |     null         | Null Values (optional)
          165.466279  -34.704730      5      11.27         K6Ve           Data Rows (1 required)

        Column description has no formal place in IPAC, what is usually
        done is to add it as a comment as follows:
        \ column1
        \ __ blablabla description of column1 blublublu
        \ column2
        \ __ description column2 bliblibli

        '''
        n = search_column_in_vals(vals,self._name)
        for mt,o_o in self.mt_map.items():
            colposition, Inst = o_o
            if colposition != None:
                val = vals[colposition][n].strip()
                try:
                    valIns = Inst(val)
                except:
                    logging.error('Trying to instanciate {i}, with {v} for column {c}'.\
                        format(i=Inst,v=val,c=self._name))
                else:
                    self[mt] = valIns


    # def set_from_data(self,data):
    #     '''
    #     '''
    #     if not data is None:
    #         Inst = self.mt_map['dtype'][1]
    #         # dtype_name = data.dtype.fields[self.name][0].name
    #         dtype_name = data[self.name].dtype.name
    #         try:
    #             from numpy import empty
    #             _a = empty(shape=[1], dtype=dtype_name)
    #         except:
    #             dtype_name = ''.join( s for s in dtype_name if not s.isdigit() )
    #         self['dtype'] = Inst(dtype_name)

def search_column_in_vals(vals,colname):
    '''
    Header keyword for column names is 'TTYPEn', where 'n' is a number

    'n', btw, is the number we lost and wanna find out here...

    Returns 'n'
    '''
    colname = colname.strip()
    logging.debug("Searching for column '{}' in header".format(colname))
    for n,value in enumerate(vals[0]):
        value = value.strip()
        if value == colname:
            break
    return n


from ._meta_base import MetaBase
class Meta(MetaBase):
    '''
    '''
    def __init__(self,header):
        '''
        'header' is a dictionary with key-values:
        - 'keywords':IPAC keywords section
        - 'comments':comments section (after keywords, typically)
        - 'metacols':lines with name,unit,dtype,null values

        Notice that values are simply lists of text lines; so to
        say that each entry of "metacols" list (value), for example,
        needs to be parsed.
        '''
        super(Meta,self).__init__(header)

        self._init_meta(header)

    def _init_meta(self,header):
        _fields = read_column_names(header)
        self._set_fields(_fields)
        self._init_columns(header)
        self._set_ncols( len(self.colnames) )

    def _init_columns(self,header):
        _columns_dict = self._extract_columns_meta(header)
        self._columns = self._columns_as_dataframe(_columns_dict)
        logging.debug("Columns metadata: \n{!s}".format(self.columns))

    @staticmethod
    def _columns_as_dataframe(cols_dict):
        _mt = list(cols_dict.values())
        dat = dict(list(zip(_mt[0], list(zip(*[list(d.values()) for d in _mt ])))))
        idx = list(cols_dict.keys())
        from booq.table import ADataFrame
        df = ADataFrame(dat,index=idx)
        df.index.name = 'colnames'
        return df

    def _extract_columns_meta(self,header):

        metacols_lines = header['metacols']

        columns_name = parse_columns_header(metacols_lines[0])
        columns_type = parse_columns_header(metacols_lines[1])
        columns_unit = parse_columns_header(metacols_lines[2], False)
        columns_null = parse_columns_header(metacols_lines[3], False)
        assert len(columns_name) == len(columns_type)
        assert len(columns_name) == len(columns_unit)
        assert len(columns_name) == len(columns_null)

        from collections import OrderedDict
        cols = OrderedDict()
        logging.debug("Reading metadata for columns {}".format(self.colnames))
        for colname in self.colnames:
            metacolumn = MetaColumn(colname)
            metacolumn.set_from_header([columns_name,columns_type,
                                        columns_unit, columns_null])
            cols[colname] = metacolumn
        return cols


# Let's work over the columns metadata, assigned to 'metacols' here
# This section of the IPAC format is composed by 4 lines:
# - column names
# - column datatype
# - column unit
# - column null value
def parse_columns_header(line,clean_empty=True):
    line = line.strip('\n')
    line = line.strip()
    sep = '|'
    if line[0] == sep:
        line = line[1:]
    if line[-1] == sep:
        line = line[:-1]
    cols = [ col.strip() for col in line.split('|') ]
    if clean_empty:
        cols = [x for x in cols if x!='']
    return cols

def read_column_names(header):
    # header,metacols = read_metadata(filename)
    metacols_lines = header['metacols']
    column_names = parse_columns_header(metacols_lines[0])
    return column_names

def read_metadata(filename):
    # Now let's read the metadata and then the data
    counter_lines_header = 0
    header = []
    metacols = []
    with open(filename,'r') as fp:
        for i,line in enumerate(fp):
            if line[0] == '\\':
                # Read header lines
                header.append(line)
            elif line[0] == '|':
                # Read columns metadata (name,data type,unit,null value)
                metacols.append(line)
            else:
                break
        counter_lines_header = i
    assert counter_lines_header == len(header)+len(metacols)
    logging.debug("Number of header lines ({:d})+({:d}): {:d}".
                format(len(header),len(metacols),counter_lines_header))
    return header,metacols



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
