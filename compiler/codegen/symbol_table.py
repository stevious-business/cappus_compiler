from enum import Enum, auto

from cfclogger import *

from compiler.lexer import tokens
from compiler.parser.ast import AST, AST_Node, AST_Terminal

class SymbolTypes(Enum):
    VARIABLE = auto()
    LABEL = auto()
    DATATYPE = auto()

class Symbol:
    def __init__(self, type_, name, dt="void", t=-1):
        self.type_ = type_
        self.liveness_begin = None
        self.liveness_end = None
        self.token: tokens.Lexeme = None
        self.name = name
        self.scope = None
        self.datatype = dt
        self.var_t = t
        log(LOG_BASE, f"New symbol <{str(self)}>!")
    
    def __str__(self):
        if self.type_ is SymbolTypes.VARIABLE:
            return "%s %s - %s [T%d]" % (self.type_.name, self.datatype,
                self.name, self.var_t)
        return f"{self.type_.name} {self.datatype} - {self.name}"

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
