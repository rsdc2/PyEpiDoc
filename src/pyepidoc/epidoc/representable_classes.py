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
from .elements.num import Num
from .elements.orig import Orig
from .elements.supplied import Supplied
from .elements.surplus import Surplus
from .elements.unclear import Unclear
from .elements.w import W

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
    'num': Num,
    'orig': Orig,
    'supplied': Supplied,
    'surplus': Surplus,
    'unclear': Unclear,
    'w': W
}