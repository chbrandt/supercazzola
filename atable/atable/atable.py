import logging
import warnings; warn = warnings.warn

from collections import OrderedDict

import os
import pandas as pd
import numpy as np

from numpy import isnan, array

# base class fot ATable
from astropy.table import Table

# definition of ATable's columns
from .acolumn import AColumn

# our versin of dataframe
from .adataframe import ADataFrame

# the metatable class
#from .ametatable import AMetaTable

from .utils import arrays, is_file


class ATable(Table):
    '''
    Inherits from Astropy's Table and adds to I/O and UCD handlers

    This class adds support for Unified Content Descriptors(UCD [1]_).

    .. [1] http://www.ivoa.net/documents/latest/UCD.html
    '''

    Column = AColumn

    _metatable = None

    @property
    def metatable(self):
        return self._metatable

    def _read_metatable(self, filename=None):
        if filename is None:
            _metatable = _read_meta_from_table(self)
        else:
            _metatable = _read_meta_from_file(filename)
        self._metatable = _metatable

    def _sync_metadata(self):
        '''
        Update table columns' metadata
        '''
        self.metatable._sync_metadata(self)

    @property
    def description(self):
        print(self.metatable.table_description)

    @property
    def columns_description(self):
        warn("Use 'nulls' property instead.", DeprecationWarning)
        print(self.metatable.description)

    @property
    def descriptions(self):
        print(self.metatable.description)

    @property
    def ucds(self):
        return self.metatable.ucd

    @property
    def units(self):
        return self.metatable.unit

    @property
    def dtypes(self):
        return self.metatable.dtype

    @property
    def nils(self):
        warn("Use 'nulls' property instead.", DeprecationWarning)
        return self.metatable.nil

    @property
    def nulls(self):
        return self.nils

    def describe(self):
        '''
        Print table content's summary
        '''
        return ADataFrame(describe(self))


    @classmethod
    def from_dataframe(cls, df, raise_index=True, rename_index=None):
        '''
        Return ATable from pandas.DataFrame 'df'

        Input:
         - df           : pandas.DataFrame
         - raise_index  : bool
                transform df' index into a column
         - rename_index : string
                If 'raise_index', rename index to this value
        '''
        if rename_index:
            df.index.names = [rename_index]
        if raise_index and len(df):
            df = df.reset_index()
        coldefs = cls._define_columns(df, df.columns)
        if not coldefs:
            return cls()
        return cls(coldefs)


    @classmethod
    def from_series(cls, series):
        '''
        Transforms ~pandas.Series to ATable

        Given 'series' index is transformed in column.
        '''
        return cls.from_dataframe(series, raise_index=True)


    def to_dataframe(self, multidimensional_columns='ignore'):
        '''
        Return a pandas.DataFrame

        If multidimensional columns detected, treat them.
        If 'multidimensional_columns' is 'ignore', just ignore respective
        columns, if 'split', split the array into columns corresponding
        position value "_i" appended to the original name.

        Input:
         - multidimensional_columns : options are 'ignore','split'
                How to deal with multidimensional columns
        '''
        nd_cols_action = multidimensional_columns
        nD_cols = detect_multiD_columns(self)
        if nD_cols:
            msg = "Multidimensional columns ({}), '{}'ing it."
            logging.warning(msg.format(nD_cols, nd_cols_action))

            cols = self.colnames
            for c in nD_cols:
                _c = cols.pop(cols.index(c))
                assert c == _c
            adf = super(ATable, self[cols]).to_pandas()

            if multidimensional_columns == 'split':
                for cname in nD_cols:
                    cdata = self[cname].data
                    names = [cname+'_'+str(i+1) for i in range(cdata.shape[1])]
                    df_col = ATable(cdata, names=names).to_pandas()
                    adf = pd.concat([adf, df_col], axis=1)
            else:
                assert multidimensional_columns == 'ignore'
        else:
            adf = super(ATable, self).to_pandas()

        return ADataFrame(adf)
    # ---
    to_pandas = to_dataframe
    # ---


    @classmethod
    def read(cls, *args, **kwargs):
        '''
        If FITS file to read, use ~booq.io.fits interface

        Except from the ``kwargs`` listed below, all other arguments
        are from ~astropy.table.Table .

        kwargs:
         - data : string
                filename to read data from
         - format : string
                filename format. If 'fits', arguments 'columns','rows','ucds' apply
         - columns : list of strings
                column names to be read
         - rows : float, integer or list of integers
                number of rows, or list of rows (0-indented) to read from
                if a float less then 1, consider a fraction of total rows to read
         - ucds : list of strings
                UCDs identifying the columns to be read
         - metatable : string
                metadata filename
         - metaonly : bool
                If True, do not load data, only metadata is read.
         - filter_rows : {column : select-function}
                'select-function' is applied to each row from 'column'
                Many columns can be provided. Slection works as AND
        '''
        #TODO: apply arguments 'columns', 'rows' and 'ucds' to all formats read

        if not bool(kwargs.get('metaonly', False)):
            filename = kwargs.get('data', None)
            if not filename:
                filename = kwargs.get('filename', None)
                if not filename:
                    filename = args[0]
            logging.info("Reading filename {}".format(filename))
            assert filename

            format = kwargs.get('format', None)
            if format is None:
                logging.debug("No 'format' argument, figuring out if FITS.")
                if is_file(filename, 'fits') or is_file(filename, 'fit'):
                    format = 'fits'
                else:
                    format = None

            if format == 'fits':
                logging.debug("FITS file being read.")
                columns = kwargs.pop('columns', None)
                rows = kwargs.pop('rows', None)
                ucds = kwargs.pop('ucds', None)
                filter_rows = kwargs.pop('filter_rows', None)
                tab = cls._read_fits(filename, columns, rows, ucds, filter_rows)
            # elif format == 'ipac':
            #     logging.debug("IPAC file being read.")
            #     columns = kwargs.pop('columns',None)
            #     rows = kwargs.pop('rows', None)
            #     ucds = kwargs.pop('ucds',None) # this is not working so far
            #     tab = cls._read_ipac(filename,columns,rows,ucds)
            elif format == 'cds':
                logging.debug("CDS file being read.")
                readme = kwargs.pop('readme', None)
                tab = super(ATable,cls).read(filename, readme=readme,
                                             format='ascii.cds')
            else:
                logging.debug("Not a FITS file, read it using astropy.table")
                tab = super(ATable, cls).read(*args, **kwargs)
        else:
            tab = ATable()

        metafile = kwargs.get('metatable', None)
        if metafile is None:
            # Back compatibility;
            # the options 'metadata' should be removed in the future.
            metafile = kwargs.get('metadata', None)

        tab._read_metatable(metafile)
        if metafile:
            tab._sync_metadata()

        return tab


    def write(self, *args, **kwargs):
        '''
        Interface astropy.table write to create a backed-up 'overwrite'

        Default behaviour ('overwrite=False') is to move old,
        pre-existent file with the same name to <filename>.BKP
        before write new, same-name file.

        'args' is passed as it is to astropy.table.Table.

        args:
         - args[0] : (first positional argument) string
                Output filename

        kwargs:
         - overwrite : bool [False]
                If False, will add extension "BKP" to eventual same-named file;
                if True, just do what it says, no "BKP" file is created.
         - metatable : string or bool [False]
                Default is False: no metatble file is written.
                If True, writes table's metadata to `metatable.ecsv`.
                For better control, a filename can be given to use as
                metatable's file name.
        ----
        '''
        clobber = kwargs.pop('overwrite', False)
        if not clobber:
            filename = args[0]
            if os.path.isfile(filename):
                os.rename(filename, filename+'.BKP')

        pretty_print = kwargs.pop('pretty_print', False)

        writemeta = kwargs.pop('metatable', False)
        if 'metadata' in kwargs.keys():
            warn('Use `metatable` instead of `metadata`.', DeprecationWarning)
            writemeta = kwargs.pop('metadata', False)
        if writemeta:
            meta = self.metatable
            metafile = 'metatable.ecsv' if writemeta is True else writemeta
            meta.write(metafile, format='ascii.ecsv', pretty_print=pretty_print)

        format = kwargs.get('format', 'fits')
        kwargs.update({'format': format})

        super(ATable, self).write(*args, **kwargs)


    @classmethod
    def from_fits(cls,fts):
        '''
        Transforms ~booq.io.fits.Fits to ~booq.table.ATable.
        '''
        try:
            meta = fts.meta
        except:
            meta = None
        data = fts.data
        columns = fts.colnames
        logging.info("Columns to read: {}".format(columns))

        coldefs = cls._define_columns(data,columns,meta)
        return cls(coldefs)


    @classmethod
    def _read_fits(cls, filename, columns, rows, ucds, filter_rows):
        '''
        Interface with ~booq.io.fits to read fits table
        '''
        from .io import fits
        _hand = fits.open(filename, bool(filter_rows))
        _fits = _hand.read(columns=columns, rows=rows, ucds=ucds, filter_rows=filter_rows)
        tab = cls.from_fits(_fits)
        return tab


    @classmethod
    def _define_columns(cls, data, columns, metadata_columns=None):
        '''
        Define ATable' columns from 'data' and 'columns' names

        If 'metadata_columns' is given, it will be used as metadata to
        the corresponding column defined.

        Input:
         - data : numpy recarray-like structure
                Key-valued data structure, like a dictionary or DataFrame
         - columns : list of strings
                Column names to use for array data retrieval
         - metadata_columns : list of ~booq.table.io.MetaColumn
                List of columns metadata
        '''
        coldefs = OrderedDict()

        logging.debug('Columns to loop over: {!r}'.format(columns))

        for cname in columns:
            logging.debug('Given column name: {!r}'.format(cname))

            # meta = metadata_columns[cname]
            if metadata_columns is not None:
                try:
                    meta = metadata_columns[cname].to_dict()
                except:
                    # logging.warning('Metadata for column {!s} not read. Is it right?'.format(cname))
                    meta = None
            else:
                meta = None

            logging.debug('Column-associated metadata: {!r}'.format(meta))

            # Let's work over the data now..
            column = data[cname]

            # We have to treat different data structures differently..
            if hasattr(column,'values'):
                # we are (probably) dealing with a pandas series/dataframe..
                logging.debug('Column looks like a pandas.Series')

                vector = column.values
                mask = column.isnull().values

                logging.debug('{} has {}/{} null values'.format(cname,sum(mask),len(mask)))
            else:
                # if here, it is (hopefully) a list or any array like object,
                # by all means, we transform into a numpy array..
                logging.debug('Column is a {} instance'.format(type(column)))

                vector = np.array(column)

                #FIXME: this (if) block should evaluate mask using 'vector', not 'column'!
                if arrays.is_numeric(column):
                    logging.debug("'{}' is numeric array'".format(cname))

                    mask = np.isnan(column)

                else:
                    logging.debug("'{}' is non-numeric'".format(cname))
                    assert arrays.is_object(column) or \
                           arrays.is_string(column)

                    mask = ~np.array([ v==v for v in column ])

            # For clear,plain data sets we should be working --ultimately--
            # with either numbers or strings
            # (considering this table to be human-readable structure)
            if arrays.is_object(vector):
                vector = arrays.to_str(vector,null='')

            # If a column name is a tuple/list items are joined into a string
            if isinstance(cname,str):
                name = cname
            else:
                # pandas.MultiIndex, for instance, will use tuples for column names
                name = '_'.join(cname)
            logging.debug('Formatted column name: {}'.format(name))

            # I'll add this line to a dictionary to detach the rest of this function
            # to the lines above (that may become a utility function)
            d = dict(data=vector,name=name,mask=mask,meta=meta)

            if d['mask'].any():
                # coldefs[name] = cls.MaskedColumn(data=vector,name=name,mask=mask,meta=meta)
                coldefs[name] = cls.MaskedColumn(**d)
            else:
                # coldefs[name] = cls.Column(data=vector,name=name,meta=meta)
                d.pop('mask')
                coldefs[name] = cls.Column(**d)

        return coldefs

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
        assert isinstance(ucd,(list,tuple))
        if match == 'any':
            indx = len(self.ucds) * [False]
            for u in ucd:
                logging.debug("UCD being matched: '{!s}'".format(u))
                u = [u]
                indx |= self.ucds.apply(lambda x:x.isin(u))
                # indx |= self.ucds.isin(u)
        else:
            assert match == 'all', "Options for 'match' are ['all','any']"
            indx = self.ucds.apply(lambda x:x.isin(ucd))
        colnames = indx[indx].index.values.tolist()
        logging.debug("Columns got from UCDs: {}".format(colnames))
        return colnames


    @classmethod
    def from_pandas(cls, df, raise_index=True, rename_index=None):
        '''
        Deprecated. Use 'from_dataframe' or 'from_series' instead
        '''
        warn("Use 'from_dataframe'/'from_series' instead.", DeprecationWarning)
        return cls.from_dataframe(df, raise_index, rename_index)

    def dump(self,filename=None,format='csv'):
        """
        Like write, but ease the format and filename use

        If filename is not given, assemble it from column names
        """
        warn("Use 'from_dataframe'/'from_series' instead.", DeprecationWarning)
        ext = '.'+format
        if not filename:
            import re
            cols = self.colnames
            filename = re.sub( '[^0-9a-zA-Z]+', '', '_'.join(cols) )

        if filename[:-(1+len(format))] != '.'+ext:
            filename += ext

        self.write(filename,format=format)


