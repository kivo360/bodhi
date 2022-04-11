from auto_all import start_all, end_all

start_all(globals())

from .types import *
from .abc import *

# from .base_ops import Binary, Expr, Grouping, Literal, Unary, Stmt

end_all(globals())
