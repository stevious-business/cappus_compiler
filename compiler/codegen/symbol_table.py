from enum import Enum, auto

from cfclogger import *

from compiler.lexer import tokens
from compiler.parser.ast import AST, AST_Node, AST_Terminal

class SymbolTypes(Enum):
    VARIABLE = auto()
    LABEL = auto()
    DATATYPE = auto()

class Symbol:
    def __init__(self, type_, name, dt="void"):
        self.type_ = type_
        self.liveness_begin = None
        self.liveness_end = None
        self.token: tokens.Lexeme = None
        self.name = name
        self.scope = None
        self.datatype = dt
    
    def __str__(self):
        return f"{self.type_.name} - {self.name}"

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
    
    def print(self, log_level):
        for symbol in self.entries:
            log(log_level, str(symbol))
