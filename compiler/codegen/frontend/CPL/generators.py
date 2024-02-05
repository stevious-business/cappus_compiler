from cfclogger import *

from compiler.lexer import tokens
from compiler.parser import ast

from compiler.codegen import symbol_table as st
from compiler.codegen import asm

class CPL2CAL:
    def __init__(self, ast_: ast.AST, symbol_table: st.SymbolTable = None,
                 scope=None, t=-1, parent=None):
        self.t = t
        self.result_t = -1
        self.symbol_table = symbol_table
        self.scope = scope
        self.parent = parent
        self.assembly = asm.Assembly()
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

    @logAutoIndent
    def generate(self):
        log(LOG_DEBG, f"Generating on {self.rootType}")
        self.assembly = self[self.rootType](self.ast.children)
        return self.assembly
    
    def root(self, children) -> asm.Assembly:
        ass = asm.Assembly()
        for child in children:
            child_ass = CPL2CAL(child, self.symbol_table, t=self.t).generate()
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
                    CPL2CAL(child, self.symbol_table, t=self.t).generate()
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
                    "When the translation unit is executed by the host \
machine, these may not be provided.")
                log(LOG_WARN, "This can lead to undefined behavior.")
        self.symbol_table.add_symbol(st.Symbol(st.SymbolTypes.LABEL, name,
                                       dt=self.dt_from_ast(type_spec)))
        assembly = asm.Assembly([
            f"{name}:",
        ])
        assembly.indent()
        cs_ass = CPL2CAL(c_statement, self.symbol_table,
                         scope=self.symbol_table.by_name(name), t=self.t
                         ).generate()
        assembly.fuse(cs_ass)
        assembly_return = asm.Assembly([
            "RET"
        ])
        assembly.fuse(assembly_return)
        log(LOG_DEBG,
            "Finished generating assembly for <function-definition>"
        )
        return assembly
    
    def dt_from_ast(self, node: ast.AST_Node | ast.AST_Terminal):
        if isinstance(node, ast.AST_Terminal): # literally just <type-name>
            return node.lexeme.value
        # Else, we must dig deeper
        if node.name == "<scoped-type-specifier>":
            return node[0].lexeme.value + " " + node[1].lexeme.value
        if type(node) == ast.AST_Node: # isinstance fucks due to bad parents
            # pointer
            return node[0].lexeme.value + " *"
        return node.lexeme.value

    # function-definition children
    def compound_statement(self,
            children: list[ast.AST_Node | ast.AST_Terminal]) -> asm.Assembly:
        op, *statements, cp = children
        assembly = asm.Assembly()
        for stmt in statements:
            child_code = CPL2CAL(
                stmt, self.symbol_table, scope=self.scope, t=self.t)
            child_code.generate()
            self.t = child_code.t
            assembly.fuse(child_code.assembly)
        return assembly
    
    def statement(self,
            children: list[ast.AST_Node | ast.AST_Terminal]) -> asm.Assembly:
        child_code = CPL2CAL(
            children[0], self.symbol_table, scope=self.scope, t=self.t
        )
        child_code.generate()
        self.t = child_code.t
        return child_code.assembly

    def additive_expression(self,
            children: list[ast.AST_Node | ast.AST_Terminal]) -> asm.Assembly:
        # Always the same
        l = CPL2CAL(children[0], self.symbol_table, self.scope, self.t)
        r = CPL2CAL(children[2], self.symbol_table, self.scope, l.t)
        l.generate()
        r.generate()
        operator_symbol = children[1].lexeme.value
        op_regs = ""
        op_imm = ""
        right_imm = r.assembly[-1].startswith(f"LDI T{r.result_t}")
        left_imm = l.assembly[-1].startswith(f"LDI T{l.result_t}")

        # Different for different expression types
        if operator_symbol == "+":
            op_regs = "ADD"
            op_imm = "ADI"
        elif operator_symbol == "-":
            op_regs = "SUB"
            op_imm = "SBI"
        
        if (right_imm == 1 and left_imm == 0):
            # right is immediate, immediate format
            self.t = l.t + 1
            self.result_t = self.t
            value = int(r.assembly.lines[-1].split()[-1])
            line = f"{op_imm} T{self.result_t}, T{l.result_t}, {value}"
            self.assembly = self.assembly.fuse(l.assembly)
            self.assembly = self.assembly.fuse(asm.Assembly([line]))
            return self.assembly
        elif (right_imm == 0 and left_imm == 1):
            # left is immediate, imm-format if adding
            if operator_symbol == "+":
                self.t = r.t + 1
                self.result_t = r.t
                value = int(l.assembly.lines[-1].split()[-1])
                line = f"{op_imm} T{self.result_t}, T{r.result_t}, {value}"
                r = CPL2CAL(children[2], self.symbol_table, self.scope, self.t
                    ).generate()
                self.assembly = self.assembly.fuse(r.assembly)
                self.assembly = self.assembly.fuse(asm.Assembly([line]))
                return self.assembly
        elif (right_imm & left_imm):
            # both are immediates, calculate value immediately
            lvalue = int(l.assembly.lines[-1].split()[-1])
            rvalue = int(r.assembly.lines[-1].split()[-1])
            if operator_symbol == "+":
                svalue = lvalue+rvalue
            else:
                svalue = lvalue-rvalue
            self.t += 1
            self.result_t = self.t
            line = f"LDI T{self.t}, {svalue}"
            self.assembly = self.assembly.fuse(asm.Assembly([line]))
            return self.assembly

        # normal procedure
        self.t = r.t + 1
        self.result_t = self.t
        line = f"{op_regs} T{self.result_t}, T{l.result_t}, T{r.result_t}"
        self.assembly = self.assembly.fuse(l.assembly).fuse(r.assembly)
        self.assembly = self.assembly.fuse(asm.Assembly([line]))
        return self.assembly
    
    def INTEGER(self, children):
        self.t += 1
        self.result_t = self.t
        assembly = asm.Assembly([
            f"LDI T{self.result_t}, {self.ast.lexeme.value}"
        ])
        return assembly
    
    def primary_expression(self,
            children: list[ast.AST_Node | ast.AST_Terminal]):
        if children[0].lexeme.tokenType == tokens.TokenType.OPENPAR:
            assembly = CPL2CAL(
                children[1], self.symbol_table, self.scope, self.t
            )
            assembly_code = assembly.generate()
            self.t = assembly.t
            self.result_t = assembly.result_t
            return assembly_code
    
    def declaration(self, children:
                    list[ast.AST_Node | ast.AST_Terminal]):
        assembly = asm.Assembly()
        if len(children) == 2:
            type_node, name_node = children
            type_ = self.dt_from_ast(type_node)
            name = name_node.lexeme.value
        else:
            # length must be three (see cpl.ebnf)
            type_node, name_node, initialization_node = children
            type_ = self.dt_from_ast(type_node)
            name = name_node.lexeme.value
            generator = CPL2CAL(
                initialization_node, self.symbol_table, self.scope, self.t
            )
        self.t += 1
        self.symbol_table.add_symbol(st.Symbol(
                st.SymbolTypes.VARIABLE, name, type_, self.t
            )
        )

        return assembly

    def IDENTIFIER(self, children):
        try:
            symbol = self.symbol_table.by_name(self.ast.lexeme.value)
            if symbol.type_ is not st.SymbolTypes.VARIABLE:
                raise TypeError(f"Expected VARIABLE, got {symbol.type_.name}!")
            if symbol.var_t == -1:
                raise ValueError("Inappropriate value for symbol.var_t!")
            self.result_t = symbol.var_t
        except KeyError:
            raise NameError(f"Name '{self.ast.lexeme.value}' is not defined")
        return asm.Assembly()