from re import findall

from .lexer import lexer, source
from .parser import parser, ast
from .codegen import asm

from .codegen.frontend.CPL.generators import CPL2CAL

from cfclogger import *
from locals import *

def fmt(lexeme: lexer.tokens.Lexeme):
    return sfmt(lexeme.tokenType.name, 15)+sfmt(lexeme.value, 25) \
            +lexeme.stamp

def compile(file):
    global DBG

    OPTIONS = CustomDebuggingOptions

    DBG.set_floor(OPTIONS.FLOOR)
    
    DBG.set(OPTIONS.LVL_SOURCE_FETCH)
    log(LOG_INFO, "Setting up...")
    log(LOG_DEBG, f"Fetching source from {file.name}...", end="")
    src: source.Source = source.Source(file)
    log(LOG_DEBG, "Done!", True)

    DBG.set(OPTIONS.LVL_LEXING)
    log(LOG_INFO, "Lexing...")
    log(LOG_DEBG, "Building Lexeme stream...", end="")
    lstream = lexer.LexemeStream(src)
    log(LOG_DEBG, "Done!", True)
    
    log(LOG_DEBG, "Finding Lexemes...")
    lexemes = lstream.findall()
    DBG.set(OPTIONS.LVL_LEXOUT)
    for lexeme in lexemes:
        log(LOG_DEBG, fmt(lexeme))
    DBG.set(OPTIONS.LVL_LEXING)
    log(LOG_DEBG, "Done!")

    DBG.set(OPTIONS.LVL_PARSING)
    log(LOG_INFO, "Parsing...")
    log(LOG_DEBG, "Building AST...")
    syntax_tree: ast.AST = parser.parse(lstream)
    DBG.set(OPTIONS.LVL_PARSEOUT)
    parser.pretty_print(syntax_tree, lvl=LOG_DEBG)
    DBG.set(OPTIONS.LVL_PARSING)
    log(LOG_DEBG, "Done!")

    DBG.set(OPTIONS.LVL_CODEGEN)
    log(LOG_INFO, "Commencing code generation...")
    cal = CPL2CAL(syntax_tree)
    assembly: asm.Assembly = cal.generate()
    log(LOG_INFO, "Done!")
    
    DBG.set(OPTIONS.LVL_SYMTABOUT)
    log(LOG_DEBG, "Final Symbol Table:")
    log_indent()
    cal.symbol_table.print(LOG_DEBG)
    log_dedent()
    log(LOG_DEBG, "End")

    DBG.set(OPTIONS.LVL_ASMOUT)
    log(LOG_DEBG, "Generated assembly:")
    assembly.niceout(LOG_DEBG, cal)
    log(LOG_DEBG, "End")
    
    DBG.set(OPTIONS.FLOOR)
    log(LOG_INFO, "Compilation successful!")

    return assembly