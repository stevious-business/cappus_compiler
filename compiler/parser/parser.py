from .reader import load_ebnf
from .ast import AST, AST_Node, AST_Terminal

from compiler.lexer import tokens, lexer

from cfclogger import *

from .cache import Cache

cache = Cache()

def genPossSet(grammar, lstream, possSet, node, possPreset={}):
    global cache
    # possPreset: dict[str: (ls, node)]
    for poss in possSet: # poss - all are true
        if possPreset.get(poss, None) is not None:
            node.add_child(possPreset[poss])
            continue
        if poss == "<identifier>":
            lexeme = lstream.consume_lexeme()
            if lexeme.tokenType != tokens.TokenType.IDENTIFIER:
                raise SyntaxError("Expected identifier, got %s" % (
                    lexeme.tokenType.name
                ))
            n = AST_Terminal(node, lexeme) # construct terminal
            node.add_child(n)
            log(LOG_VERB, f"Parsed identifier {lexeme.value}")
            log(LOG_DEBG, "Found an <identifier>!")
        elif poss == "<integer-constant>":
            lexeme = lstream.consume_lexeme()
            if lexeme.tokenType != tokens.TokenType.INTEGER:
                raise SyntaxError("Expected integer, got %s" % (
                    lexeme.tokenType.name
                ))
            n = AST_Terminal(node, lexeme) # construct terminal
            node.add_child(n)
            log(LOG_VERB, f"Parsed integer {lexeme.value}")
            log(LOG_DEBG, "Found an <integer-constant>!")
        elif poss == "<string>":
            lexeme = lstream.consume_lexeme()
            if lexeme.tokenType != tokens.TokenType.STRING:
                raise SyntaxError("Expected string, got %s" % (
                    lexeme.tokenType.name
                ))
            n = AST_Terminal(node, lexeme) # construct terminal
            node.add_child(n)
            log(LOG_VERB, f"Parsed string {lexeme.value}")
            log(LOG_DEBG, "Found a <string>!")
        elif poss == "<floating-constant>":
            lexeme = lstream.consume_lexeme()
            if lexeme.tokenType != tokens.TokenType.FLOAT:
                raise SyntaxError("Expected float, got %s" % (
                    lexeme.tokenType.name
                ))
            n = AST_Terminal(node, lexeme) # construct terminal
            node.add_child(n)
            log(LOG_VERB, f"Parsed float {lexeme.value}")
            log(LOG_DEBG, "Found a <floating-constant>!")
        elif poss == "<boolean-constant>":
            lexeme = lstream.consume_lexeme()
            if lexeme.tokenType != tokens.TokenType.BOOL:
                raise SyntaxError("Expected bool, got %s" % (
                    lexeme.tokenType.name
                ))
            n = AST_Terminal(node, lexeme) # construct terminal
            node.add_child(n)
            log(LOG_VERB, f"Parsed bool {lexeme.value}")
            log(LOG_DEBG, "Found a <boolean-constant>!")
        elif poss.endswith("}?"):
            try:
                lst = lstream.copy()
                n = genASTNode(node, grammar, poss[1:-2], lst)
                node.add_child(n)
                lstream.update(lst)
            except SyntaxError:
                log(LOG_DEBG, f"Optional '{poss[1:-2]}' not present")
        elif poss.endswith("}*"):
            try:
                while True:
                    n = genASTNode(node, grammar, poss[1:-2], lstream)
                    node.add_child(n)
            except SyntaxError:
                pass
        elif poss.endswith("}+"):
            raise_ = True
            try:
                while True:
                    n = genASTNode(node, grammar, poss[1:-2],
                                    lstream)
                    node.add_child(n)
                    raise_ = False
            except SyntaxError:
                if raise_:
                    raise SyntaxError
        elif poss in grammar.keys():
            n = genASTNode(node, grammar, poss, lstream)
            node.add_child(n)
        else:
            rule_type = tokens.from_string(poss)
            next_lexeme = lstream.consume_lexeme()
            if rule_type != next_lexeme.tokenType:
                raise SyntaxError("Invalid Token Type: "
                                    +rule_type.name+" "
                                    +next_lexeme.tokenType.name)
            if poss != next_lexeme.value:
                raise SyntaxError("Invalid Lexeme Value: "
                                    +poss+" "
                                    +next_lexeme.value)
            # Valid, continue
            log(LOG_VERB,
                f"Parsed {rule_type.name}: {next_lexeme.value}")
            n = AST_Terminal(node, next_lexeme) # construct terminal
            node.add_child(n)

