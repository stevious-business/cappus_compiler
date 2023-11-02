from cfclogger import *

class Assembly:
    def __init__(self, lines=[], labels=[]):
        self.lines = lines
        self.labels = labels
    
    def add_line(self, line):
        self.lines.append(line)
    
    def add_label(self, label):
        self.labels.append(label)
    
    def fuse(self, asm):
        return Assembly(self.lines+asm.lines, self.labels+asm.labels)