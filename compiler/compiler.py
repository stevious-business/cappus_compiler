from io import TextIOWrapper, StringIO

from .lexer import lexer, source
from .parser import parser, ast
from .codegen import asm

from .codegen.frontend.CPL.generators import CPL2CPC

from cfclogger import *
from locals import *

from unit_tests.object_serializer import pretty_serialized_item


SELECTED_OPTIONS = DebugOutputOptions


def fmt(lexeme: lexer.tokens.Lexeme):
    return sfmt(lexeme.tokenType.name, 15)+sfmt(lexeme.value, 25) \
            + lexeme.stamp


def compile_unit_test(file, silent=True, update_floor=True):
    global DBG
    if silent:
        DBG.set_silent(True)
    try:

        assert isinstance(file, TextIOWrapper) or isinstance(file, StringIO)
        assert isinstance(update_floor, bool)

        OPTIONS = SELECTED_OPTIONS

        if update_floor:
            DBG.set_floor(OPTIONS.FLOOR)

        DBG.set(OPTIONS.LVL_SOURCE_FETCH)
        log(LOG_INFO, "Setting up...")
        if isinstance(file, TextIOWrapper):
            log(LOG_DEBG, f"Fetching source from {file.name}...", end="")
        else:
            log(LOG_DEBG, f"Fetching source from <string>...", end="")
        src: source.Source = source.Source(file)
        log(LOG_DEBG, "Done!", True)
        yield ("SOURCE", src)

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
        yield ("LEXEMES", lexemes)

        DBG.set(OPTIONS.LVL_PARSING)
        log(LOG_INFO, "Parsing...")
        log(LOG_DEBG, "Building AST...")
        syntax_tree: ast.AST = parser.parse(lstream)
        DBG.set(OPTIONS.LVL_PARSEOUT)
        parser.pretty_print(syntax_tree, lvl=LOG_DEBG)
        DBG.set(OPTIONS.LVL_PARSING)
        log(LOG_DEBG, "Done!")
        yield ("AST", syntax_tree)

        DBG.set(OPTIONS.LVL_CODEGEN)
        log(LOG_INFO, "Commencing code generation...")
        cpc = CPL2CPC(syntax_tree)
        assembly: asm.Assembly = cpc.generate()
        log(LOG_INFO, "Done!")

        DBG.set(OPTIONS.LVL_SYMTABOUT)
        log(LOG_DEBG, "Final Symbol Table:")
        log_indent()
        cpc.symbol_table.print(LOG_DEBG)
        log_dedent()
        log(LOG_DEBG, "End")
        yield ("SYM_TAB", cpc.symbol_table)

        DBG.set(OPTIONS.LVL_ASMOUT)
        log(LOG_DEBG, "Generated assembly:")
        assembly.niceout(LOG_DEBG, cpc)
        log(LOG_DEBG, "End")
        yield ("INTERMEDIATE", assembly)

        DBG.set(OPTIONS.FLOOR)
        log(LOG_INFO, "Compilation successful!")
    finally:
        DBG.set_silent(False)


def compile_silently(file):
    DBG.set_silent(True)
    try:
        res = compile(file, update_floor=False)
    except Exception:
        DBG.set_silent(False)
        raise
    DBG.set_silent(False)
    return res


def compile(file, update_floor=True):
    global DBG

    assert isinstance(file, TextIOWrapper) or isinstance(file, StringIO)
    assert isinstance(update_floor, bool)

    OPTIONS = SELECTED_OPTIONS

    if update_floor:
        DBG.set_floor(OPTIONS.FLOOR)

    DBG.set(OPTIONS.LVL_SOURCE_FETCH)
    log(LOG_INFO, "Setting up...")
    if isinstance(file, TextIOWrapper):
        log(LOG_DEBG, f"Fetching source from {file.name}...", end="")
    else:
        log(LOG_DEBG, f"Fetching source from <string>...", end="")
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
    cpc = CPL2CPC(syntax_tree)
    assembly: asm.Assembly = cpc.generate()
    log(LOG_INFO, "Done!")

    DBG.set(OPTIONS.LVL_SYMTABOUT)
    log(LOG_DEBG, "Final Symbol Table:")
    log_indent()
    cpc.symbol_table.print(LOG_DEBG)
    log_dedent()
    log(LOG_DEBG, "End")

    DBG.set(OPTIONS.LVL_ASMOUT)
    log(LOG_DEBG, "Generated assembly:")
    assembly.niceout(LOG_DEBG, cpc)
    log(LOG_DEBG, "End")

    DBG.set(OPTIONS.FLOOR)
    log(LOG_INFO, "Compilation successful!")

    return assembly
