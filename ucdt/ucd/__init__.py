import six
from ucd._ucd import UCDAtom, UCDWord, UCD, UCDBase
from ucd.ivoa import structure
Roots = structure.init_roots()
del structure


def tests():
    pass


class UCDTree(UCDAtom):
    '''
    '''
    def __init__(self):
        super(UCDTree, self).__init__(None)
        self.ucds = []
        # self.root = []
        # self._init_roots()

    # def _init_roots(self):
    #     for k, v in Roots.items():
    #         self.add_child(v)

    def __str__(self):
        return self.print_tree()

    def load(self, ucds, data=None):
        if not ucds:
            return self
        if data is None:
            data = [None] * len(ucds)
        for u, d in zip(ucds, data):
            self.insert(u, d)
        return load

    def insert(self, ucd, data=None):
        '''
        Insert the pair 'ucd','data'
        '''
        ucd = UCD(ucd, data)
        self.ucds.append(ucd)
        return self

    def search(self, ucd):
        '''
        Search for a 'ucd'

        The idea is to retrieve items with 'ucd' in common
        '''
        if not isinstance(ucd, UCDWord):
            ucd = UCDWord(ucd)
        subtree = self._find_word(ucd)
        return retrieve_all(subtree)

    def all(self):
        items = []
        for atom in self.children:
            items.extend(retrieve_all(atom))
        return items

    def print_tree(self):
        items = print_branch(self.children, 1)
        return '\n'.join(items)

    def _add_ucd(self, ucd, data):
        ucd.add(data)
        self.
        for word in ucd:
            self._add_word(word, data)

    def _add_word(self, word, data):
        assert isinstance(word, UCDWord)
        subtree = self
        for i, atom in enumerate(word):
            # if i == 0:
            #     assert atom.is_root and self.has_child(atom)
            if not subtree.has_child(atom):
                subtree.add_child(atom)
            subtree = subtree.get_child(atom)
        subtree.data.append(data)

    def _find_word(self, word):
        assert isinstance(word, UCDWord)
        subtree = self
        for i, atom in enumerate(word):
            if not subtree.has_child(atom):
                return None
            subtree = subtree.get_child(atom)
        return subtree


def print_leaf(leaf, level):
    lvl = ''.join([' |']*level)
    fmt = '{level}-{leaf}'
    return fmt.format(level=lvl, leaf=str(leaf))


def print_branch(branch, level):
    leaves = []
    for i, leaf in enumerate(branch):
        leaves.append(print_leaf(leaf, level))
        leaves.extend(print_branch(leaf.children, level+1))
    return leaves


def retrieve_all(atom):
    if not atom.children:
        return [atom]
    items = []
    for child in atom.children:
        items.extend(retrieve_all(child))
    return items
