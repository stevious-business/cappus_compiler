from re import findall, sub

from cfclogger import *

# Assembly, partially in the form of TAC (no register allocation)
class Assembly:
    def __init__(self, lines=[], indenture=0):
        self.lines = lines.copy()
        # Labels are just lines that are also in the ST
        if lines:
            log(LOG_VERB, f"Initializing assembly with {lines}")
        self.indenture = indenture
        self.marked = False
        self.marker = "0"
    
    def __getitem__(self, item):
        try:
            return self.lines[item]
        except IndexError:
            return ""
    
    def add_line(self, line):
        log(LOG_VERB,
            f"Adding {sfmt(line, 25, True)} to marked assembly {self.marker}!"
        )
        self.lines.append(line)
    
    def indent(self):
        self.indenture += 1
    
    def mark(self, id):
        self.marked = True
        self.marker = id
    
    def fuse(self, asm):
        for line in asm.lines.copy():
            self.add_line("    "*self.indenture+line)
        return self
    
    def export(self, f):
        for line in self.lines:
            f.write(line)
            f.write("\n")
    
    def niceout(self, dbg_lvl, cpc):
        for line in self.lines:
            s: str = line
            potentially_replaceables = findall(r"T([0-9]+)", line)
            for replaceable in potentially_replaceables:
                try:
                    sym = cpc.symbol_table.by_t(int(replaceable), False)
                    var_name = sym.name
                    s = sub(f"T{replaceable}\\b", var_name, s)
                    #s = s.replace("T"+replaceable, var_name)
                except KeyError:
                    continue
            log(dbg_lvl, s)