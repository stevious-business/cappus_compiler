from cfclogger import *

from compiler.lexer import tokens
from compiler.parser import ast

from compiler.codegen import symbol_table as st
from compiler.codegen import asm

class CPL2CAL:
    def __init__(self, ast_: ast.AST, symbol_table: st.SymbolTable = None,
                 scope=None):
        self.symbol_table = symbol_table
        self.scope = scope
        if self.symbol_table is None:
            self.symbol_table = st.SymbolTable()
            self.symbol_table.add_symbol(
                st.Symbol(st.SymbolTypes.LABEL, "global")
            )
            self.scope = self.symbol_table.by_name("global")
        self.ast = ast_
        self.rootType = self.ast.name
        if isinstance(self.ast, ast.AST_Terminal):
            self.rootType = self.ast.lexeme.tokenType.name

    def __getitem__(self, item):
        if item.startswith("<"):
            return self.__getattribute__(item[1:-1].replace("-", "_"))
        return self.__getattribute__(item)

    def generate(self):
        log(LOG_DEBG, f"Generating on {self.rootType}")
        return self[self.rootType](self.ast.children)
    
    def root(self, children) -> asm.Assembly:
        ass = asm.Assembly()
        ass.mark("root")
        for child in children:
            print(ass.lines)
            child_ass = CPL2CAL(child, self.symbol_table).generate()
            ass = ass.fuse(child_ass)
        
        return ass
    
    # root children
    def translation_unit(self,
                        children: list[
                            ast.AST_Node | ast.AST_Terminal
                        ]) -> asm.Assembly:
        assembly = asm.Assembly()
        assembly.mark("t-u")
        for child in children:
            if isinstance(child, ast.AST_Terminal):
                if child.lexeme.value == "EOF":
                    log(LOG_DEBG,
                        "Finished generating assembly for <translation-unit>"
                    )
                    return assembly
                log(LOG_FAIL, f"Error @ {child.lexeme.stamp}")
                raise TypeError(
                    f"Should not get terminal except EOF! Got {child.name}"
                )
            else:
                assembly = assembly.fuse(
                    CPL2CAL(child, self.symbol_table).generate()
                )
        raise SyntaxError("No EOF Token at end of <translation-unit>!")
    
    # translation-unit children
    def EOF(self, children) -> asm.Assembly:
        return asm.Assembly()
    
    def function_definition(self,
            children: list[ast.AST_Node | ast.AST_Terminal]) -> asm.Assembly:
        type_spec, name, op, *args, cp, c_statement = children
        name = name.lexeme.value
        # warning about main entrypoint
        if name == "main":
            if args:
                log(LOG_WARN,
                    "You are using arguments for the entrypoint 'main'.")
                log(LOG_WARN,
                    "When the translation unit is executed by the host\
machine, these may not be provided.")
                log(LOG_WARN, "This can lead to undefined behavior.")
        self.symbol_table.add_symbol(st.Symbol(st.SymbolTypes.LABEL, name))
        assembly = asm.Assembly([
            f"{name}:",
        ])
        assembly.mark("f-d")
        assembly.indent()
        cs_ass = CPL2CAL(c_statement, self.symbol_table,
                         scope=self.symbol_table.by_name(name)).generate()
        assembly.fuse(cs_ass)
        assembly_return = asm.Assembly([
            "RET"
        ])
        assembly.fuse(assembly_return)
        log(LOG_DEBG,
            "Finished generating assembly for <function-definition>"
        )
        return assembly
    
    # function-definition children
    def compound_statement(self,
            children: list[ast.AST_Node | ast.AST_Terminal]) -> asm.Assembly:
        op, *statements, cp = children
        assembly = asm.Assembly()
        for stmt in statements:
            assembly.fuse(
                CPL2CAL(stmt, self.symbol_table, scope=self.scope).generate()
            )
        return assembly
    
    def statement(self,
            children: list[ast.AST_Node | ast.AST_Terminal]) -> asm.Assembly:
        return CPL2CAL(
            children[0], self.symbol_table, scope=self.scope
        ).generate()