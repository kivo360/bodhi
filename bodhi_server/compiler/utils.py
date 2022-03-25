from bodhi_server.compiler import Token, TokenType, Binary
from auto_all import start_all, end_all


def new_token(tyoken_type: TokenType, lexeme: str):
    return Token(token_type=tyoken_type, lexeme=lexeme)
