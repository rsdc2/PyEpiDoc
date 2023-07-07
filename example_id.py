from pyepidoc.epidoc.ids import *

# ID = 'ISic999999-9999'
# ID = 'ISic000001-0010'
b = 52
x = compress('ISic035001-9999', b)
print(x)

# z = compress('ISic004515-9999', b)
# print(z)
y = decompress('zzzzz', b)
print(y)
# v = 4097
# print(v)
# x = decToBase(v, b)
# print(x)
# y = baseToDec(x, b)
# print(y)
