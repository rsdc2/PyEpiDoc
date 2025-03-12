from __future__ import annotations
from typing import TypeVar
from enum import Enum
from ..shared.classes import EnumerableEnum

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
    Subst = 'subst'
    C = 'c' # Character element


# Elements that contain text that would not be 
# included in a normalized form of the text
class OrigTextType(EnumerableEnum):  
    # Del = 'del'
    # Surplus = 'surplus'
    Orig = 'orig'
    Sic = 'sic'
    G = 'g'
    Am = 'am'


class RegTextType(EnumerableEnum):
    Reg = 'reg'
    Corr = 'corr'


class AtomicTokenType(EnumerableEnum):
    Name = 'name'
    # RoleName = 'roleName'
    AddName = 'addName'
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
    Milestone = 'milestone'
    Certainty = 'certainty'
    HandShift = 'handShift'
    Link = 'link'


class AlwaysSubsumableType(EnumerableEnum):
    """For items that should be subsumed regardless of whether or not there is a space.
    Membership of this class means that the behaviour of SubsumableRels takes place 
    regardless of the presence of a space between the tokens.
    Note that the token must also be listed in SubsumableRels"""
    # Hi = 'hi'
    Lb = 'lb'
    G = 'g'
    Comment = 'Comment'


AlwaysSubsumable = AlwaysSubsumableType.values()


class SpaceSeparated(EnumerableEnum):

    """
    |Element|s that should be separated by spaces    
    """

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
    Gap = 'gap'
    Unclear = 'unclear'
    Supplied = 'supplied'


class N_ID_Elements(EnumerableEnum):
    W = 'w'
    Orig = 'orig'
    G = 'g'


class NoSpace(EnumerableEnum):
    Note = 'note'


class ContainerType(EnumerableEnum):
    Ab = 'ab'
    Lg = 'lg'
    L = 'l'
    Div = 'div'


class CompoundTokenType(EnumerableEnum):
    PersName = 'persName'
    # Choice = 'choice'
    PlaceName = 'placeName'
    RoleName = 'roleName'
    OrgName = 'orgName'
    Foreign = 'foreign'
    Hi = 'hi' # can also contain atomic token types
    Note = 'note'
    Date = 'date'
    RS = 'rs'
    Add = 'add' # Correct place?    
    Cb = 'cb' # Column beginning


# Elements that carry tokens, e.g. as internal or external text
TokenCarrier = set(
      SubatomicTagType.values() 
    + AtomicTokenType.values() 
    + AtomicNonTokenType.values() 
    + CompoundTokenType.values() 
    + AlwaysSubsumableType.values() 
    + ['Comment']
)


# Elements that carry text to be included in normalized edition
NormalizedTextCarrier = set(
    SubatomicTagType.values() 
    + AtomicTokenType.values() 
    + CompoundTokenType.values() 
    + AlwaysSubsumableType.values()
) - set(OrigTextType.values())


# Elements that can carry @xml:id
IdCarrier = set(
    SubatomicTagType.values() 
    + AtomicTokenType.values() 
    + AtomicNonTokenType.values() 
    + CompoundTokenType.values() 
)


class AbbrType(EnumerableEnum):
    suspension = 'suspension'
    contraction = 'contraction'
    contraction_with_suspension = 'contraction_with_suspension'
    multiplication = 'muliplication'
    unknown = 'unknown'

    def __str__(self) -> str:
        str_dict = {
            'suspension': 'Suspension',
            'contraction': 'Contraction',
            'contraction_with_suspension': 'Contraction with suspension',
            'multiplication': 'Multiplication',
            'unknown': 'Unknown'
        }        
        return str_dict.get(self.name, 'Unknown')


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

    @staticmethod
    def to_str(tc: TextClass) -> str:
        return tc.value
    
    def __str__(self) -> str:
        return self.value



class SpaceUnit(Enum):
    Tab = "\t"
    Space = " "