'''
    @classmethod
    def _read_ipac(cls, filename, columns, rows, ucds=None):
        from booq.io import ipac
        res = ipac.read(filename, columns=columns, rows=rows, ucds=ucds)

        names = res['names']
        types = res['types']
        units = res['units']
        nulls = res['nulls']
        data = res['data']
        from astropy.table import Table,MaskedColumn
        cols = []
        for i,_name in enumerate(names):
            _type = types[i]
            _unit = units[i]
            _null = nulls[i]
            _data = [ _dat[i] for _dat in data ]
            _mask = [ _dat == _null for _dat in _data ]
            col = cls.MaskedColumn(data=_data, name=_name, mask=_mask, dtype=_type)
            cols.append(col)
        return cls(cols)
'''

# =====================================================================
# Auxiliary functions
# ===================
def _read_meta_from_table(table):
    '''
    Instantiate ~metatable.MetaTable object from 'table'
    '''
    from .ametatable import AMetaTable
    meta = AMetaTable.read_from_table(table)
    return meta


def _read_meta_from_file(filename):
    from .ametatable import AMetaTable
    meta = AMetaTable.read(filename)
    return meta


def describe(table):
    from collections import OrderedDict
    sts = OrderedDict()

    from .utils import stats
    for col in table.colnames:
        sts[col] = stats.basic(table[col])
    return sts

def detect_multiD_columns(tab):
    cols = tab.colnames
    nD_cols = []
    for c in cols:
        if tab[c].ndim > 1:
            nD_cols.append(c)
    return nD_cols
# =====================================================================

