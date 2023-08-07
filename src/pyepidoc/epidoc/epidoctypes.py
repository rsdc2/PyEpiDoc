from typing import Optional, TypeVar, Union, MutableSequence, Generic
from enum import Enum
import operator
from ..base.basetypes import EnumerableEnum


T = TypeVar('T')

whitespace = {'\n', '\t', ' '}
PUNCTUATION = {'·'}


class SubatomicTagType(EnumerableEnum):
    Ex = 'ex'
    Expan = 'expan'
    Unclear = 'unclear'
    Abbr = 'abbr'
    Supplied = 'supplied'
    Del = 'del'
    Choice = 'choice'   # Choice always contained by an atomic word type, but never smaller than that, so not like others in this category
    Hi = 'hi' # can also contain atomic token types
    Surplus = 'surplus'
    Link = 'link'
    Subst = 'subst'


class AtomicTokenType(EnumerableEnum):
    Name = 'name'
    W = 'w'
    Num = 'num'
    Measure = 'measure'


class AtomicNonTokenType(EnumerableEnum):
    """
    These tokens do not contain text that can be incorporated into linguistic analysis.
    They stand either for metalinguistic tokens, such as line breaks or interpuncts (<lb>, <g>),
    text that cannot currently be analysed (<orig>, <seg>),
    or editorial notes (<note>).
    """
    G = 'g'
    Lb = 'lb'
    Space = 'space'
    Gap = 'gap'
    Orig = 'orig'   
    Seg = 'seg'     
    Note = 'note'   


class AlwaysSubsumableType(EnumerableEnum):
    """For items that should be subsumed regardless of whether or not there is a space.
    Membership of this class means that the behaviour of SubsumableRels takes place 
    regardless of the presence of a space between the tokens.
    Note that the token must also be listed in SubsumableRels"""
    # Hi = 'hi'
    Lb = 'lb'
    G = 'g'


AlwaysSubsumable = AlwaysSubsumableType.values()


class SpaceSeparated(EnumerableEnum):
    Name = 'name'
    W = 'w'
    Num = 'num'
    Measure = 'measure'
    
    PersName = 'persName'
    PlaceName = 'placeName'
    RoleName = 'roleName'
    OrgName = 'orgName'
    Foreign = 'foreign'
    
    G = 'g'

class NoSpace(EnumerableEnum):
    Note = 'note'


class ContainerType(EnumerableEnum):
    Ab = 'ab'
    Div = 'div'


class CompoundTokenType(EnumerableEnum):
    PersName = 'persName'
    PlaceName = 'placeName'
    RoleName = 'roleName'
    OrgName = 'orgName'
    Foreign = 'foreign'
    Hi = 'hi' # can also contain atomic token types
    Note = 'note'


TokenCarrier = set(
    SubatomicTagType.values() + 
    AtomicTokenType.values() + 
    AtomicNonTokenType.values() + 
    CompoundTokenType.values() + 
    AlwaysSubsumableType.values()
)


class AbbrType(EnumerableEnum):
    suspension = 'suspension'
    contraction = 'contraction'
    contraction_with_suspension = 'contraction_with_suspension'
    multiplication = 'muliplication'
    unknown = 'unknown'


class TextClass(EnumerableEnum):
    Funerary = '#function.funerary'
    LegalTestament = '#function.legal.testament'
    Unknown = '#function.unknown'
    Oracle = '#function.oracle'
    TesseraCivic = '#function.tessera.civic'
    DocumentPrivate = '#function.document.private'
    ProductionOwnership = '#function.production-ownership'
    Label = '#function.label'
    Ownership = '#function.ownership'
    Account = '#function.account'
    Abecedarium = '#function.abecedarium'
    Measure = '#function.measure'
    QuarryMark = '#function.quarry_mark'
    Calendar = '#function.calendar'
    Graffiti = '#function.graffiti'
    Seat = '#function.seat'
    Prayer = '#function.prayer'
    Touristic = '#function.touristic' 
    Magical = '#function.magical'
    List = '#function.list'
    Advertisement = '#function.advertisement' 
    Caption = '#function.caption' 
    Decree = '#function.decree'
    Terminus = '#function.terminus'
    CultDomainChristian = '#cult_domain.christian'
    Function = '#function.measure.weight'
    Dedication = '#function.dedication'
    Commercial = '#function.commercial'
    Stamp = '#function.stamp'
    Greeting = '#function.greeting'
    Signature = '#function.signature'
    EmptyDots = '#function....'
    Public = '#function.document.public'
    Defixio = '#function.defixio'
    Legal = '#function.legal'
    Ludic = '#function.ludic'
    TesseraHospitalis = '#function.tessera_hospitalis'
    Epigram = '#function.epigram'
    Milestone = '#function.milestone'
    LegalContract = '#function.legal.contract'
    Alphabet = '#function.alphabet'
    Votive = '#function.votive'
    Honorific = '#function.honorific'
    ListMagistrates = '#function.list.magistrates' 
    Letter = '#function.letter'
    ListPriests = '#function.list.priests'
    Cadastral = '#function.cadastral' 
    LexSacra = '#function.lex_sacra'
    Regulatory = '#function.regulatory'
    Building = '#function.building'
    Empty = '#function'
    ListInventory = '#function.list.inventory'


class SetRelation(Enum):
    @staticmethod
    def intersection(set1:set, set2:set) -> bool:
        return not set.isdisjoint(set1, set2)
        
    @staticmethod
    def propersubset(set1:set, set2:set) -> bool:
        return set.issubset(set1, set2) and set1 != set2

    subset = set.issubset
    equal = set.__eq__
    disjoint = set.isdisjoint


class GtLtRelation(Enum):
    gt = operator.gt
    lt = operator.lt


class SpaceUnit(Enum):
    Tab = "\t"
    Space = " "


class Morphology:

    def __init__(self, full:Optional[str]=None, case:Optional[str]=None, number:Optional[str]=None):
        if full is not None and full != "_" and full != "":
            self._parsefull(full)
            return 
        
        self._case = '-' if case is None else case
        self._number = '-' if number is None else number

    @property
    def case(self) -> str:
        return self._case

    @property
    def number(self) -> str:
        return self._number

    def _parsefull(self, full:str):
        if len(full) != 9:
            raise ValueError('Morphology string of incorrect length.')

        items = list(full)
        self._case = items[7]
        self._number = items[2]
        
    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if type(other) is Morphology:
            return str(self) == str(other)
        
        return False

    def __str__(self) -> str:
        return f'--{self.number}----{self.case}-'

    def __repr__(self) -> str:
        return f'Morphology("{self.__str__()}")'


class TokenInfo:

    def __init__(self, 
        lemma:Optional[str]=None, 
        morphology:Optional[Morphology]=None, 
        # abbr:Optional[str]=None
        ):
        # self._abbr_str = abbr
        self._lemma = lemma
        self._morphology = morphology if morphology is not None else Morphology()

    # @property
    # def abbr_str(self) -> Optional[str]:
    #     return self._abbr_str

    @property
    def lemma(self):
        return self._lemma
    
    @property
    def morphology(self):
        return self._morphology

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if type(other) is TokenInfo:
            return str(self) == str(other)
        
        return False

    def __str__(self) -> str:
        # return f'Lemma: {self.lemma}; Morphology: --{self.morphology.number}----{self.morphology.case}-; Abbr: {self.abbr_str}'
        return f'Lemma: {self.lemma}; Morphology: --{self.morphology.number}----{self.morphology.case}-'

    def __repr__(self) -> str:
        return f'WordInfo("{self.__str__()}")'
