from compiler.lexer import tokens


class AST_Node:
    def __init__(self, name, parent, children: list = []):
        self.parent = parent
        self.children = children
        self.name = name

    def add_child(self, child):
        self.children.append(child)

    def get_children(self):
        return self.children

    def count_children(self):
        return len(self.children)

    def __getitem__(self, item):
        return self.children[item]

    def as_one(self):   # Return exactly one node, and child if possible
        if len(self.children) == 1:
            return self.children[0]
        for i, child in enumerate(self.children):
            self.children[i] = child.as_one()
        return self


class AST_Terminal(AST_Node):
    def __init__(self, parent: AST_Node, lexeme: tokens.Lexeme):
        super().__init__("terminal", parent, [])
        self.lexeme = lexeme
        self.name = f"{self.lexeme.tokenType.name}: {self.lexeme.value}"

    def get(self):
        return self.lexeme

    def set(self, lexeme: tokens.Lexeme):
        self.lexeme = lexeme


class AST(AST_Node):
    def __init__(self, children: list = []):
        self.name = "root"
        self.children = []
