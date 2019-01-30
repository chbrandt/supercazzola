import ucd
t = ucd.UCDTree()
u1 = ucd.UCD('meta.id;meta.main')
t.insert(u1,'col1')
u2 = ucd.UCD('pos.eq.ra;meta.main')
t.insert(u2,'col2')
print('Tree:\n{}'.format(t))
w = ucd.UCDWord('meta.main')
print('Search:', w)
r = t.search(w)
for u in r:
    print(u)
