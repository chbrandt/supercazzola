# -*- coding:utf-8 -*-
'''
This module holds some utilities for handling UCDs.

The tools in here are basically interface (or alike) for
the ones offered by Vizier at 'http://cds.u-strasbg.fr/UCD/tools.htx'.
'''

def ucd_from_description(description,get='best'):
    '''
    Get a UCD suggestions from 'description'

    GAVO service for UCDs ('http://dc.zah.uni-heidelberg.de/ucds/ui/ui/form') is used

    Input:
     - description : string
            Description of a column
     - get : string
            Options are ['best','all'], the 'best' of suggestions or 'all' of them

    Output:
     - If 'get=best' return a tuple with (suggested ucd,{'probability','description'});
        Otherwise, if 'get=all' return a {sugested ucds,{'probability','description'}}
    '''

    _form_url = 'http://dc.zah.uni-heidelberg.de/ucds/ui/ui/form'
    _rest_url = '?__nevow_form__=genForm&_FORMAT=txt&submit=Go&description='
    _search_url = _form_url+_rest_url

    import requests
    r = requests.post("{}'{}'".format(_search_url,description))
    from collections import OrderedDict
    _ucd = OrderedDict()
    for l in r.iter_lines():
        l = l.split()
        _ucd[l[1]] = {'probability':l[0], 'description':' '.join(l[2:])}
        # if get == 'best':
        #     break # Yes, runs only once; first line is the highest scored ucd.
    if get == 'best':
        _ucd = _ucd.popitem(last=False)
    return _ucd

def translate_ucd1_to_1p(ucd1):
    '''
    Translate UCD version 1 to 1+

    Vizier UCD tools are used (http://cds.u-strasbg.fr/doc/UCD/).
    '''
    from ucd.ivoa import ucd1_to_1p
    reload(ucd1_to_1p)
    map_of_words = ucd1_to_1p.get_words_map()
    return map_of_words[ucd1]
