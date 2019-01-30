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
import csv
import re
import string

def write_ds9cat(x,y,size=20,marker='circle',color='red',outputfile='ds9.reg',filename='None'):
    """
    Function to write a ds9 region file given a set of centroids

    It works only with a circular 'marker' with fixed
    radius for all (x,y) - 'centroids' - given.

    Input:
     - x : int | []
        X-axis points
     - y : int | []
        Y-axis points
     - size : int | []
     - marker : str | [str]
     - outputfile : str | [str]

    Output:
     <bool>

    Example:

    >>> write_ds9cat(x=100,y=100,outputfile='test.reg')
    >>>
    >>> import os
    >>> s = os.system('cat test.reg')
    # Region file format: DS9 version 4.1
    # Filename: None
    global color=green dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1
    image
    circle(100,100,20) # color=red
    >>>
    >>>
    >>>
    >>> write_ds9cat(x=[1,2],y=[0,3],outputfile='test.reg',size=[10,15],marker=['circle','box'])
    >>>
    >>> s = os.system('cat test.reg')
    # Region file format: DS9 version 4.1
    # Filename: None
    global color=green dashlist=8 3 width=1 font="helvetica 10 normal" select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1
    image
    circle(1,0,10) # color=red
    box(2,3,15,15,0) # color=red
    >>>

    """


    try:
        if len(x) != len(y):
            print("X and Y lengths do not math. Check their sizes.", file=sys.stderr);
            return False;
    except:
        x = [x];
        y = [y];

    centroids = list(zip(x,y));
    length = len(centroids);

    # Lets verify if everyone here is a list/tuple:
    #
    try:
        len(size);
    except TypeError:
        size = [size];
    _diff = max(0,length-len(size))
    if _diff:
        size.extend([ size[-1] for i in range(0,_diff+1) ]);
    #
    if type(marker) == type(str()):
        marker = [marker];
    _diff = max(0,length-len(marker))
    if _diff:
        marker.extend([ marker[-1] for i in range(0,_diff+1) ]);
    #
    if type(color) == type(str()):
        color = [color];
    _diff = max(0,length-len(color))
    if _diff:
        color.extend([ color[-1] for i in range(0,_diff+1) ]);

    output = open(outputfile,'w');
    # DS9 region file header
    output.write("# Region file format: DS9 version 4.1\n");
    output.write("# Filename: %s\n" % (filename));
    output.write("global color=green dashlist=8 3 width=1 font=\"helvetica 10 normal\" ");
    output.write("select=1 highlite=1 dash=0 fixed=0 edit=1 move=1 delete=1 include=1 source=1\n");
    output.write("image\n");

    for i in range(length):
        if marker[i] == 'circle':
            output.write("circle(%s,%s,%s) # color=%s\n" % (x[i],y[i],size[i],color[i]));
        elif marker[i] == 'box':
            output.write("box(%s,%s,%s,%s,0) # color=%s\n" % (x[i],y[i],size[i],size[i],color[i]));

    output.close();

    return

# ---

def read_ds9cat(regionfile):
    """ Function to read ds9 region file

    Only regions marked with a 'circle' or 'box' are read.
    'color' used for region marks (circle/box) are given as
    output together with 'x','y','dx','dy' as list in a
    dictionary. The key 'image' in the output (<dict>) gives
    the filename in the 'regionfile'.

    Input:
     - regionfile   :   ASCII (ds9 format) file

    Output:
     -> {'image':str,'x':[],'y':[],'size':[],'marker':[],'color':[]}


    Example:

    >>> write_ds9cat(x=[1,2],y=[0,3],outputfile='test.reg',size=[10,15])
    >>>
    >>> D = read_ds9cat('test.reg')
    >>>

    """

    D_out = {'filename':'', 'marker':[], 'color':[], 'x':[], 'y':[], 'size':[]};

    fp = open(regionfile,'r');

    for line in fp.readlines():

        if (re.search("^#",line)):
            if (re.search("Filename",line)):
                imagename = string.split(line,"/")[-1];
                D_out['filename'] = re.sub("# Filename: ","",imagename).rstrip('\n');
            continue;

        else:
            try:
                _cl = re.search('(?<=color\=).*',line).group();
                color = string.split(_cl)[0];
            except AttributeError:
                pass;

            if re.search("circle",line) or re.search("box",line):
                marker = string.split(line,"(")[0];
            else:
                continue;

            try:
                _fg = re.sub("\)","",re.search('(?<=box\().*\)',line).group());
                x,y,dx,dy = string.split(_fg,sep=",")[:4];
                D_out['x'].append(eval(x));
                D_out['y'].append(eval(y));
                D_out['size'].append(max(eval(dx),eval(dy)));
                D_out['color'].append(color);
                D_out['marker'].append(marker);
                continue;
            except AttributeError:
                pass;

            try:
                _fg = re.sub("\)","",re.search('(?<=circle\().*\)',line).group());
                x,y,R = string.split(_fg,sep=",")[:3];
                D_out['x'].append(eval(x));
                D_out['y'].append(eval(y));
                D_out['size'].append(eval(R));
                D_out['color'].append(color);
                D_out['marker'].append(marker);
                continue;
            except AttributeError:
                pass;

    fp.close();
    return D_out;

# ---
if __name__ == "__main__":
    import doctest;
    doctest.testmod()
