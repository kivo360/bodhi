from auto_all import start_all, end_all

start_all(globals())
from .nodes import *
from .edges import *

end_all(globals())
