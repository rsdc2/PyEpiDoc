from dataclasses import dataclass
from enum import Enum


class Bk(Enum):
    Mt = 'Mat'
    Mk = 'Mrk'
    Lk = 'Luk'
    Jn = 'Jhn'
    Rm = 'Rom'
    Ac = 'Act'
    ICo = '1Co'
    IICo = '2Co'
    Ga = 'Gal'
    Ep = 'Eph'
    Co = 'Col'
    Ph = 'Php'
    ITh = '1Th'
    IITh = '2Th'
    ITi = '1Ti'
    IITi = '2Ti'
    Ti = 'Tit'
    Philem = 'Phl'
    Hb = 'Heb'
    Js = 'Jas'
    IPe = '1Pe'
    IIPe = '2Pe'
    Ju = 'Jud'
    IJn = '1Jn'
    IIJn = '2Jn'
    IIIJn = '3Jn'
    Rv = 'Rev'

NT_BOOKS: dict[Bk, list[str]] = {
    Bk.Mt:      ['01', 'mt', 'matt', 'matthew', 'mat'],
    Bk.Mk:      ['02', 'mk', 'mark', 'mrk'],
    Bk.Lk:      ['03', 'lk', 'luke', 'luk'],
    Bk.Jn:      ['04', 'jn', 'john', 'jhn'],
    Bk.Rm:      ['05', 'rm', 'rom', 'romans'],
    Bk.Ac:      ['06', 'ac', 'acts'],
    Bk.ICo:     ['07', '1co', '1cor', '1corinthians', 'icorinthians', 'icorinthians', 'ico', 'icor'],
    Bk.IICo:    ['08', '2co', '2cor', '2corinthians', 'iicorinthians', 'iicorinthians', 'iico', 'iicor'],
    Bk.Ga:      ['09', 'ga', 'gal', 'galatians'],
    Bk.Ep:      ['10', 'ep', 'eph', 'ephesians'],
    Bk.Co:      ['11', 'co', 'col', 'colossians'],
    Bk.Ph:      ['12', 'ph', 'phil', 'philippians'],
    Bk.ITh:     ['13', '1th', 'ith', '1thess', 'ithess', 'ithessalonians', '1thessalonians'],
    Bk.IITh:    ['14', '2th', 'iith', '2thess', 'iithess', 'iithessalonians', '2thessalonians'],
    Bk.ITi:     ['15', '1ti', '1tim', 'iti', 'itim', '1timothy', 'itimothy'],
    Bk.IITi:    ['16', '2ti', '2tim', 'iiti', 'iitim', '2timothy', 'iitimothy'],
    Bk.Ti:      ['17', 'ti', 'tit', 'titus'],
    Bk.Philem:  ['18', 'philem'],
    Bk.Hb:      ['19', 'hb', 'heb', 'hebrews'],
    Bk.Js:      ['20', 'js', 'jas', 'james'],
    Bk.IPe:     ['21', '1pe', '1pet', 'ipeter', '1peter'],
    Bk.IIPe:    ['22', '2pe', 'iipet', 'iipeter', '2peter'],
    Bk.Ju:      ['23', 'jude', 'jud'],
    Bk.IJn:     ['24', '1jn', 'ijn', '1john', 'ijohn'],
    Bk.IIJn:    ['25', '2jn', 'iijn', '2john', 'iijohn'],
    Bk.IIIJn:   ['26', '3jn', 'iiijn', '3john', 'iiijohn'],
    Bk.Rv:      ['27', 'rv', 'rev', 'revelation'],
}

@dataclass
class BibleBook:

    _bk: Bk

    def __init__(self, book_id: str):
        for book in NT_BOOKS.items():
            ids = book[1]
            bk_id = book[0]
            if book_id.lower().replace(' ', '') in ids:
                self._bk = bk_id
                return
        raise ValueError(f"Book id {book_id} not found")
    
    @property
    def book(self) -> Bk:
        return self._bk

    def __str__(self) -> str:
        return str(self._bk.value)
    
    def __eq__(self, other: object) -> bool:
        if isinstance(other, BibleBook):
            return self._bk == other._bk
        return false