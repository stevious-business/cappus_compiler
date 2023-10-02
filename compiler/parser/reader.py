import re

from cfclogger import *

def parse_rule(str_: str) -> list[tuple]:
    s = str_.split(" ")
    ret = []
    c = []
    while s:
        if len(s) == 1:
            if s[0]:
                ret.append((s[0],))
            break
        while s[0] != "|" and s[0]:
            if s[0] == "\\|":
                c.append("|")
            else:
                c.append(s[0])
            del s[0]
            if not s:
                break
        if s:
            del s[0] # delete |
        ret.append(tuple(c))
        c = []
    return ret

def load_ebnf(fp):
    regex_stmt = r"([^\s+]+) ::= ((.+\n)+)"
    #regex_subst = r"((\b(?<=[^\"])|^)[\w-]+)"

    with open(fp) as f:
        data = f.read().replace("'", '"')
    
    stmt_list = re.findall(regex_stmt, data)

    stmt_dict = {}
    for stmt in stmt_list:
        stmt_dict[stmt[0]] = re.sub(r"\s+", r" ", stmt[1])
    
    if stmt_dict.get("<translation-unit>", None) is None:
        log(LOG_FAIL, "Invalid grammar! (Missing <translation-unit>)")
        raise SyntaxError
    
    grammar = {}
    for key in stmt_dict:
        grammar[key] = parse_rule(stmt_dict[key])
    
    #log(LOG_VERB, f"Grammar: {grammar}")

    return grammar