def genASTNode(parent, grammar: dict, generator_type: str,
           ls: lexer.LexemeStream) -> AST_Node:
    global cache
    cache_entry = cache[(generator_type, ls.pointer)]
    if cache_entry is not None:
        log(LOG_DEBG,
            f"Cache hit for {generator_type}/{ls.pointer}; size: {cache.size()} bytes")
        if cache_entry == 0:
            raise SyntaxError(f"[CACHED] Invalid path for {generator_type}! [200]")
        else:
            node, ptr = cache_entry
            ls.pointer = ptr
            return node
    if generator_type not in grammar.keys():
        # terminal
        rule_type = tokens.from_string(generator_type)
        next_lexeme = ls.consume_lexeme()
        if rule_type != next_lexeme.tokenType:
            raise SyntaxError(
                "Invalid Token type; expected: %s %s got: %s %s" % (
                    rule_type.name, generator_type, next_lexeme.tokenType,
                    next_lexeme.value
                ))
        if generator_type != next_lexeme.value:
            raise SyntaxError(
                "Invalid Token type; expected: %s %s got: %s %s" % (
                    rule_type.name, generator_type, next_lexeme.tokenType,
                    next_lexeme.value
                ))
        # Valid, continue
        node = AST_Node(generator_type, parent, [])
        n = AST_Terminal(node, next_lexeme) # construct terminal
        return n
    log(LOG_DEBG, f"Going into {generator_type}...")
    log_indent()
    rule_set = grammar[generator_type]
    non_recursive_possSets = []
    recursive_possSets = []
    for possSet in rule_set:
        if generator_type in possSet:
            recursive_possSets.append(possSet)
        else:
            non_recursive_possSets.append(possSet)
    if recursive_possSets != []:
        log(LOG_VERB, f"Recursive generator type {generator_type}")
        for nr_possSet in non_recursive_possSets:
            lstream = ls.copy()
            node = AST_Node(generator_type, parent, [])
            genPossSet(grammar, lstream, nr_possSet, node)
            valid = False
            while True:
                try:
                    for r_possSet in recursive_possSets:
                        try:
                            ret_node = AST_Node(generator_type, parent, [])
                            genPossSet(grammar, lstream, r_possSet, ret_node,
                                    {generator_type: node})
                            node = ret_node
                            valid = True
                            break
                        except SyntaxError:
                            continue
                except SyntaxError:
                    log(LOG_DEBG, f"Exiting {generator_type}!")
                    if not valid:
                        log(LOG_VERB, f">> Failed for rule '{generator_type}' [210]")
                    else:
                        log(LOG_VERB, f">> R Success for rule '{generator_type}'")
                        ls.update(lstream)
                    log_dedent()
                    return node
                if not valid:
                    log(LOG_DEBG, f"Exiting {generator_type}!")
                    log(LOG_VERB, f">> NR Success for rule '{generator_type}' [211]")
                    print(ls.pointer)
                    log_dedent()
                    return node
        log(LOG_DEBG, f"Exiting {generator_type}!")
        log(LOG_VERB, f">> Failed for rule '{generator_type}' [212]")
        log_dedent()
        cache.set((generator_type, ls.pointer), 0)
        raise SyntaxError("No valid recursive path! [213]")
    for i, possSet in enumerate(rule_set):
        # possSet - one is true
        lstream = ls.copy()
        node = AST_Node(generator_type, parent, [])
        try:
            genPossSet(grammar, lstream, possSet, node)
        except SyntaxError as e:
            log(LOG_VERB, f"Failed for '{rule_set.index(possSet)}' ({e.msg})")
        else:
            log(LOG_VERB, f"Success for '{rule_set.index(possSet)}'")
            log(LOG_DEBG, f"Exiting {generator_type}!")
            log(LOG_VERB, f">> Success for rule '{generator_type}' index {i}")
            log_dedent()
            log(LOG_BASE, "Caching successful result!")
            cache.set((generator_type, ls.pointer),
                      (node.as_one(), lstream.pointer))
            ls.update(lstream)
            return node
    log(LOG_DEBG, f"Exiting {generator_type}!")
    log(LOG_VERB, f">> Failed for rule '{generator_type}'")
    log_dedent()
    cache.set((generator_type, ls.pointer), 0)
    raise SyntaxError("No valid path!")

def parse(lstream: lexer.LexemeStream) -> AST:
    global cache

    cache.clear()

    grammar = load_ebnf("compiler/parser/cpl.ebnf")

    if grammar.get("<translation-unit>", None) is None:
        log(LOG_FAIL, "Invalid grammar! (Missing <translation-unit>)")
        raise SyntaxError
    
    root = AST([])
    n = genASTNode(root, grammar, "<translation-unit>", lstream)
    root.add_child(n)
    return root

def pretty_print(ast: AST_Node | AST, prefix="", lvl=LOG_VERB):
    """Pretty prints a syntax tree"""
    t_char = "├── "
    i_char = "│   "
    l_char = "└── "
    empty  = "    "
    if prefix == "":
        log(lvl, ast.name)
    children = ast.get_children()
    for ast_node in children:
        if ast_node is children[-1]:
            # last child
            pref = prefix + l_char
            log(lvl, pref+ast_node.name)
            pretty_print(ast_node, prefix+empty, lvl=lvl)
        else:
            pref = prefix + t_char
            log(lvl, pref+ast_node.name)
            pretty_print(ast_node, prefix+i_char, lvl=lvl)
