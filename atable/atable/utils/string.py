# -*- coding:utf-8 -*-

def fill(string, fill_with='_'):
    '''
    Fill whitespaces with 'fill_with'

    Whitespaces are any of '[ \t\r\n]+'
    '''
    import re
    char_set = '[ \t\r\n]+'
    s = re.sub(char_set, fill_with, string)
    return s

def clean(string, replace_with=''):
    '''
    Replace non-alphanumerics with 'replace_with'

    Alphanumeric chars are '[0-9a-zA-Z]+'
    '''
    import re
    char_set = '[^0-9a-zA-Z]+'
    s = re.sub(char_set, replace_with, string)
    return s
