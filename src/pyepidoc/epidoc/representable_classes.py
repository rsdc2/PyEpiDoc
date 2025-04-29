from .elements.abbr import Abbr
from .elements.am import Am
from .elements.choice import Choice
from .elements.del_elem import Del
from .elements.ex import Ex
from .elements.expan import Expan
from .elements.g import G
from .elements.gap import Gap
from .elements.hi import Hi
from .elements.lb import Lb
from .elements.name import Name
from .elements.num import Num
from .elements.orig import Orig
from .elements.pers_name import PersName
from .elements.supplied import Supplied
from .elements.surplus import Surplus
from .elements.unclear import Unclear
from .elements.w import W
from .elements.measure import Measure

elem_classes: dict[str, type] = {
    'abbr': Abbr,
    'am': Am,
    'choice': Choice,
    'ex': Ex, 
    'del': Del,
    'expan': Expan,
    'g': G,
    'gap': Gap,
    'hi': Hi,
    'lb': Lb,
    'name': Name,
    'num': Num,
    'orig': Orig,
    'persName': PersName,
    'supplied': Supplied,
    'surplus': Surplus,
    'unclear': Unclear,
    'w': W,
    'measure': Measure
}