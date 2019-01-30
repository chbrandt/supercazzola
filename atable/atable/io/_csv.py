"""Module to read/write ascii catalog files (CSV and DS9)"""

##@package catalogs
##@file ascii_data

"""
The following functions are meant to help in reading and writing text CSV catalogs
as well as DS9 region files. Main structure used is dictionaries do deal with catalog
data in a proper way.
"""

import sys
import logging
import re
import string

# ---
def write(columns, fieldnames=None, filename='cat.csv', mode='w', delimiter=','):
    """
    Write a CSV catalog from given dictionary contents

    Given dictionary is meant to store lists of values corresponding to key/column in the
    csv file. So that each entry 'fieldnames' is expected to be found within 'columns'
    keys, and the associated value (list) will be written in a csv column

    Input:
     - columns     {str:[]} : Contents to be write in csv catalog
     - fieldnames     [str] : List with fieldnames/keys to read from 'columns'
     - filename         str : Name of csv catalog to write
     - mode             str : Write a new catalog, 'w', or append to an existing one, 'a'.
     - delimiter        str : Delimiter to use between columns in 'filename'

    Output:
     * If no error messages are returned, a file 'filename' is created.


    Example:

    >>> D = {'x':[0,0,1,1],'y':[0,1,0,1],'id':['0_0','0_1','1_0','1_1'],'z':[0,0.5,0.5,1]} #\
    >>> fields = ['id','x','y','z'] #\
    >>> #\
    >>> dict_to_csv( D, fields, filename='test.csv') #\
    >>> #\
    >>> import os #\
    >>> #\

    ---
    """
    import csv

    dictionary  = columns.copy()

    if fieldnames is None:
        fieldnames = list(dictionary.keys())

    for k in fieldnames:
        if type(dictionary[k])!=type([]) and type(dictionary[k])!=type(()):
            dictionary[k] = [dictionary[k]]

    logging.debug("Fields being written to (csv) catalog: %s",fieldnames)

    max_leng = max([ len(dictionary[k])  for k in fieldnames if type(dictionary[k])==type([]) ])

    for k in fieldnames:
        leng = len(dictionary[k])
        if leng != max_leng:
            dictionary[k].extend(dictionary[k]*(max_leng-leng))

    catFile = open(filename,mode)
    catObj = csv.writer(catFile, delimiter=delimiter,
                        quoting=csv.QUOTE_NONNUMERIC,
                        skipinitialspace=True)
    catObj.writerow(fieldnames)

    LL = [ dictionary[k] for k in fieldnames ]
    for _row in zip(*LL):
        catObj.writerow(_row)
    catFile.close()

    return

# ---
def read(filename, fieldnames=None, comment='#', delimiter=',', dialect='excel', header_lines=1):
    """
    Read CSV catalog and return a dictionary with the contents

    read( filename, fieldnames, ...) -> {}

     To each column data read from 'filename' is given the respective 'fieldnames'
    entry; if 'fieldnames' is None, the first line *right before the table*
    is assumed for the names.
     Lines begging by 'comment' will be saved in a special key (called "comments").
    Particularly, lines begging with 'comment', followed by *one* string, a colon
    and (at the 4th field) whatever value(strings), will be a single-valued key/value
    entry in the dictionary. This is to be used as a valued for further processing.
    '''
    # pi_value : 3.1415
    (...)
    '''

    Input:
     - filename     :: str
        Name of csv catalog to read
     - fieldnames   :: list/tuple of str
        Columns to be read from catalog
     - comment      :: str
        Comment line character
     - header_lines :: int
        Number of lines to remove from the head of 'filename'
     - delimiter    :: str
        Delimiter to use between columns in 'filename'
     - dialect      :: str
        CSV file fine structure (See help(csv) for more info)

    Output:
     - {*fieldnames}

    Example:

#    >>> import os
#    >>> os.system('grep -v "^#" /etc/passwd | head -n 3 > test.asc')
#    0
#    >>> s = os.system('cat test.asc')
    nobody:*:-2:-2:Unprivileged User:/var/empty:/usr/bin/false
    root:*:0:0:System Administrator:/var/root:/bin/sh
    daemon:*:1:1:System Services:/var/root:/usr/bin/false
    >>>
    >>> D = dict_from_csv('test.asc',['user','star'],delimiter=':',header_lines=0)
    >>>

    ---
    """

    #Initialize csv reader
    try:
        cfile = open(filename,'r');
    except:
        return None

    # ---
    import re
    class utils:

        @staticmethod
        def iscomment(line,comment='#'):
            if line[0]!=comment:
                return False
            return re.sub('#\s*','',line)

        @staticmethod
        def isvariable(line,sep=':'):
            _l = line.split(sep)
            if len(_l)!=2:
                return False
            _k = _l[0].strip()
            _v = _l[1].strip()
            return {_k:_v}

        @staticmethod
        def parseline(line):
            return re.sub('^\s*','',line)     # remove first whitespace char

    # ---

    # Initialize output dictionary
    tout = { 'comments' : [],
             'variables': {} }
    cnt = 0
    for line in cfile.readline():
        comment_line = utils.iscomment(line)
        if comment_line != False:
            cnt+=1
            comment_var = utils.isvariable(comment_line)
            if comment_var != False:
                tout['variables'].update(comment_var)
            else:
                tout['comments'].update(comment_line)
        else:
            if re.sub('^\s*$','',line) is '' and cnt==0:
                print("error: first line os file is empty. Empty file? Check it.")
                return False
            cfile.seek(cnt)


    if fieldnames is not None:
        for k in fieldnames:
            tout[k] = [];
    else:
        assert False
    lixo_head = [ next(catFile) for i in range(header_lines) ];

    catObj = csv.DictReader(catFile,fieldnames,delimiter=delimiter,dialect=dialect);
    for row in catObj:
        for k in fieldnames:
            Dout[k].append(row[k]);

    return Dout;


if __name__ == "__main__":
    import doctest;
    doctest.testmod()
