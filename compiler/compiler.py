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

    DBG.set_floor(LOG_DEBG)
    
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

    DBG.set(LOG_BASE)
    log(LOG_INFO, "Commencing code generation...")
    cal = CPL2CAL(syntax_tree)
    assembly: asm.Assembly = cal.generate()
    log(LOG_INFO, "Done!")
    
    log(LOG_DEBG, "Final Symbol Table:")
    log_indent()
    cal.symbol_table.print(LOG_DEBG)
    log_dedent()
    log(LOG_DEBG, "End")

    log(LOG_DEBG, "Generated assembly:")
    for line in assembly.lines:
        s: str = line
        potentially_replaceables = findall(r"T([0-9]+)", line)
        for replaceable in potentially_replaceables:
            try:
                sym = cal.symbol_table.by_t(int(replaceable), False)
                var_name = sym.name
                s = s.replace("T"+replaceable, var_name)
            except KeyError:
                continue
        log(LOG_DEBG, s)
    log(LOG_DEBG, "End")
    
    log(LOG_INFO, "Compilation successful!")

    return assembly