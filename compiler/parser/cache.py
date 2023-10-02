from sys import getsizeof

class Cache:
    def __init__(self):
        self.entries = {}
    
    def size(self):
        return getsizeof(self.entries)
    
    def __getitem__(self, item: tuple):
        return self.entries.get(item, None)

    def clear(self):
        self.__init__()
    
    def set(self, item: tuple, value):
        self.entries[item] = value