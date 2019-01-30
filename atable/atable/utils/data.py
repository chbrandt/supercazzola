# -*- coding:utf-8 -*-
import logging

from .is_misc import is_number

def sample_rows(nrows, fraction=0.1):
    '''
    Return a boolean array uniformly sampled to a certain 'fraction'

    'fraction' accounts for the number of 'True' elements in an array of size
    'nrows * fraction' if 'fraction < 1'. Otherwise, if 'fraction >= 1', the
    size of the output array is 'fraction' itself.
    '''
    import random
    from numpy import asarray
    assert 0<fraction, "ValueError: 'fraction' should be greater than 0"
    if fraction > nrows:
        logging.warning("'fraction > nrows'! Will use the 'nrows' as output size")

    nsamp = int(fraction) if fraction >= 1 else int(fraction * nrows)
    nsamp = min(nrows,nsamp) # when fraction > nrows, needs to be fixed
    nsamp = int(nsamp)
    idx = set()
    while len(idx)<nsamp:
        n = random.randint(0, nrows-1)
        idx.add(n)
    return asarray(list(idx),dtype=int)

def sample_array(data_array, fraction=0.1):
    """
    Return a sample from 'data_array' rows

    The size of the sample will be 'len(data_array) * fraction', if
    'fraction < 1'. If 'fraction >= 1', it is considered as the absolute
    number of rows.

    Sample is the result of a uniform random distribution selection from
    input data.

    Input:
     - data_array : ~numpy.ndarray
            Data from where rows are randomly chosen
     - fraction : int, float
            Number between (0,array'length); limits are non-inclusive.
            If the number is higher (inclusive) than '1', it is assumed to be
            the absolute value for the sample size; otherwise, if between (0,1)
            it is assumed to be the relative, array-length multiplication factor.
    Output:
     - sampled_array : ~numpy.ndarray
            Rows are randomly chosen from a normal distribution, all same columns
    """
    nrows = len(data_array)
    idx = sample_rows(nrows,fraction)
    sample_data = data_array[idx]

    return sample_data


def sample(data, fraction=0.1):
    '''
    Return an array randomly sampled of size('data') * 'fraction'

    If 'data' is a number, a boolean array covered by 'fraction' of True
    elements. If 'data' is an array, a 'fraction' of it is equaly randomly
    chosen.

    Input:
     - data : integer or ~numpy.ndarray instance
            Source for sample array or (if a number) as the size of output array
     - fraction: float or integer
            If 'fraction >= 1', it is used directy as the size of output sample;
            if 'fraction < 1', the size of sample will be 'len(data) * fraction'

    '''
    if is_number(data):
        return sample_rows(data, fraction)
    else:
        assert utils.is_array(data), "'data' does not look like an array"
        return sample_array(data, fraction)
