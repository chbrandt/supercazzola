# -*- coding:utf-8 -*-

from ._ucd import UCDAtom, UCDWord, UCD

from .ivoa import structure
Roots = structure.init_roots()
del structure
