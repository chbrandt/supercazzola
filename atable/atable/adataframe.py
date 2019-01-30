import numpy as np

from pandas import DataFrame
class ADataFrame(DataFrame):
    '''
    Add some features to ~pandas.DataFrame
    '''
    _metadata = ['to_table']#,'metatable']

    @property
    def _constructor(self):
        return ADataFrame

    @property
    def _constructor_sliced(self):
        return ASeries

    # @property
    # def metatable(self,filename=None):
    #     if not filename:
    #         return _read_meta_from_dataframe(self)
    #     else:
    #         return _read_meta_from_file(filename)

    def __init__(self,*args,**kwargs):
        super(ADataFrame,self).__init__(*args,**kwargs)

    @staticmethod
    def read(data,*args,**kwargs):
        from .atable import ATable
        __doc__ = ATable.read.__doc__
        tab = ATable.read(data,*args,**kwargs)
        return tab.to_dataframe()

    def write(self, metadata=True, overwrite=False):
        from .atable import ATable
        __doc__ = ATable.write.__doc__
        tab = self.to_table()
        tab.write(metadata=metadata,overwrite=overwrite)

    def to_table(self,raise_index=True,rename_index=None):
        from .atable import ATable
        tab = ATable.from_dataframe(self,raise_index,rename_index)
        tab.meta = self.meta
        return tab

    def describe(self, include='all', showNullIndexes=False):
        print(super(ADataFrame,self).describe(include=include))
        size = len(self)
        print("\nTotal number of rows: {:d} ({:.1e})".format(size,size))
        print("\n-> Has Nil? (How many?)")
        has_nil = self.isnull().apply(np.sum)
        print(has_nil)
        # print "{:d} ({:.3f}%)".format(has_nil,100*float(has_nil)/size)
        if showNullIndexes:
            for c in has_nil.index:
                if not has_nil[c]: continue
                print("\n-> Indexes where column '{}' is null:".format(c))
                print(self[self[c].isnull()].index.values)

    def crop(self,**kwargs):
        for key in kwargs.keys():
            val = kwargs[key]
            assert key in self.columns, "Column '{}' not found in table".format(key)
            assert len(val)==2, "Range '{}':'{}' must have length==2".format(key,val)
        indxs = None
        for key in kwargs.keys():
            val = kwargs[key]
            if indxs is None:
                indxs = self[key].between(*val)
            else:
                indxs &= self[key].between(*val)
        return self.loc[indxs]


from pandas import Series
class ASeries(Series):
    '''
    Add some features to ~pandas.Series
    '''
    _metadata = ['to_table']

    @property
    def _constructor(self):
        return ASeries

    @property
    def _constructor_expanddim(self):
        return ADataFrame

    def __init__(self,*args,**kwargs):
        super(ASeries,self).__init__(*args,**kwargs)

    def to_table(self):
        from .atable import ATable
        tab = ATable.from_series(self)
        return tab

    def describe(self, include='all', showNullIndexes=False):
        print(super(ASeries,self).describe(include=include))
        size = len(self)
        print("\nTotal number of rows: {:d} ({:.1e})".format(size,size))
        print("\n-> Has Nil? (How many?)")
        has_nil = self.isnull().sum()
        print("{:d} ({:.3f}%)".format(has_nil,100*float(has_nil)/size))
        if showNullIndexes:
            for c in has_nil.index:
                if not has_nil[c]: continue
                print("\n-> Indexes where column '{}' is null:".format(c))
                print(self[self[c].isnull()].index.values)

