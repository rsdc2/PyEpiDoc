from pyepidoc.epidoc.ids import *

ID = 'ISic999999-9999'
ID = 'ISic000001-0010'
b = 52
x = compressId(ID, b)
print(x)
y = expandId('aPjksM', b)
print(y)
# v = 4097
# print(v)
# x = decToBase(v, b)
# print(x)
# y = baseToDec(x, b)
# print(y)
