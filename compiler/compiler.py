from .lexer import lexer, source
from .parser import parser, ast

from cfclogger import log
from locals import *

def fmt(lexeme: lexer.tokens.Lexeme):
    return sfmt(lexeme.tokenType.name, 15)+sfmt(lexeme.value, 25) \
            +lexeme.stamp

def sfmt(str_: str, len_: int):
    strlen = len(str_)
    remain = len_ - strlen
    return str_ + remain * "."

def compile(file):
    log(LOG_INFO, "Setting up...")
    log(LOG_DEBG, "Fetching source...", end="")
    src: source.Source = source.Source(file)
    log(LOG_DEBG, "Done!", True)

    log(LOG_INFO, "Lexing...")
    log(LOG_DEBG, "Building Lexeme stream...", end="")
    lstream = lexer.LexemeStream(src)
    log(LOG_DEBG, "Done!", True)

    log(LOG_DEBG, "Finding Lexemes...")
    lexemes = lstream.findall()
    for lexeme in lexemes:
        log(LOG_VERB, fmt(lexeme))
    log(LOG_DEBG, "Done!")

    log(LOG_INFO, "Parsing...")
    log(LOG_DEBG, "Building AST...")
    syntax_tree: ast.AST = parser.parse(lstream)
    parser.pretty_print(syntax_tree)
    log(LOG_DEBG, "Done!")
    
    log(LOG_INFO, "Compilation successful!")