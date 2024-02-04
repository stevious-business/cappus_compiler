from .reader import load_ebnf
from .ast import AST, AST_Node, AST_Terminal

from compiler.lexer import tokens, lexer

from cfclogger import *

from .cache import Cache

cache = Cache()

@logAutoIndent
def generate_rule(grammar, lstream, possSet, node, possPreset={}):
    global cache
    # possPreset: dict[str: (lsptr, node)]
    for poss in possSet: # poss - all are true
        if possPreset.get(poss, None) is not None:
            # preset is there
            node.add_child(possPreset[poss][1])
            possPreset[poss][1].parent = node
            lstream.pointer = possPreset[poss][0]
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

def obtain_subsets(generator_type: str, rule_set):
    non_recursive_subSets = []
    recursive_subSets = []
    for possSet in rule_set:
        if possSet[0] == generator_type:
            recursive_subSets.append(possSet)
        else:
            non_recursive_subSets.append(possSet)
    return non_recursive_subSets, recursive_subSets

def check_cache(generator_type, ls: lexer.LexemeStream):
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

def gen_terminal(generator_type, grammar, ls, parent):
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

def genASTNode(parent, grammar: dict, generator_type: str,
           ls: lexer.LexemeStream) -> AST_Node:

    log(LOG_DEBG, f"Going into {generator_type}...")

    if ret := check_cache(generator_type, ls): return ret

    if ret := gen_terminal(generator_type, grammar, ls, parent): return ret
    
    rule_set = grammar[generator_type]
    non_recursive_subSets, recursive_subSets = obtain_subsets(generator_type,
                                                              rule_set)
    
    recursiveNode: AST_Node = None
    for i, possSet in enumerate(rule_set):
        if possSet not in non_recursive_subSets: continue
        lstream = ls.copy()
        node = AST_Node(generator_type, parent, [])
        try:
            generate_rule(grammar, lstream, possSet, node)
        except SyntaxError:
            # pf = partial failure
            log(LOG_VERB, f"[PF] Type {generator_type}, opt {i}")
        else:
            recursiveNode = node
            break
    
    if recursiveNode is None:
        log(LOG_DEBG, f"[F] Type {generator_type}, ptr {ls.pointer}")
        cache.set((generator_type, ls.pointer), 0)
        raise SyntaxError("No valid path!")
    
    success = True
    while success: # loop that will perform the recursion
        success = False
        for i, possSet in enumerate(rule_set):
            if possSet not in recursive_subSets: continue
            # try to loop over recursive possibilities to find one that works
            lstream2 = ls.copy()
            parent_node = AST_Node(generator_type, parent, [])
            try:
                generate_rule(grammar, lstream2, possSet, parent_node,
                    {generator_type: (lstream.pointer, recursiveNode)})
            except SyntaxError:
                # pf = partial failure
                log(LOG_VERB, f"[PF] Type {generator_type}, opt {i}")
            else:
                recursiveNode = parent_node
                success = True
                lstream.update(lstream2)
                break
    log(LOG_DEBG,
        f"[S] Type {generator_type}, opt {i}, ptr {lstream.pointer}")
    log(LOG_BASE, "Caching successful result!")
    cache.set((generator_type, ls.pointer),
                (recursiveNode.as_one(), lstream.pointer))
    ls.update(lstream)
    return recursiveNode.as_one()


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
