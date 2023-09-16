import re

from cfclogger import *

def load_ebnf(fp):
    regex_stmt = r"([^\s+]+) ::= ((.+\n)+)"
    regex_subst = r"((\b(?<=[^\"])|^)[\w-]+)"

    with open(fp) as f:
        data = f.read()
    
    stmt_list = re.findall(regex_stmt, data)

    stmt_dict = {}
    for stmt in stmt_list:
        stmt_dict[stmt[0]] = re.sub(r"\s+", r" ", stmt[1])
    
    if stmt_dict.get("translation-unit", None) is None:
        log(LOG_FAIL, "Invalid grammar! (Missing translation-unit)")
        raise SyntaxError
    
    return stmt_dict