import logging

from . import arrays,string,lists

def is_scalar(data):
    '''
    Check whether 'data' is a scalar type

    Scalars are numbers, strings, booleans.
    '''
    from numpy import isscalar as np_isscalar
    return np_isscalar(data)


def is_number(data):
    '''
    Check whether 'data' is a numeric scalar
    '''
    if not is_scalar(data):
        return False
    try:
        data_after_math = int(((data + 1)) / (float(data) + 1))
        looks_num = data_after_math == 1
    except:
        looks_num = False
    return looks_num


def is_array(data,dtype=None):
    '''
    Check whether 'data' is a ~numpy.ndarray

    Optionaly, check for array dtype. Options are:
     - 'numeric'
     - 'string'
     - 'object'
    '''
    from numpy import ndarray
    _is = isinstance(data, ndarray)
    if dtype is None or _is == False:
        return _is
    _dtypes = { 'numeric':arrays.is_numeric,
                'string': arrays.is_string,
                'object': arrays.is_object }
    assert dtype in _dtypes.keys(), "Value '{}' not a valid dtype. Options are: {}".format(dtype,_dtypes.keys())
    return _dtypes[dtype](data)


def list_contents_are_equal(lleft,lright):
    __doc__ = lists.have_same_content.__doc__
    return lists.have_same_content(lleft,lright)


def is_file(filename,filetype=None):
    '''
    Check if 'filename' exist and optionally if of type 'filetype'
    '''
    from os import path
    if not path.isfile(filename):
        logging.debug("Not a (valid) file.")
        return False
    ext = path.basename(filename).split('.')[-1]
    chk = ext.lower() == filetype.lower()
    if not chk:
        logging.debug("A file, but extension and 'filetype' not match.")
    return chk

