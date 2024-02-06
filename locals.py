LOG_BASE = 0 # dump everything
LOG_VERB = 1 # realistically everything that should be known
LOG_DEBG = 2 # general structure and program trace
LOG_INFO = 3 # user-level output
LOG_WARN = 4 # important mishaps
LOG_FAIL = 5 # absolute failure

SW_NAME = "CFC" # Compiler For Cappus

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

class VerboseOptions(DebugOptions):
    pass

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

class LexerDebuggingOptions(OnlyFatalOptions): # includes source fetcher
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

class CustomDebuggingOptions(DebugOptions):
    pass

class DBGLVL:
    def __init__(self, lvl):
        self.lvl = lvl
        self.floor = 0
    
    def set(self, lvl):
        if lvl >= self.floor:
            self.lvl = lvl
    
    def set_floor(self, lvl):
        self.floor = lvl
        if self.lvl < lvl:
            self.lvl = lvl

    def get(self):
        return self.lvl

DBG = DBGLVL(LOG_DEBG)