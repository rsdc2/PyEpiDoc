from dataclasses import dataclass
from enum import Enum


class Bk(Enum):
    Mt = 'mt'
    Mk = 'mk'
    Lk = 'lk'
    Jn = 'jn'
    Rm = 'rm'
    Ac = 'ac'
    ICo = '1co'
    IICo = '2co'
    Ga = 'ga'
    Ep = 'ep'
    Co = 'co'
    Ph = 'ph'
    ITh = '1th'
    IITh = '2th'
    ITi = '1ti'
    IITi = '2ti'
    Ti = 'ti'
    Hb = 'hb'
    Js = 'js'
    IPe = '1pe'
    IIPe = '2pe'
    Ju = 'ju'
    IJn = '1jn'
    IIJn = '2jn'
    IIIJn = '3jn'
    Rv = 'rv'

NT_BOOKS: dict[Bk, list[str]] = {
    Bk.Mt: ['mt', 'matt', 'matthew'],
    Bk.Mk: ['mk', 'mark'],
    Bk.Lk: ['lk', 'luke'],
    Bk.Jn: ['jn', 'john'],
    Bk.Rm: ['rm', 'rom', 'romans'],
    Bk.Ac: ['ac', 'acts'],
    Bk.ICo: ['1co', '1cor', '1corinthians', 'icorinthians', 'icorinthians', 'ico', 'icor'],
    Bk.IICo: ['2co', '2cor', '2corinthians', 'iicorinthians', 'iicorinthians', 'iico', 'iicor'],
    Bk.Ga: ['ga', 'gal', 'galatians'],
    Bk.Ep: ['ep', 'eph', 'ephesians'],
    Bk.Co: ['co', 'col', 'colossians'],
    Bk.Ph: ['ph', 'phil', 'philippians'],
    Bk.ITh: ['1th', 'ith', '1thess', 'ithess', 'ithessalonians', '1thessalonians'],
    Bk.IITh: ['2th', 'iith', '2thess', 'iithess', 'iithessalonians', '2thessalonians'],
    Bk.ITi: ['1ti', '1tim', 'iti', 'itim', '1timothy', 'itimothy'],
    Bk.IITi: ['2ti', '2tim', 'iiti', 'iitim', '2timothy', 'iitimothy'],
    Bk.Ti: ['ti', 'tit', 'titus'],
    Bk.Hb: ['hb', 'heb', 'hebrews'],
    Bk.Js: ['js', 'jas', 'james'],
    Bk.IPe: ['1pe', '1pet', 'ipeter', '1peter'],
    Bk.IIPe: ['2pe', 'iipet', 'iipeter', '2peter'],
    Bk.Ju: ['jude', 'jud'],
    Bk.IJn: ['1jn', 'ijn', '1john', 'ijohn'],
    Bk.IIJn: ['2jn', 'iijn', '2john', 'iijohn'],
    Bk.IIIJn: ['3jn', 'iiijn', '3john', 'iiijohn'],
    Bk.Rv: ['rv', 'rev', 'revelation'],
}

@dataclass
class BibleBook:

    _book: Bk

    def __init__(self, book_id: str):
        for book in NT_BOOKS.items():
            ids = book[1]
            bk_id = book[0]
            if book_id.lower().replace(' ', '') in ids:
                self._book = bk_id
                return
        raise ValueError(f"Book id {book_id} not found")
    
    @property
    def book(self) -> Bk:
        return self._book

    def __str__(self) -> str:
        return NT_BOOKS[self._book][0].capitalize()
