LOG_BASE = 0    # dump everything
LOG_VERB = 1    # realistically everything that should be known
LOG_DEBG = 2    # general structure and program trace
LOG_INFO = 3    # user-level output
LOG_WARN = 4    # important mishaps
LOG_FAIL = 5    # absolute failure
LOG_SILENT_MODE = 6     # For setting floor

SW_NAME = "CFC"     # Compiler For Cappus

EXPECTATIONS_TABLE = {
    "s": "SOURCE",
    "l": "LEXEMES",
    "a": "AST",
    "i": "INTERMEDIATE",
    "t": "SYM_TAB"
}

META_BLOCK = """--- START META ---

NAME %s
DESCRIPTION A unit test

--- END ---
"""

CODE_BLOCK = """--- START TEST_CODE ---

%s

--- END ---
"""

EXPECTATION_BLOCK = """--- START EXPECTED_%s ---

%s

--- END ---
"""


class DebugOptions:
    FLOOR = 0
    LVL_SOURCE_FETCH = 0
    LVL_LEXING = 0
    LVL_LEXOUT = 0
    LVL_PARSING = 0
    LVL_PARSEOUT = 0
    LVL_CODEGEN = 0
    LVL_SYMTABOUT = 0
    LVL_ASMOUT = 0


class VerboseOutputOptions(DebugOptions):
    FLOOR = LOG_VERB


class DebugOutputOptions(DebugOptions):
    FLOOR = LOG_DEBG

class WarningOutputOptions(DebugOptions):
    FLOOR = LOG_WARN


class OnlyFatalOptions(DebugOptions):
    FLOOR = LOG_FAIL
    LVL_SOURCE_FETCH = LOG_FAIL
    LVL_LEXING = LOG_FAIL
    LVL_LEXOUT = LOG_FAIL
    LVL_PARSING = LOG_FAIL
    LVL_PARSEOUT = LOG_FAIL
    LVL_CODEGEN = LOG_FAIL
    LVL_SYMTABOUT = LOG_FAIL
    LVL_ASMOUT = LOG_FAIL


class StandardUsageOptions(DebugOptions):
    FLOOR = LOG_INFO


class LexerDebuggingOptions(OnlyFatalOptions):  # includes source fetcher
    FLOOR = LOG_BASE
    LVL_LEXING = LOG_BASE
    LVL_LEXOUT = LOG_BASE


class ParserDebuggingOptions(OnlyFatalOptions):
    FLOOR = LOG_BASE
    LVL_PARSING = LOG_BASE
    LVL_PARSEOUT = LOG_BASE


class CodeGenDebuggingOptions(OnlyFatalOptions):
    FLOOR = LOG_BASE
    LVL_CODEGEN = LOG_BASE
    LVL_SYMTABOUT = LOG_BASE
    LVL_ASMOUT = LOG_BASE


class CustomDebuggingOptions(CodeGenDebuggingOptions):
    LVL_PARSEOUT = LOG_DEBG


class DBGLVL:
    def __init__(self, lvl):
        self.lvl = lvl
        self.floor = 0
        self.silent = False

    def set(self, lvl):
        if lvl >= self.floor:
            self.lvl = lvl
    
    def set_silent(self, is_silent):
        self.silent = is_silent

    def set_floor(self, lvl):
        self.floor = lvl
        if self.lvl < lvl:
            self.lvl = lvl

    def get(self):
        return LOG_SILENT_MODE if self.silent else self.lvl


DBG = DBGLVL(LOG_DEBG)
