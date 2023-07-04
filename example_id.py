from functools import reduce

digits16 = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F'}
digits32 = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G', 17: 'H', 18: 'I', 19: 'J', 20: 'K', 21: 'L', 22: 'M', 23: 'N', 24: 'O', 25: 'P', 26: 'Q', 27: 'R', 28: 'S', 29: 'T', 30: 'U', 31: 'V'}
digits52 = {0: 'A', 1: 'B', 2: 'C', 3: 'D', 4: 'E', 5: 'F', 6: 'G', 7: 'H', 8: 'I', 9: 'J', 10: 'K', 11: 'L', 12: 'M', 13: 'N', 14: 'O', 15: 'P', 16: 'Q', 17: 'R', 18: 'S', 19: 'T', 20: 'U', 21: 'V', 22: 'W', 23: 'X', 24: 'Y', 25: 'Z', 26: 'a', 27: 'b', 28: 'c', 29: 'd', 30: 'e', 31: 'f', 32: 'g', 33: 'h', 34: 'i', 35: 'j', 36: 'k', 37: 'l', 38: 'm', 39: 'n', 40: 'o', 41: 'p', 42: 'q', 43: 'r', 44: 's', 45: 't', 46: 'u', 47: 'v', 48: 'w', 49: 'x', 50: 'y', 51: 'z'}
digits62 = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G', 17: 'H', 18: 'I', 19: 'J', 20: 'K', 21: 'L', 22: 'M', 23: 'N', 24: 'O', 25: 'P', 26: 'Q', 27: 'R', 28: 'S', 29: 'T', 30: 'U', 31: 'V', 32: 'W', 33: 'X', 34: 'Y', 35: 'Z', 36: 'a', 37: 'b', 38: 'c', 39: 'd', 40: 'e', 41: 'f', 42: 'g', 43: 'h', 44: 'i', 45: 'j', 46: 'k', 47: 'l', 48: 'm', 49: 'n', 50: 'o', 51: 'p', 52: 'q', 53: 'r', 54: 's', 55: 't', 56: 'u', 57: 'v', 58: 'w', 59: 'x', 60: 'y', 61: 'z'}
digits87 = {0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 6: '6', 7: '7', 8: '8', 9: '9', 10: 'A', 11: 'B', 12: 'C', 13: 'D', 14: 'E', 15: 'F', 16: 'G', 17: 'H', 18: 'I', 19: 'J', 20: 'K', 21: 'L', 22: 'M', 23: 'N', 24: 'O', 25: 'P', 26: 'Q', 27: 'R', 28: 'S', 29: 'T', 30: 'U', 31: 'V', 32: 'W', 33: 'X', 34: 'Y', 35: 'Z', 36: 'a', 37: 'b', 38: 'c', 39: 'd', 40: 'e', 41: 'f', 42: 'g', 43: 'h', 44: 'i', 45: 'j', 46: 'k', 47: 'l', 48: 'm', 49: 'n', 50: 'o', 51: 'p', 52: 'q', 53: 'r', 54: 's', 55: 't', 56: 'u', 57: 'v', 58: 'w', 59: 'x', 60: 'y', 61: 'z', 62: '.', 63: ',', 64: '!', 65: '/', 66: '-', 67: '+', 68: '=', 69: '^', 70: '£', 71: '$', 72: '?', 73: '|', 74: '%', 75: ')', 76: '(', 77: '*', 78: ':', 79: ';', 80: '@', 81: '#', 82: '~', 83: '}', 84: '{', 85: '[', 86: ']'}

digitsDict = {16: digits16, 32: digits32, 52: digits52, 62: digits62, 87: digits87}

def revDigits(d:dict[int, str]) -> dict[str, int]:
    return {v: k for k, v in d.items()}

def formatConv(id:str) -> int:
    return int(id.replace('-', '').replace('ISic', ''))

def decToBase(dec:int, base:int) -> str:

    def f(i:int) -> list[int]:
        q = i // base
        r = i % base

        to_app = [q] if q < base else f(q)

        return to_app + [r]
        
    l = f(dec)
    return ''.join([digitsDict[base][item] for item in l])


def baseToDec(baseInpt:str, base:int) -> int:
    
    def f(l:list[str], acc:int) -> int:
        if l == []:
            return acc
        
        v = revDigits(digitsDict[base])[l[0]] * base ** (len(l) - 1)

        return f(l[1:], acc + v)
    
    return f(list(baseInpt), 0)


def compressId(id:str, base:int) -> str:
    return decToBase(formatConv(id), base)

def expandId(id:str, base:int) -> str:
    expanded = str(baseToDec(id, base))
    return 'ISic' + expanded[:-4].rjust(6, '0') + '-' + expanded[-4:]

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
