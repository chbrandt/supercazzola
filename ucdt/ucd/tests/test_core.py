import ucd
# t.insert(u1)
# u2 = ucd.UCD('pos.eq.ra')
# t.insert(u2)
# print('Tree', t)
# r = t.search(u1)
# print('Search:', u1)
# for u in r:
#   print(u)


def test_tree_empty():
    t = ucd.UCDTree()

    assert len(t.all()) == 0


def test_insert():
    u = ucd.UCD('meta.id;meta.main')

    t = ucd.UCDTree()
    t.insert(u, 'info')

    assert len(t.all()) == 2


def test_search():
    um = ucd.UCD('meta.id;meta.main')
    up1 = ucd.UCD('pos.eq.ra;meta.main')
    up2 = ucd.UCD('pos.eq.dec;meta.main')

    cols = ['col1', 'col2', 'col3']

    t = ucd.UCDTree()
    t.insert(um, 'col1')
    t.insert(up1, 'col2')
    t.insert(up2, 'col3')

    r = t.search('meta.main')

    assert len(r) == 1
    assert len(r[0].data) == len(cols)
    assert all(d in cols for u in r for d in u.data)
