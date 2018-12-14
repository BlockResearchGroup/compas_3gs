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


# g = 1.5

# assert 1 < g, "value is not between 0 and 1"

# if g > 1:
#     print("test")
#     raise



test = {
    (1, 2): 5,
    (2, 1): 3,
    (2, 2): 1,
}

selection = test[(3, 2)] or test[(2, 1)]

print(selection)








