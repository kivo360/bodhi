from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import json
from functools import cache
from black import format_str, FileMode

from loguru import logger
from bodhi_server.utils import consistent_classes as const_class
from bodhi_server.compiler import (
    OpType,
    BinopType,
    UnaryType,
    NodeType,
)

CURR_DIRR = Path(__file__).parent
GEN_DIR = CURR_DIRR / "gencode"

OUTPUT_FILES = {
    "nodes": (GEN_DIR / "nodes.py"),
    "workflow": (GEN_DIR / "workflows.py"),
}


def store_file(outype: str, result: str):
    GEN_DIR.mkdir(parents=True, exist_ok=True)

    io_file = OUTPUT_FILES[outype]
    logger.info(str(io_file))
    if io_file.exists():
        io_file.unlink()
    io_file.touch(exist_ok=True)
    io_file.write_text(result)


@cache
def get_metatdata():
    return json.loads(Path(CURR_DIRR / "metadata.json").read_text())


__op_map = {
    "+": BinopType.ADD,
    "-": BinopType.SUB,
    "*": BinopType.MUL,
    "/": BinopType.DIV,
    "//": BinopType.FLOORDIV,
    "%": BinopType.MOD,
    "|": BinopType.BIT_OR,
    "&": BinopType.BIT_AND,
    "^": BinopType.BIT_XOR,
    ">": BinopType.GT,
    ">=": BinopType.GE,
    "<": BinopType.LT,
    "<=": BinopType.LE,
    "==": BinopType.EQ,
    "!=": BinopType.NE,
    "and": OpType.AND,
    "or": OpType.OR,
}


__unary_op_map = {
    "+": UnaryType.PLUS,
    "-": UnaryType.MINUS,
    "!": UnaryType.NOT,
    "not": UnaryType.NOT,
}


__stmt_map = {
    "program": NodeType.PROGRAM,
    "class": NodeType.CLASS,
    "exprstmt": NodeType.EXPRSTMT,
    "variable": NodeType.VARIABLE,
    "assign": NodeType.ASSIGN,
    "block": NodeType.BLOCK,
    "if": NodeType.IF,
    "while": NodeType.WHILE,
    "call": NodeType.CALL,
    "return": NodeType.RETURN,
    "logical": NodeType.LOGICAL,
    "function": NodeType.FUNCTION,
    "expr": NodeType.EXPR,
    "for": NodeType.FOR,
    "break": NodeType.BREAK,
    "continue": NodeType.CONTINUE,
}

__expr_map = {
    "program": NodeType.PROGRAM,
    "class": NodeType.CLASS,
    "exprstmt": NodeType.EXPRSTMT,
    "variable": NodeType.VARIABLE,
    "assign": NodeType.ASSIGN,
    "block": NodeType.BLOCK,
    "if": NodeType.IF,
    "while": NodeType.WHILE,
    "call": NodeType.CALL,
    "return": NodeType.RETURN,
    "logical": NodeType.LOGICAL,
    "function": NodeType.FUNCTION,
    "expr": NodeType.EXPR,
    "for": NodeType.FOR,
    "break": NodeType.BREAK,
    "continue": NodeType.CONTINUE,
}


def format_result(result: str):
    return format_str(result, mode=FileMode(line_length=120))


def match_enum(token: str):
    return (
        __op_map.get(token, None)
        or __unary_op_map.get(token, None)
        or __expr_map.get(token.lower(), None)
        or None
    )


def generate_workflow(tmp_env: Environment):
    from devtools import debug

    # meta = get_metatdata()

    # nodes = meta["nodes"]
    # node_list = []  # A list of dicts that have the final descriptions for nodes.
    # for category in nodes.keys():
    #     for token, binop in nodes.get(category).items():
    #         logger.warning(const_class(binop))
    #         node_list.append(
    #             {
    #                 "class_name": const_class(binop),
    #                 "token": token,
    #                 "enum": match_enum(token),
    #             }
    #         )
    template = tmp_env.get_template("flyte.py.j2")
    rendered = template.render()
    formatted = format_result(rendered)
    store_file("workflow", formatted)
    return format_result(rendered)


def main():

    tmp_env = Environment(loader=FileSystemLoader(str(CURR_DIRR / "templates")))
    generate_workflow(tmp_env)
    # temp_env.get_template("")


if __name__ == "__main__":
    main()
