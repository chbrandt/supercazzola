# -*- coding:utf-8 -*-
import logging

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
