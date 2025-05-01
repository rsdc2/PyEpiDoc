from pyepidoc.epidoc.ids import compress, decompress, pad_and_insert_fixed_strs
import random
import pytest
from typing import Literal

compressions_52 = [
    ("ISic000001-0001", "AADkR", "First token id"),
    ("ISic000000-0000", "AAAAA", "Zero token id")
    # ("ISic099999-9999", "ωωωωω", "Last token id")
]


compressions_100 = [
    ("ISic000001-00001", "AAKAB", "First token id"),
    ("ISic000000-00000", "AAAAA", "Zero token id"),
    ("ISic099999-99999", "ωωωωω", "Last token id")
]


def test_id_100_correct_roundtrip():
    ID = 'ISic099999-09999' # 'ISic999999-9999'
    b = 100
    x = compress(ID, b)
    y = decompress(x, b)

    assert y == ID


@pytest.mark.parametrize(['uncompressed', 'compressed', '_'], compressions_52)
def test_id_52_correct_compression(uncompressed, compressed, _):
    assert compress(uncompressed, 52) == compressed


@pytest.mark.parametrize(['uncompressed', 'compressed', '_'], compressions_100)
def test_id_100_correct_compression(uncompressed, compressed, _):
    assert compress(uncompressed, 100) == compressed


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
            # breakpoint()
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
