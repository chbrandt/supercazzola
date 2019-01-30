# -*- coding:utf-8 -*-

def limits(iterable,lim,func,lvl=0):
    """
    Find the limit (min,max) value within an iterable structure.

    Args:
        iterable: iterable object (e.g, [])
            Iterable object where values, one by one, will be compared.
            Object can be a flat or nested association of iterable objects.
        lim: comparable value (e.g, float)
            Initial limiting value to compare. Assume it as a boundary value.
        func: function (e.g, min)
            Comparative function to apply for any pair of values.
            ``func`` should take two values and return the succesfull one.

    Returns:
        Value within ``iterable`` that succeds comparison by ``func``.

    Example:
        >>> a = range(11)
        >>> from random import shuffle
        >>> shuffle(a)
        >>> lmin = findLimit(a,11,min)
        >>> lmax = findLimit(a,-1,max)
        >>> lmin==0
        True
        >>> lmax==10
        True
    """
    # _shift = lvl*'\t'
    #
    # frame = inspect.currentframe()
    # args,_,_,values = inspect.getargvalues(frame)
    # log.debug(_shift+'Input arguments:')
    # for arg in args:
    #     log.debug(_shift+'\t%s : %s' % (arg,values[arg]))

    # log.debug(_shift+'Iterate over: %s' % str(iterable))
    # log.debug(_shift+'\titerable object %s' % id(iterable))
    for it in iterable:
        # log.debug(_shift+'\tcurrent it: %s' % str(it))
        # log.debug(_shift+'\tinput lim: %s' % str(lim))
        if isinstance(it,(list,tuple)):
            # log.debug(_shift+'\tnested structure (%s)' % type(it))
            it = findLimit(it,lim,func,lvl=lvl+1)
            # log.debug(_shift+'\treturned limit: %s' % str(it))
            # log.debug(_shift+'\tlim object %s' % id(it))
        lim = func(it,lim)
        # log.debug(_shift+'\tcurrent lim: %s' % lim)
        # log.debug(_shift+'\tlim object %s' % id(lim))
    return lim

def min(iterable):
    """
    Handy function to find the minimum value inside nested iterables
    """
    return limits(iterable, lim=float('+inf'), func=min)

def max(iterable):
    """
    Handy function to find the maximum value inside nested iterables
    """
    return limits(iterable, lim=float('-inf'), func=max)

def have_same_content(left,right):
    '''
    Check whether two lists *contents* are equal
    '''
    return set(left) == set(right)
