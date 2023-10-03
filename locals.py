LOG_BASE = 0 # dump everything
LOG_VERB = 1 # realistically everything that should be known
LOG_DEBG = 2 # general structure and program trace
LOG_INFO = 3 # user-level output
LOG_WARN = 4 # important mishaps
LOG_FAIL = 5 # absolute failure

SW_NAME = "CFC" # Compiler For Cappus

class DBGLVL:
    def __init__(self, lvl):
        self.lvl = lvl
    
    def set(self, lvl):
        self.lvl = lvl

    def get(self):
        return self.lvl

DBG = DBGLVL(LOG_DEBG)
