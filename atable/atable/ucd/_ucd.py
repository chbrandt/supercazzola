# -*- coding:utf-8 -*-

from collections import OrderedDict

def _is_string(word):
    import sys
    if sys.version_info.major == 3:
        # Python 3
        return isinstance(word,str)
    else:
        # Python 2
        return isinstance(word,(str,unicode))

class UCDBase(object):
    def __eq__(self,other):
        return self.__repr__() == repr(other)

    def copy(self):
        return eval(self.__repr__())

class UCDAtom(UCDBase):
    '''
    '''
    def __init__(self,atom,family=None,description=None,parent=None,children=None):
        self._atom = atom
        self._family = family
        self._description = description
        self._parent = parent

        assert not children
        self._children = []

    def __eq__(self,other):
        return str(self) == str(other)

    def __nonzero__(self):
        return not self._atom is None

    def __str__(self):
        return str(self._atom)

    def __repr__(self):
        _args = '{atom!r},{family!r},{description!r},{parent!r},{children!r}'.format(
                atom = self._atom,
                family = self._family,
                description = self._description,
                parent = self._parent,
                children = self._children
        )
        return 'UCDAtom({args})'.format(args=_args)

    def has_child(self,atom):
        return atom in self.children

    def add_child(self,atom):
        assert isinstance(atom,UCDAtom)
        if not atom in self._children:
            self._children.append(atom)

    def get_child(self,atom):
        assert isinstance(atom,UCDAtom)
        i_child = self.children.index(atom)
        return self.children[i_child]

    @property
    def is_root(self):
        return not self._parent

    @property
    def family(self):
        return self._family

    @property
    def parent(self):
        return self._parent

    @property
    def children(self):
        return self._children

    @property
    def description(self):
        return self._description

    @property
    def scope(self):
        return self.family

class UCDWord(UCDBase):
    '''
    '''
    def __init__(self, word, namespace='ivoa', description=None):
        assert _is_string(word)
        #TODO: we need an assert for the namespace. It would go through a list of available ones in the lib
        self._word = self.process_word(word)
        self._namespace = namespace
        self._description = description

    def __len__(self):
        return len(self._word)

    def __iter__(self):
        for a in self._word:
            yield a

    def __str__(self):
        _ns,_word = self.to_string().split(':')
        if _ns == 'ivoa':
            return _word
        return ':'.join([ _ns,_word ])

    def __repr__(self):
        _ns,_word = self.to_string().split(':')
        _args = '{word!r},{namespace!r},{description!r}'.format(
                word = _word,
                namespace = _ns,
                description = self._description
        )
        return 'UCDWord({args})'.format(args=_args)

    def to_string(self):
        _word = '.'.join([ str(atom) for atom in self._word ])
        _ns = self._namespace
        return ':'.join([ _ns,_word ])

    def process_word(self,word):
        out = list()

        def clean_word(word,separator='.'):
            '''
            A UCD word can have '.' in it, and probably a delimiting ';'

            Anything after an possible ';' will be cutout, as well as trailing spaces.
            '''
            assert _is_string(word)
            words = word.split(';')
            word = words[0]
            word = word.strip()
            return word
        assert word == clean_word(word), "more then one ucd-word given ('{}'), I can handle only one".format(word)

        #REVIEW: with this local import I skip a circular reference between Roots and UCDAtom. Not really proud of it... õ.O
        # from booq.ucd import Roots
        atoms = word.split('.')

        atom_root = atoms[0]
        # assert Roots.has_key(atom_root)
        # REVIEW: decide whether root has to be copied (so forming a completely new tree)
        # atom = Roots[atom_root].copy()
        # out.append(atom)
        # parent = atom
        parent = None
        for atom in atoms:
            atom = UCDAtom(atom, parent=parent)
            out.append( atom )
            parent = atom
        for i_parent,i_child in zip(range(len(out)),range(1,len(out))):
            atom = out[i_parent]
            child = out[i_child]
            atom.add_child(child)
        return out

    @property
    def root(self):
        return self._word[0]
    family = root

    @property
    def scope(self):
        return self.root.scope

    def isin(self,scope):
        if _is_string(scope):
            _isin = scope in str(self)
        else:
            _isin = any([ self.isin(str(scp)) for scp in scope ])
        return _isin

class UCD(UCDBase):
    '''
    '''
    def __init__(self,ucd=None):
        '''
        Input:
         - ucd : str,unicode
                A (UCD) composite-word
        '''
        if isinstance(ucd,UCD):
            self._ucd = ucd.copy()
        else:
            # assert _is_string(ucd) or ucd is None, "{}".format(type(ucd))
            self._ucd = self.def_ucd(ucd)

    def __eq__(self,other):
        if _is_string(other):
            other = UCD(other)
        return self.__repr__() == repr(other)

    def __ne__(self,other):
        return not self == other

    def __nonzero__(self):
        return self.__len__()

    def __len__(self):
        return len(self._ucd)

    def __iter__(self):
        for w in self._ucd:
            yield w

    def __str__(self):
        return ';'.join([ str(w) for w in self ])

    def __repr__(self):
        _args = '{ucd!r}'.format(ucd=str(self))
        return 'UCD({args})'.format(args=_args)

    def to_string(self):
        return ';'.join([ w.to_string() for w in self ])

    @staticmethod
    def def_ucd(word):
        #TODO: implement 'unknown' UCD
        # out = OrderedDict()
        out = list()
        try:
            word = word.strip()
        except:
            # not a string...tchau!
            return out
        if word is None or word == '':
            return out
        from astropy.io.votable import ucd
        _nw = ucd.parse_ucd(word,check_controlled_vocabulary=True,has_colon=True)
        for ns,w in _nw:
            _ucd = UCDWord(w,ns)
            # out[_ucd] = None
            out.append(_ucd)
        return out

    @property
    def words(self):
        return [ w for w in self ]

    @property
    def primary(self):
        _it = iter(self)
        return _it.next()

    @property
    def family(self):
        return self.primary.family

    @property
    def scope(self):
        return [ w.scope for w in self ]

    def isin(self,scope):
        '''
        Check whether ucd is related to/within 'scope'

        'scope' is another UCD or a word
        '''
        if _is_string(scope):
            scope = [scope]
        _isin = sum([ w.isin(scope) for w in self ])
        return _isin == len(scope)

