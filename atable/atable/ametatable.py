# -*- coding:utf-8 -*-
import logging

from astropy.table import Table

from collections import OrderedDict
_METACOLUMNS = OrderedDict()
_METACOLUMNS['index'] = 'colname'
_METACOLUMNS['columns'] = [ 'description',
                            'unit',
                            'ucd',
                            'dtype',
                            'null' ]
_METAGLOBAL = ['description']

from .atable import ATable
_ATTRMAPS = { ATable : {'nil':'null'}}


from .ucd import UCD
def converter_unit(unitname):
    unitname = '' if unitname is None else str(unitname)
    try:
        from astropy.units import Unit
        unt = Unit(unitname,parse_strict='warn')
    except:
        from astropy.units import UnrecognizedUnit
        unt = UnrecognizedUnit
    return unt

_CONVERTER = {  'ucd':          UCD,
                'unit':         lambda x:converter_unit(x),
                'dtype':        lambda x:x,
                'null':         lambda x:x,
                'description':  lambda x:x}


from .adataframe import ADataFrame
class AMetaTable(ADataFrame):
    '''
    Use ~booq.ADataFrame to manage a set of metadata from booq's ATable

    This class will use the data part -- columns and rows -- to store
    metadata of a third party table, where ``rows`` represent each
    column of that table (first column, the name of that table columns)
    and the ``columns`` represent each metadatum of that table's columns.
    The ``meta`` component is to be used as the (third party) table's
    metadata.
    '''
    # =================================================================
    # Definition of '_constructor' is mandatory when inheriting
    # from pandas.DataFrame
    @property
    def _constructor(self):
        return AMetaTable

    # As well as the definition of extra members in '_metadata'
    _metadata = ['_index',
                 '_columns',
                 '_global',
                 '_init_skel',
                 '_copy_global_meta',
                 'read_from_table',
                 'extract',
                 'read_from_file',
                 'read',
                 'description',
                 'describe',
                 '_meta',
                 '_set_meta',
                 '_get_meta',
                 'meta']
    # =================================================================

    # _columns for the third-table columns' metadata attributes
    _columns = _METACOLUMNS['columns']
    _index   = _METACOLUMNS['index']
    _global  = _METAGLOBAL

    # _meta goes for third-table metadata
    _meta = None

    def _set_meta(self,meta):
        assert isinstance(meta,dict)
        self._meta = meta

    def _get_meta(self):
        return self._meta#.copy()

    meta = property(_get_meta, _set_meta, doc="Get/Set table's metadata")

    @property
    def table_description(self):
        return self.meta['description']

    # @property
    # def description(self):
    #     return self['description']
    #
    # @property
    # def ucd(self):
    #     return self['ucd']
    #
    # @property
    # def unit(self):
    #     return self['unit']
    #
    # @property
    # def dtype(self):
    #     return self['dtype']
    #
    # @property
    # def nil(self):
    #     return self['nil']

    def pprint(self):
        print()
        print('Description:')
        print('============')
        desc = self.table_description
        if len(desc) > 100:
            _i = 0
            _j = 0
            _lines = []
            while _j < len(desc)-1:
                _i = _j
                _j += min(72,len(desc)-_j) - 1
                while desc[_j] != ' ' and _j < len(desc)-1:
                    _j += 1
                _j += 1
                _lines.append(desc[_i:_j])
            desc = '\n\t'.join(_lines)
        print('\t{}'.format(desc))
        print()
        print()
        print('MetaTable:')
        print('==========')
        import pandas
        pandas.set_option('expand_frame_repr', False)
        print(self)


    @classmethod
    def read_from_file(cls, filename, format='ascii.ecsv'):
        '''
        Reads 'filename' to ~AMetaTable

        Input:
         - filename : string
            Name of filename containing metadata
         - format : string
            Name of the format 'filename' is written
            Default option is 'ascii.ecsv'
        '''
        table = Table.read(filename, format=format)

        # Let's guarantee we have all necessary columns
        if cls._index not in table.colnames:
            logging.error("No '{!s}' found in metadata table.".format(cls._index))
            return None

        rownames, columns = cls._init_skel()

        rownames = table[cls._index]
        for metaname in cls._columns:
            if metaname not in table.colnames:
                metavalue = [None] * len(rownames)
            else:
                metavalue = table[metaname]
            columns[metaname] = [_CONVERTER[metaname](mv) for mv in metavalue]

        tab = cls(columns, index=rownames)
        tab.index.names = [cls._index]

        # copy table's meta data
        tab.meta = cls._copy_global_meta(table)
        return tab
    # ---
    read = read_from_file
    # ---

    @classmethod
    def read_from_table(cls, table):
        '''
        Read ~astropy.table.Table columns' metadata

        Metadata read are the ones in _METACOLUMNS/_ATTRMAPS

        Input:
         - table : ~booq.table.ATable, ~astropy.table.Table
            Catalog of interest

        Output:
         - ~booq.table.ADataFrame
            Metadata table extracted
        '''
        assert isinstance(table, Table)

        # table's column names turn to be this table's index
        rownames, columns = cls._init_skel()

        for colname in table.colnames:
            rownames.append(colname)
            for metaname in cls._columns:
                try:
                    _amap = _ATTRMAPS[table.__class__]
                    attrname = _amap[metaname]
                except:
                    attrname = metaname
                try:
                    column = table[colname]
                    metavalue = getattr(column, attrname)
                except:
                    metavalue = None
                columns[metaname].append(_CONVERTER[metaname](metavalue))

        tab = cls(columns, index=rownames)
        tab.index.names = [cls._index]

        # copy table's meta data
        tab.meta = cls._copy_global_meta(table)
        return tab
    # ---
    extract = read_from_table
    # ---


    def to_table(self):
        '''
        Transform to ~booq.table.ATable
        '''
        table = super(AMetaTable, self).to_table(raise_index=True)
        return table


    def write(self, filename='metatable.ecsv', format='ascii.ecsv',
              pretty_print=False):
        '''
        Write metatable to filename in ECSV format

        Input:
         - filename : string
            Name of file to write metadata table.
         - format : string
            Format for 'filename'. Default is 'ascii.ecsv'
        '''
        table = self.to_table()
        table.write(filename, format=format)
        # This is ugly, but works and I don't want to get into the
        # details of using file objects and so on...
        # The idea here is to take the just-written file (format ecsv)
        # which is working and give it a better/cleaner view; such
        # cleaner view is a properly tabulate table file.
        if pretty_print and format in ('ascii.ecsv', 'ascii.csv'):
            with open(filename, 'r') as fp:
                lines = []
                for line in fp.readlines():
                    if line[0] != '#':
                        break
                    lines.append(line.strip())
            df = self.copy()
            df.columns.name = df.index.name
            df.index.name = None
            ts = df.to_string()
            lines.extend(ts.split('\n'))
            with open(filename, 'w') as fp:
                fp.write('\n'.join(lines))


    @classmethod
    def _copy_global_meta(cls, table):
        assert cls._meta is None
        _meta = {k: None for k in cls._global}
        try:
            tmt = table.meta
            _meta.update(tmt)
        except:
            pass
        return _meta


    @classmethod
    def _init_skel(cls):
        from collections import OrderedDict
        columns = OrderedDict()
        for colname in cls._columns:
            columns[colname] = []
        rownames = []
        return rownames, columns


    def _sync_metadata(self, table):
        '''
        Update table columns' metadata
        '''
        # First let's invert the attributes map from 'metatable' module
        _amap = _ATTRMAPS[table.__class__]

        # Now, for each column of 'this' table..
        for colname in table.colnames:
            column = table[colname]
            # update each of attribute given by metatable
            # (attributes are metatable'columns)
            for metaname in self.columns:
                try:
                    attrname = _amap[metaname]
                except:
                    attrname = metaname
                value = self.loc[colname,metaname]
                value = value if value==value else None
                if hasattr(column,attrname):
                    setattr(column,attrname,value)
                else:
                    logging.error('Column {} has no attribute {}'.format(colname,attrname))

