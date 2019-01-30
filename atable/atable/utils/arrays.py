# -*- coding:utf-8 -*-

import logging

def is_numeric(arrei):
    '''
    Check whether given array is of numeric type
    '''
    if not hasattr(arrei,'dtype'):
        # If not an 'dtype' argument, should not be numpy array either
        assert is_array(arrei)==False
        return False
    return arrei.dtype.kind in 'biful'

def is_object(arrei):
    '''
    Check whether 'arrei' has 'dtype' attribute of object type
    '''
    if not hasattr(arrei,'dtype'):
        # If not an 'dtype' argument, should not be numpy array either
        assert is_array(arrei)==False
        return False
    return arrei.dtype.kind == 'O'

def is_string(arrei):
    '''
    Check whether given array is of string type
    '''
    if not hasattr(arrei,'dtype'):
        # If not an 'dtype' argument, should not be numpy array either
        assert is_array(arrei)==False
        return False
    return arrei.dtype.kind in ['S','U']

def to_str(arrei,null=''):
    '''
    '''
    if is_object(arrei):
        return object2str(arrei,null='')
    else:
        return arrei.astype(str)
to_string = to_str

def object2str(arrei,null=''):
    '''
    Try to cast "object" type array to "string" type

    Null values will be represented as '' (empty string)
    '''
    assert is_object(arrei)
    a = arrei.astype(str)
    ind_nan = a == 'nan'
    ind_nan |= a == 'NaN'
    ind_nan |= a == 'na'
    ind_nan |= a == 'NA'
    a[ind_nan] = null
    return a

def split(arrei, N):
    '''
    Split an array in N pieces
    '''
    logging.debug("input::{0!s}".format(locals()))
    from numpy import arange,array_split
    index = arange(len(arrei))
    arrei_split = [ arrei[idx] for idx in array_split( index,N ) ]
    return arrei_split

def join(arrei_list):
    '''
    Join list of arrays
    '''
    logging.debug("input::{0!s}".format(locals()))
    from numpy import append
    arrei_join = None
    for each in arrei_list:
        if arrei_join is None:
            arrei_join = each
        else:
            arrei_join = append(arrei_join,each)
    return arrei_join

def binning(vector, bins=10, spacing='linear'):
    """
    Apply binning to 1-D array following a spacing rule

    'vector' is a 1D float array from where values will
    be binned (https://en.wikipedia.org/wiki/Data_binning)
    in 'bins' following 'spacing' rule.
    """
    import numpy as np
    spacing_function = {'linear' : np.linspace}

    if spacing is not 'linear':
        spacing = 'linear'

    xmin = vector.min() if xmin is None else xmin
    xmax = vector.max() if xmax is None else xmax

    from booq.utils import is_number
    if is_number(bins):
        bins = spacing_function[spacing](xmin,xmax,bins)
    else:
        assert is_array(bins), "Argument 'bins' should be a number or an array."
    digit = np.digitize(vector,bins)
    return bins[digit]

def binning(vector,nbins,xmin=None,xmax=None,spacing='linear'):
    """
    """
    import numpy as np
    spacing_function = {'linear' : np.linspace}

    if spacing is not 'linear':
        spacing = 'linear'

    xmin = vector.min() if xmin is None else xmin
    xmax = vector.max() if xmax is None else xmax
    nbins = 10 if not (nbins >= 1) else nbins

    bins = spacing_function[spacing](xmin,xmax,nbins+1)
    return bins

def histogram(vector,bins=None):
    """
    Return the histogram of vector given the bins

    Input:
     - vector : array-like
     - bins   : integer
                If 'None', auto define the best number of bins
    """
    import numpy as np
    if bins is None:
        def binswidth(dados):
            import math
            import numpy
            width = 3.49 * numpy.std(dados) * math.pow(dados.size,-1/3.);
            return width;
        _dat = np.asarray(vector);
        _w = binswidth(_dat.ravel());
        _min = _dat.ravel().min();
        _max = _dat.ravel().max();
        bins = (_max-_min)/_w;
        bins = min(100,max(10,bins));
        bins = int(bins)
        del _dat,_w,_min,_max;

    from booq.utils import is_number
    if is_number(bins):
        bins = binning(vector,bins)

    h,b = np.histogram(vector,bins=bins,normed=False)
    assert np.array_equal(b,bins)
    return h,b
