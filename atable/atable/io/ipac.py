#-*- coding=utf-8 -*-
import logging

import numpy as np

_dtype_conversion_table = {
    'char'      : str,
    'double'    : float,
    'int'       : int
}
_null_conversion_table = {
    'char'      : 'null',
    'double'    : float('nan'),
    'int'       : -999
}
# _null_conversion_table = {
#     'char'      : None,
#     'double'    : None,
#     'int'       : None
# }

def read(filename, columns=None, rows=None, ucds=None):
    '''
    Read IPAC file lines to list

    NOTE: UCDs are still not supported
    '''
    # If 'rows' is not None, means I'll have to read *some* of them,
    # to read *some* of them I need to know how many they are.
    counter_lines_total = 0
    with open(filename) as fp:
        for i, l in enumerate(fp):
            pass
        counter_lines_total = i + 1
    logging.debug("Total number of lines of (IPAC) file '{}':{:d}".
                format(filename,counter_lines_total))
    del i,l,fp

    # Now let's read the metadata and then the data
    counter_lines_header = 0
    header = []
    metacols = []
    with open(filename,'r') as fp:
        for i,line in enumerate(fp):
            if line[0] == '\\':
                # Read header lines
                header.append(line)
            elif line[0] == '|':
                # Read columns metadata (name,data type,unit,null value)
                metacols.append(line)
            else:
                break
        counter_lines_header = i
    assert counter_lines_header == len(header)+len(metacols)
    logging.debug("Number of header lines ({:d})+({:d}): {:d}".
                format(len(header),len(metacols),counter_lines_header))
    del i,line,fp

    # Let's work over the columns metadata, assigned to 'metacols' here
    # This section of the IPAC format is composed by 4 lines of the file:
    # - column names
    # - column datatype
    # - column unit
    # - column null value
    def parse_columns_header(line,clean_empty=True):
        line = line.strip('\n')
        line = line.strip()
        sep = '|'
        if line[0] == sep:
            line = line[1:]
        if line[-1] == sep:
            line = line[:-1]
        cols = [ col.strip() for col in line.split('|') ]
        if clean_empty:
            cols = [x for x in cols if x!='']
        return cols
    # --
    columns_name = parse_columns_header(metacols[0])

    if columns is None:
        columns = columns_name[:]
    _columns_position = { col:i for i,col in enumerate(columns_name) }
    columns_position = []
    for col in columns:
        assert col in columns_name, "Column '{}' is not in the file".format(col)
        columns_position.append(_columns_position[col])
    assert len(columns)==len(columns_position)
    logging.debug("Columns position to read: {}".
                format(list(zip(columns,columns_position))))
    del _columns_position, col

    columns_type = parse_columns_header(metacols[1])
    columns_unit = parse_columns_header(metacols[2], clean_empty=False)
    columns_null = parse_columns_header(metacols[3], clean_empty=False)
    assert len(columns_name) == len(columns_type)
    assert len(columns_name) == len(columns_unit)
    assert len(columns_name) == len(columns_null)
    assert len(columns_name) >= len(columns)

    # If 'rows' was given guarantee we are working with an array of
    # indexes
    counter_lines_data = counter_lines_total - counter_lines_header
    if rows is None:
        from numpy import arange
        rows = arange(counter_lines_total - counter_lines_header)

    from booq.utils import is_array,is_number
    if is_number(rows):
        from booq.data.utils import sample_rows
        rows = sample_rows(counter_lines_data,rows)
    else:
        rows = np.asarray(rows)
    assert is_array(rows)
    logging.debug("Number of rows to be read: {:d}".format(len(rows)))

    rows = rows + counter_lines_header
    rows = list(rows)
    rows.sort()

    from booq.utils import progressBar
    # pb = progressBar.ProgressTimer(description="Reading file",n_iter=len(rows))
    pb = progressBar.ProgressBar(total=len(rows))

    data = []
    _dtypes = [ _dtype_conversion_table[ctype] for ctype in columns_type ]
    _nulls = [ _null_conversion_table[ctype] for ctype in columns_type ]
    with open(filename,'r') as fp:
        i_old = None
        for i,line in enumerate(fp):
            if len(rows) == 0:
                break
            if line[0] == '\\' or line[0] == '|':
                continue
            if i == rows[0]:
                data_line = []
                for j,dat in enumerate(line.split()):
                    if not j in columns_position:
                        continue
                    dat = dat.strip()
                    if dat == columns_null[j]:
                        dat = _nulls[j]
                    data_line.append(_dtypes[j](dat))
                data.append(data_line)
                _ = rows.pop(0)
                pb.update()
    try:
        pb.close()
    except:
        pb.finish()

    names = columns[:]
    types = [ _dtypes[i] for i in columns_position ]
    units = [ columns_unit[i] for i in columns_position ]
    nulls = [ _nulls[i] for i in columns_position ]
    out = { 'names':names,
            'types':types,
            'units':units,
            'nulls':nulls,
            'data':data    }

    return out
