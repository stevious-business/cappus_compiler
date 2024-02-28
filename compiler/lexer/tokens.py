from enum import Enum, auto

from cfclogger import *


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
    ENUMERATION = auto()


class TokenList:
    KEYWORDS = [
        "local",
        "subglobal",
        "global",
        "int",
        "str",
        "float",
        "bool",
        "void",
        "if",
        "else",
        "for",
        "while",
        "break",
        "continue",
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
        "^",
        "~"
    ]

    DOUBLES = [
        "++",
        "+=",
        "--",
        "-=",
        "**",
        "*=",
        "/=",
        ">>",
        ">=",
        "<=",
        "<<",
        "&&",
        "||",
        "!=",
        "^=",
        "%=",
        "&=",
        "|=",
        "=="
    ]

    TRIPLES = [
        ">>=",
        "<<="
    ]

    BOOLEANS = ("true", "false")

    OPENPARS = ("(", "[", "{")

    CLOSEPARS = (")", "]", "}")


class Lexeme:
    def __init__(self, tokenType: TokenType, value: str, src):
        self.tokenType = tokenType
        self.value = value
        self.src = src
        self.ptr = self.src.ptr
        self.stamp = src.get_pos()


def from_string(str_: str):
    """Returns a TokenType of which <str_> is a valid value"""
    specials = {
        "=": TokenType.EQUALS,
        ";": TokenType.SEMICOLON,
        ".": TokenType.DOT,
        ",": TokenType.COMMA,
        ":": TokenType.COLON,
        "EOF": TokenType.EOF
    }
    if str_ in TokenList.OPENPARS:
        return TokenType.OPENPAR
    elif str_ in TokenList.CLOSEPARS:
        return TokenType.CLOSEPAR
    elif str_ in TokenList.SINGLES + TokenList.DOUBLES + TokenList.TRIPLES:
        return TokenType.OPERATOR
    elif str_ in TokenList.KEYWORDS:
        return TokenType.KEYWORD
    elif str_ in TokenList.BOOLEANS:
        return TokenType.BOOL
    elif str_ in specials.keys():
        return specials[str_]
    else:
        log(LOG_WARN, f"Invalid value {str_}")
        return TokenType.INVALID
