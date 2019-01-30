# -*- coding:utf-8 -*-

from string import letters
from string import digits

def fill(word, fill_with='_'):
    '''
    Fill whitespaces with 'fill_with'

    Whitespaces are any of '[ \t\r\n]+'
    '''
    import re
    char_set = '[ \t\r\n]+'
    s = re.sub(char_set, fill_with, word)
    return s

def clean(word, replace_with=''):
    '''
    Replace non-alphanumerics with 'replace_with'

    Alphanumeric chars are '[0-9a-zA-Z]+'
    '''
    import re
    char_set = '[^0-9a-zA-Z]+'
    s = re.sub(char_set, replace_with, word)
    return s

def is_empty(word):
    '''
    Check whether given string is whitespace-filled
    '''
    return not bool(word and word.strip())

def is_alphanumeric(word):
    '''
    Check whether given string contains *only* alphanumeric digits
    '''
    char_set = letters+digits
    return all( s in char_set for s in word )

def is_letter(word):
    '''
    Check whether 'word' contains *only* letters
    '''
    return all( s in letters for s in word )

def is_numeric(word):
    '''
    Check whether 'word' contains only numbers
    '''
    return all( s in digits for s in word )
