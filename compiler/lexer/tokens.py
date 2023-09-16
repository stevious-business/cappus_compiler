from enum import Enum, auto

class TokenType(Enum):
    DOT = auto()
    COMMA = auto()
    COLON = auto()
    EQUALS = auto()
    SEMICOLON = auto()
    OPERATOR = auto()
    INVALID = auto()
    OPENPAR = auto()
    CLOSEPAR = auto()
    KEYWORD = auto()
    EOF = auto()

    IDENTIFIER = auto()
    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOL = auto()

class TokenList:
    KEYWORDS = [
        "int",
        "str",
        "float",
        "bool",
        "if",
        "else",
        "for",
        "while",
        "return"
    ]

    SINGLES = [
        "+",
        "-",
        "*",
        "/",
        "%",
        ">",
        "<",
        "&",
        "|",
        "!",
        "^"
    ]

    DOUBLES = [
        "++",
        "+=",
        "--",
        "-=",
        "**"
        "*=",
        "/=",
        ">>",
        ">=",
        "<=",
        "<<",
        "&&",
        "||",
        "!=",
        "^="
    ]

    TRIPLES = [
        ">>=",
        "<<="
    ]

    BOOLEANS = ("true", "false")

class Lexeme:
    def __init__(self, tokenType: TokenType, value: str, src):
        self.tokenType = tokenType
        self.value = value
        self.src = src
        self.stamp = src.get_pos()