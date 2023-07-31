

def generate_n():
    x = 0
    while x < 10:

        yield x
        x += 1

def generate_isic_ids(max):

    r1 = iter(range(0, max))
    for i in r1:
        r2 = iter(range(0, 1000))
        for j in r2:
            inscription_id = 'ISic' + str(i).rjust(6, '0') + '-' + str(j).rjust(4, '0')
        
            yield inscription_id

def generate_n_():
    x = 0

    def f(z):
        yield z

    y = f(x)
    x += 1
    return y

# for i in generate_n():
#     print(i)

# print(next(generate_n()))
# print(next(generate_n()))
for i in generate_isic_ids(10):
    print(i)