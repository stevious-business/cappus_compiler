from .reader import load_ebnf
from .ast import AST, AST_Node, AST_Terminal

from compiler.lexer import tokens, lexer

from cfclogger import *

def parse(lstream: lexer.LexemeStream) -> AST:
    grammar = load_ebnf("compiler/parser/cpl.ebnf")

    if grammar.get("translation-unit", None) is None:
        log(LOG_FAIL, "Invalid grammar! (Missing translation-unit)")
        raise SyntaxError
    
    log(LOG_DEBG, f"Grammar for translation-unit:\n{grammar['translation-unit']}")
    log(LOG_DEBG, f"Existing keys:\n{grammar.keys()}")
    
    return AST("translation-unit", [
        AST_Node("function-definition",None,[
            AST_Terminal(None, tokens.Lexeme(tokens.TokenType.KEYWORD, "int", lstream.source)),
            AST_Terminal(None, tokens.Lexeme(tokens.TokenType.IDENTIFIER, "var", lstream.source))
        ]),
        AST_Terminal(None, tokens.Lexeme(tokens.TokenType.EQUALS, "=", lstream.source))
    ])

def pretty_print(ast: AST_Node | AST, prefix=""):
    """Pretty prints a syntax tree"""
    t_char = "├── "
    i_char = "│   "
    l_char = "└── "
    empty  = "    "
    if prefix == "":
        log(LOG_VERB, ast.name)
    children = ast.get_children()
    for ast_node in children:
        if ast_node is children[-1]:
            # last child
            pref = prefix + l_char
            log(LOG_VERB, pref+ast_node.name)
            pretty_print(ast_node, prefix+empty)
        else:
            pref = prefix + t_char
            log(LOG_VERB, pref+ast_node.name)
            pretty_print(ast_node, prefix+i_char)