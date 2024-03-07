from io import TextIOWrapper

class Source:
    def __init__(self, file):
        self.data = file.read()
        self.file = file
        if isinstance(file, TextIOWrapper):
            self.filename = file.name
        else:
            self.filename = "(string)"
        self.length = len(self.data)
        self.ptr = 0
        self.chars = list(self.data)
        self.line = 1
        self.col = 0

    def get(self, _fp=False, depth=1, com=False) -> str:
        if self.ptr < self.length:
            if self.ptr+depth-1 < self.length:
                c: str = self.chars[self.ptr+depth-1]
            else:
                c = "EOF"
        else:
            if _fp:
                # if we were coming from peek function,
                # we must increment pointer because
                # peek function subsequently decrements it
                self.ptr += 1
            return "EOF"
        self.ptr += 1
        if not _fp:     # fp = from peek
            if c == "\n":
                self.line += 1
                self.col = 0
            else:
                self.col += 1
        if not com:     # not (yet) in a comment
            if c == "/":
                if self.peek() == "/":
                    while self.peek(com=True) != "\n":
                        self.get(com=True)
                    self.get()
                    return self.get(com)
                elif self.peek() == "*":
                    while self.get(com=True) != "*" or \
                            self.peek(com=True) != "/":
                        if self.peek(com=True) == "EOF":
                            raise EOFError(
                                f"Unclosed Comment at {self.get_pos()}"
                            )
                    self.get()
                    while self.peek() in " \n\r\t\b":
                        self.get()
                    return self.get()
        return c

    def peek(self, depth=1, com=False) -> str:
        c = self.get(_fp=True, depth=depth, com=com)
        self.ptr -= 1
        return c

    def get_pos(self) -> str:
        return f"<{self.filename}> {self.line}:{self.col}"
