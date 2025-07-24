from .edition_elements.abbr import Abbr
from .edition_elements.am import Am
from .edition_elements.choice import Choice
from .edition_elements.corr import Corr
from .edition_elements.del_elem import Del
from .edition_elements.desc import Desc
from .edition_elements.ex import Ex
from .edition_elements.expan import Expan
from .edition_elements.g import G
from .edition_elements.gap import Gap
from .edition_elements.hi import Hi
from .edition_elements.lb import Lb
from .edition_elements.name import Name
from .edition_elements.num import Num
from .edition_elements.orig import Orig
from .edition_elements.pers_name import PersName
from .edition_elements.place_name import PlaceName
from .edition_elements.role_name import RoleName
from .edition_elements.sic import Sic
from .edition_elements.space import Space
from .edition_elements.supplied import Supplied
from .edition_elements.surplus import Surplus
from .edition_elements.unclear import Unclear
from .edition_elements.w import W
from .edition_elements.measure import Measure

representable_classes: dict[str, type] = {
    'abbr': Abbr,
    'am': Am,
    'choice': Choice,
    'corr': Corr,
    # 'desc': Desc,
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
    'placeName': PlaceName,
    'roleName': RoleName,
    'sic': Sic,
    'space': Space,
    'supplied': Supplied,
    'surplus': Surplus,
    'unclear': Unclear,
    'w': W,
    'measure': Measure
}