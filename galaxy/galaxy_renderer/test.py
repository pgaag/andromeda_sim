def r1(a1, a2):
    out = []
    for i in range(len(a1)):
        try:
            out += [(a1[i], a2[i])]
        except IndexError:
            print("Index error!")
    print(out, ',', len(out))
    return out
class M:
    def __init__(self, b1, b2):
        self.b1, self.b2 = b1, b2
        self.d = dict(r1(b1, b2))
    @property
    def my_p(self):
        return self.d
    @my_p.setter
    def my_p(self, par):
        print('aufruf my_p.setter')
        self.d = par


if __name__ == '__main__':
    t1, t2 = ('A', 'B', 'C'), (1, 2)
    m = M(t1, t2)
    d = m.my_p
    print(d['B'])
    try:
        print(d['D'])
    except KeyError:
        print('Fehler')
    m.my_p = {'1': 'eins', '2': 'zwei'}
    print(m.my_p['2'])
