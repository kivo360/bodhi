from auto_all import start_all, end_all


start_all(globals())
from .core import *
from .binary import *
from .booleans import *
from .compares import *

end_all(globals())
