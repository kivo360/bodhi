
#%%

from mangostar import FlexibleModel
from datetime import datetime
from typing import Dict, Any, Optional

DictAny = Dict[str, Any]
# %%
class EventGeneric(FlexibleModel):
    name: str
    values:DictAny = {}
    timestamp: datetime = datetime.now()
    selects: DictAny

class Actor(EventGeneric):
    pass
    
    

class Activity(EventGeneric):
    name: Optional[str] = None
    

class Target(EventGeneric):
    pass    

# %%
