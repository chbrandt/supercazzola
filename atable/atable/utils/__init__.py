import logging

from . import arrays,string,lists
from .is_misc import is_scalar,is_number,is_array,is_file


def list_contents_are_equal(lleft,lright):
    __doc__ = lists.have_same_content.__doc__
    return lists.have_same_content(lleft,lright)

