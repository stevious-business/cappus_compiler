from enum import Enum, auto

from cfclogger import *

from compiler.lexer import tokens
from compiler.parser.ast import AST, AST_Node, AST_Terminal

class SymbolTypes(Enum):
    VARIABLE = auto()
    LABEL = auto()
    DATATYPE = auto()

class Symbol:
    def __init__(self, type_, name):
        self.type_ = type_
        self.liveness_begin = None
        self.liveness_end = None
        self.token: tokens.Lexeme = None
        self.name = name
        self.scope = None

class SymbolTable:
    def __init__(self):
        self.entries: list[Symbol] = []
    
    def add_symbol(self, symbol:Symbol):
        self.entries.append(symbol)

    def by_name(self, name):
        for symbol in self.entries:
            if symbol.name == name:
                return symbol
        log(LOG_FAIL, f"Failed to find symbol {name} in table")
        raise KeyError(name)
