from pyepidoc.epidoc.ids import *
import random


def test_id_correct_expansion():
    ID = 'ISic099999-9999' # 'ISic999999-9999'
    b = 52
    x = compress(ID, b)
    y = decompress(x, b)

    assert y == ID


def generate_isic_ids(max_doc_id: int=10, max_token_id: int=10):
    
    r1 = iter(range(0, max_doc_id))

    for i in r1:
        r2 = iter(range(0, max_token_id))
        for j in r2:
            inscription_id = pad_and_insert_fixed_strs(str(i) + str(j), 4)
        
            yield inscription_id


def full_circle(id: str, base: Literal[52, 100]):
    return decompress(compress(id, base), base)


def test_all_isic_ids():

    for id in generate_isic_ids(100, 100):
        assert full_circle(id, 52) == id


def rand_gen(start:int, end:int, size:int):
    for _ in range(size):
        yield random.randint(start, end)


def test_random_isic_ids():
    for doc_id in rand_gen(start=1, end=40000000, size=20):
        doc_id_str = str(doc_id)
        
        assert full_circle(pad_and_insert_fixed_strs(doc_id_str, 4), 52) == pad_and_insert_fixed_strs(doc_id_str, 4)
