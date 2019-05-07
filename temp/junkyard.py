from itertools import tee


p = [-2, 0, -2, 3, 7, 1]


print(p[::len(p)-1])




c = {
    'a' : 0,
    'b' : 3,
    'c' : -2,
    'd' : 4,
    'e' : 1
}

print(sorted(c.values()))




a = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
b = [0, 3]


d = [a[i] for i in b]


for index, value in enumerate(a):
    print(index, value)








def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

m = pairwise(a)
for pair in m:
    print(pair)


f = {
    0: 1,
    1: 9,
    2: 4,
    3: 7,
    4: 2,
    5: 8
}

e = [f[i] for i in b]


print(e)

print (5.2 % 2)


test = {
    (1, 2): 5,
    (2, 1): 3,
    (2, 2): 1,
}


q = set([(1, 2), (3, 4), (5, 6)])


if (1, 2) in q:
    print('yes')


for number in a:
    if number % 2 == 0:
        continue

    print(number)
    print('no')



fs = frozenset((1, 2))

x, y = list(fs)

print(x, y)



text = 'hello'

print(str(text))


def test_func():
    print('a')


test_func_dup = test_func


test_func_dup()


class Foo():
    a = 5


testclass = Foo()

print(isinstance(testclass, Foo))




def faces():
    faces = {0: [], 1: [], 2: [], 3: []}
    for fkey in faces:
        yield fkey, faces[fkey]



for fkey, attr in faces():
    print(fkey)


m = [0, 1, 2, 3]

if len(m) < 5:
    print('no')

a, b, c = m[0:3]

print(a, b, c)

