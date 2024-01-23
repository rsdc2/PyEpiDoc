from pyepidoc.epidoc.ids import *
import random
import pytest



def test_id_correct_expansion():
    ID = 'ISic099999-9999' # 'ISic999999-9999'
    b = 52
    x = compress(ID, b)
    y = decompress(x, b)

    assert y == ID


def generate_isic_ids(doc_ids_count: int=10, elem_ids_count: int=10):
    """
    :param doc_ids_count: Number of I.Sicily document IDs to generate
    :param elem_ids_count: Number of element IDs to generate within
    each document 
    :returns: a generator for sequential I.Sicily element IDs 
    up to a maximum document ID and element ID specified in the
    parameters
    """
    
    r1 = iter(range(0, doc_ids_count))

    # Iterate through I.Sicily document IDs
    for i in r1:
        r2 = iter(range(0, elem_ids_count))

        # Iterate through the token IDs in the I.Sicily document
        for j in r2:
            inscription_id = pad_and_insert_fixed_strs(str(i) + str(j), 4)
            breakpoint()
            yield inscription_id


def full_circle(id: str, base: Literal[52, 100]):
    """
    Compress and decompress an ID
    """
    return decompress(compress(id, base), base)


def test_all_isic_ids():
    """
    Iterates through all the I.Sicily IDs 
    and all the token IDs within that I.Sicily ID
    sequentially up to a maximum specified in 
    the parameters of generate_isic_ids
    """

    for id in generate_isic_ids(100, 100):
        assert full_circle(id, 52) == id


def rand_gen(start:int, end:int, size:int):
    """
    Generate a random number to turn into an ID

    :param start: lower limit of the range
    :param end: upper limit of the range
    :param size: number of ids to generate
    :returns: a random number to turn into an ID
    """
    for _ in range(size):
        yield random.randint(start, end)


def test_random_isic_ids():
    for doc_id in rand_gen(start=1, end=40000000, size=20):
        doc_id_str = str(doc_id)

        isic_id = pad_and_insert_fixed_strs(doc_id_str, 4)
        assert full_circle(isic_id, 52) == isic_id
