from .reader import load_ebnf
from .ast import AST, AST_Node, AST_Terminal

from compiler.lexer import tokens, lexer

from cfclogger import *

def genASTNode(parent, grammar: dict, generator_type: str,
           lstream: lexer.LexemeStream) -> AST_Node:
    node = AST_Node(generator_type, parent, [])
    rules = grammar[generator_type].split(" ")
    for rule in rules:
        if rule.startswith('"') and rule.endswith('"'):
            rule_type = tokens.from_string(rule[1:-1])
            next_lexeme: tokens.Lexeme = lstream.consume_lexeme()
            if rule_type != next_lexeme.tokenType:
                log(LOG_FAIL, "Expected: %s Received: %s" % (
                    rule_type.name, next_lexeme.tokenType.name
                ))
                raise SyntaxError(f"Invalid Token at {next_lexeme.stamp}")
            if rule[1:-1] != next_lexeme.value:
                log(LOG_FAIL, "Expected: %s Received: %s" % (
                    rule[1:-1], next_lexeme.value
                ))
                raise SyntaxError(f"Invalid Lexeme at {next_lexeme.stamp}")
            # Valid, continue
            n = AST_Terminal(node, next_lexeme) # construct terminal
    return node

def parse(lstream: lexer.LexemeStream) -> AST:
    grammar = load_ebnf("compiler/parser/cpltest.ebnf")

    if grammar.get("translation-unit", None) is None:
        log(LOG_FAIL, "Invalid grammar! (Missing translation-unit)")
        raise SyntaxError
    
    root = AST("root", [])
    genASTNode(root, grammar, "translation-unit", lstream)
    return root

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