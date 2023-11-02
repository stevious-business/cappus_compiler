from .lexer import lexer, source
from .parser import parser, ast
from .codegen import asm

from .codegen.CPL.generators import CPL2CAL

from cfclogger import *
from locals import *

def fmt(lexeme: lexer.tokens.Lexeme):
    return sfmt(lexeme.tokenType.name, 15)+sfmt(lexeme.value, 25) \
            +lexeme.stamp

def compile(file):
    global DBG
    
    DBG.set(LOG_VERB)

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
    DBG.set(LOG_DEBG)
    for lexeme in lexemes:
        log(LOG_DEBG, fmt(lexeme))
    log(LOG_DEBG, "Done!")

    DBG.set(LOG_BASE)
    log(LOG_INFO, "Parsing...")
    log(LOG_DEBG, "Building AST...")
    syntax_tree: ast.AST = parser.parse(lstream)
    DBG.set(LOG_DEBG)
    parser.pretty_print(syntax_tree, lvl=LOG_DEBG)
    log(LOG_DEBG, "Done!")

    DBG.set(LOG_VERB)
    log(LOG_INFO, "Commencing code generation...")
    assembly: asm.Assembly = CPL2CAL(syntax_tree).generate()
    log(LOG_INFO, "Done!")
    
    log(LOG_DEBG, "Generated assembly:")
    for line in assembly.lines:
        log(LOG_DEBG, line)
    log(LOG_DEBG, "End")
    
    log(LOG_INFO, "Compilation successful!")

    return assembly