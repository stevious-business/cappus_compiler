from typing import Any

from cfclogger import *

from compiler.lexer import tokens
from compiler.parser import ast

from compiler.codegen import symbol_table as st
from compiler.codegen import asm

from .expressionHelpers import ExpressionHelper


class CPL2CPC:
    def __init__(self, ast_: ast.AST, symbol_table: st.SymbolTable = None,
                 scope=None, t=-1, **kwargs):
        self.t = t
        self.result_t = -1
        self.symbol_table = symbol_table
        self.scope = scope
        self.kwargs = kwargs
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

    def __getattribute__(self, __name: str) -> Any:
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            return self.kwargs[__name]

    def __getitem__(self, item):
        if item.startswith("<"):
            return self.__getattribute__(item[1:-1].replace("-", "_"))
        return self.__getattribute__(item)

    @logAutoIndent
    def generate(self) -> asm.Assembly:
        log(LOG_DEBG, f"Generating on {self.rootType}, T{self.t}")
        self.assembly = self[self.rootType](self.ast.children)
        return self.assembly

    def root(self, children) -> asm.Assembly:
        ass = asm.Assembly()
        for child in children:
            child_ass = CPL2CPC(child, self.symbol_table, t=self.t).generate()
            ass = ass.fuse(child_ass)

        return ass

    # root children
    def translation_unit(
            self,
            children: list[ast.AST_Node | ast.AST_Terminal]) -> asm.Assembly:
        assembly = asm.Assembly()
        for child in children:
            if isinstance(child, ast.AST_Terminal):
                if child.lexeme.value == "EOF":
                    log(
                        LOG_DEBG,
                        "Finished generating assembly for <translation-unit>"
                    )
                    return assembly
                log(LOG_FAIL, f"Error @ {child.lexeme.stamp}")
                raise TypeError(
                    f"Should not get terminal except EOF! Got {child.name}"
                )
            else:
                assembly = assembly.fuse(
                    CPL2CPC(child, self.symbol_table, t=self.t).generate()
                )
        raise SyntaxError("No EOF Token at end of <translation-unit>!")

    # translation-unit children
    def EOF(self, children) -> asm.Assembly:
        return asm.Assembly()

    def function_definition(self,
                            children: list[ast.AST_Node | ast.AST_Terminal]):
        type_spec, name, op, *args, cp, c_statement = children
        name = name.lexeme.value
        # warning about main entrypoint
        if name == "main":
            if args:
                log(LOG_WARN,
                    "You are using arguments for the entrypoint 'main'.",
                    use_indent=False)
                log(LOG_WARN,
                    "When the translation unit is executed by the host \
machine, these may not be provided.",
                    use_indent=False)
                log(LOG_WARN, "This can lead to undefined behavior.",
                    use_indent=False)
        self.symbol_table.add_symbol(st.Symbol(st.SymbolTypes.LABEL, name,
                                     dt=self.dt_from_ast(type_spec)))
        assembly = asm.Assembly([
            f"{name}:",
        ])
        assembly.indent()
        cs_ass = CPL2CPC(c_statement, self.symbol_table,
                         scope=self.symbol_table.by_name(name), t=self.t
                         ).generate()
        assembly.fuse(cs_ass)
        assembly_return = asm.Assembly([
            "RET"
        ])
        assembly.fuse(assembly_return)
        log(
            LOG_DEBG,
            "Finished generating assembly for <function-definition>"
        )
        return assembly

    def dt_from_ast(self, node: ast.AST_Node | ast.AST_Terminal):
        if isinstance(node, ast.AST_Terminal):  # literally just <type-name>
            return node.lexeme.value
        # Else, we must dig deeper
        if node.name == "<scoped-type-specifier>":
            return node[0].lexeme.value + " " + node[1].lexeme.value
        if not isinstance(node, ast.AST_Terminal):
            # pointer
            return node[0].lexeme.value + " *"
        return node.lexeme.value

    # function-definition children
    def compound_statement(self,
                           children: list[ast.AST_Node | ast.AST_Terminal]):
        op, *statements, cp = children
        assembly = asm.Assembly()
        for stmt in statements:
            child_code = CPL2CPC(
                stmt, self.symbol_table, scope=self.scope, t=self.t)
            child_code.generate()
            self.t = child_code.t
            assembly.fuse(child_code.assembly)
        return assembly

    def statement(self,
                  children: list[ast.AST_Node | ast.AST_Terminal]):
        child_code = CPL2CPC(
            children[0], self.symbol_table, scope=self.scope, t=self.t
        )
        child_code.generate()
        self.t = child_code.t
        return child_code.assembly

    # expressions
    def expression_helper(self, children, expr_fmt) -> asm.Assembly:
        """
        :expr_fmt: dict format:
        {
            "expression_name": str,
            "<symbol_name>": {
                "op_regs": str,
                "op_imm": str,
                "commutative": bool,
                "dual_imm_func": str
            }
        }
        """
        # Always the same
        l_operand = CPL2CPC(children[0], self.symbol_table, self.scope, self.t)
        l_operand.generate()
        left_imm = l_operand.assembly[-1] \
            .startswith(f"LDI T{l_operand.result_t}")
        lt_or_selft = (self.t if left_imm else l_operand.t)
        r_operand = CPL2CPC(
            children[2], self.symbol_table, self.scope, lt_or_selft
        )
        r_operand.generate()
        operator_symbol = children[1].lexeme.value
        op_regs = ""
        op_imm = ""
        right_imm = r_operand.assembly[-1] \
            .startswith(f"LDI T{r_operand.result_t}")

        # Different for different expression types
        try:
            operator_fmt = expr_fmt[operator_symbol]
            op_regs = operator_fmt["op_regs"]
            op_imm = operator_fmt["op_imm"]
            is_commutative = operator_fmt["commutative"]
            dual_imm_fn_name = operator_fmt["dual_imm_func"]
        except KeyError:
            log(LOG_FAIL,
                "Invalid expr_fmt! (name %s, symbol %s)" % (
                    expr_fmt["expression_name"], operator_symbol
                ), use_indent=False)
            raise

        if (right_imm == 1 and left_imm == 0):
            # right is immediate, immediate format
            # optimization: reuse T's if they aren't reserved for vars
            self.t = l_operand.t + 1
            if not self.symbol_table.has_t(l_operand.result_t):
                self.result_t = l_operand.result_t
                self.t = l_operand.t
            else:
                self.result_t = self.t
            value = int(r_operand.assembly.lines[-1].split()[-1])
            line = f"{op_imm} T{self.result_t}, T{l_operand.result_t}, {value}"
            self.assembly = self.assembly.fuse(l_operand.assembly)
            self.assembly = self.assembly.fuse(asm.Assembly([line]))
            return self.assembly
        elif (right_imm == 0 and left_imm == 1):
            # left is immediate, imm-format if adding
            if is_commutative:
                self.t = r_operand.t + 1
                if not self.symbol_table.has_t(r_operand.result_t):
                    self.result_t = r_operand.result_t
                    self.t = r_operand.t
                else:
                    self.result_t = self.t
                value = int(l_operand.assembly.lines[-1].split()[-1])
                line = "%s T%d, T%d, %d" % (
                    op_imm,
                    self.result_t,
                    r_operand.result_t,
                    value
                )
                r_operand = CPL2CPC(
                    children[2], self.symbol_table, self.scope, self.t
                )
                r_operand.generate()
                self.assembly = self.assembly.fuse(r_operand.assembly)
                self.assembly = self.assembly.fuse(asm.Assembly([line]))
                return self.assembly
        elif (right_imm & left_imm):
            # both are immediates, calculate value immediately
            lvalue = int(l_operand.assembly.lines[-1].split()[-1])
            rvalue = int(r_operand.assembly.lines[-1].split()[-1])
            svalue = ExpressionHelper().__getattribute__(dual_imm_fn_name)(
                lvalue, rvalue
            )
            self.t += 1
            self.result_t = self.t
            line = f"LDI T{self.t}, {svalue}"
            self.assembly = self.assembly.fuse(asm.Assembly([line]))
            return self.assembly

        # normal procedure
        self.t = r_operand.t + 1
        if not self.symbol_table.has_t(l_operand.result_t):
            self.result_t = l_operand.result_t
            self.t = r_operand.t
        else:
            self.result_t = self.t
        line = "%s T%d, T%d, T%d" % (
            op_regs,
            self.result_t,
            l_operand.result_t,
            r_operand.result_t
        )
        self.assembly = self.assembly.fuse(l_operand.assembly) \
                            .fuse(r_operand.assembly)
        self.assembly = self.assembly.fuse(asm.Assembly([line]))
        return self.assembly

    def expression_template(self, children):
        return self.expression_helper(children, {
            "expression_name": "",
            "": {
                "op_regs": "",
                "op_imm": "",
                "commutative": False,
                "dual_imm_func": ""
            },
        })

    def logical_or_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "logical-or-expression",
            "||": {
                "op_regs": "LOR",
                "op_imm": "LOI",
                "commutative": True,
                "dual_imm_func": "logical_or"
            }
        })

    def logical_and_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "logical-and-expression",
            "&&": {
                "op_regs": "LAN",
                "op_imm": "LAI",
                "commutative": True,
                "dual_imm_func": "logical_and"
            }
        })

    def inclusive_or_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "inclusive-or-expression",
            "|": {
                "op_regs": "ORR",
                "op_imm": "ORI",
                "commutative": True,
                "dual_imm_func": "bw_or"
            }
        })

    def exclusive_or_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "exclusive-or-expression",
            "^": {
                "op_regs": "XOR",
                "op_imm": "XRI",
                "commutative": True,
                "dual_imm_func": "bw_xor"
            }
        })

    def and_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "and-expression",
            "&": {
                "op_regs": "AND",
                "op_imm": "ANI",
                "commutative": True,
                "dual_imm_func": "bw_and"
            }
        })

    def equality_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "equality-expression",
            "==": {
                "op_regs": "EQU",
                "op_imm": "EQI",
                "commutative": True,
                "dual_imm_func": "eq"
            },
            "!=": {
                "op_regs": "NEQ",
                "op_imm": "NQI",
                "commutative": True,
                "dual_imm_func": "neq"
            },
        })

    def relational_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "relational-expression",
            "<": {
                "op_regs": "LTR",
                "op_imm": "LTI",
                "commutative": False,
                "dual_imm_func": "lt"
            },
            ">": {
                "op_regs": "GTR",
                "op_imm": "GTI",
                "commutative": False,
                "dual_imm_func": "gt"
            },
            ">=": {
                "op_regs": "GTE",
                "op_imm": "GEI",
                "commutative": False,
                "dual_imm_func": "ge"
            },
            "<=": {
                "op_regs": "LTE",
                "op_imm": "LEI",
                "commutative": False,
                "dual_imm_func": "le"
            },
        })

    def shift_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "shift-expression",
            "<<": {
                "op_regs": "LSH",
                "op_imm": "LSI",
                "commutative": False,
                "dual_imm_func": "lsh"
            },
            ">>": {
                "op_regs": "RSH",
                "op_imm": "RSI",
                "commutative": False,
                "dual_imm_func": "rsh"
            },
        })

    def additive_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "additive-expression",
            "+": {
                "op_regs": "ADD",
                "op_imm": "ADI",
                "commutative": True,
                "dual_imm_func": "add"
            },
            "-": {
                "op_regs": "SUB",
                "op_imm": "SBI",
                "commutative": False,
                "dual_imm_func": "sub"
            }
        })

    def multiplicative_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "multiplicative-expression",
            "*": {
                "op_regs": "MUL",
                "op_imm": "MLI",
                "commutative": True,
                "dual_imm_func": "mul"
            },
            "/": {
                "op_regs": "DIV",
                "op_imm": "DVI",
                "commutative": False,
                "dual_imm_func": "div"
            },
            "%": {
                "op_regs": "MOD",
                "op_imm": "MDI",
                "commutative": False,
                "dual_imm_func": "mod"
            },
        })

    def power_expression(self, children):
        return self.expression_helper(children, {
            "expression_name": "power-expression",
            "**": {
                "op_regs": "POW",
                "op_imm": "PWI",
                "commutative": False,
                "dual_imm_func": "pow"
            },
        })

    def INTEGER(self, children):
        self.t += 1
        self.result_t = self.t
        assembly = asm.Assembly([
            f"LDI T{self.result_t}, {self.ast.lexeme.value}"
        ])
        return assembly

    def primary_expression(
            self, children: list[ast.AST_Node | ast.AST_Terminal]):
        if children[0].lexeme.tokenType == tokens.TokenType.OPENPAR:
            assembly = CPL2CPC(
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
            self.t += 1
            self.symbol_table.add_symbol(st.Symbol(
                    st.SymbolTypes.VARIABLE, name, type_, self.t
                )
            )
            return assembly
        # length must be three (see cpl.ebnf)
        type_node, name_node, initialization_node = children
        type_ = self.dt_from_ast(type_node)
        name = name_node.lexeme.value
        self.t += 1
        self.symbol_table.add_symbol(st.Symbol(
                st.SymbolTypes.VARIABLE, name, type_, self.t
            )
        )
        generator = CPL2CPC(
            initialization_node, self.symbol_table, self.scope, self.t,
            modifiable=self.t
        )
        asm_code = generator.generate()
        assembly = assembly.fuse(asm_code)
        self.t = generator.t
        self.result_t = generator.result_t

        return assembly

    def assignment_expression(self, children:
                              list[ast.AST_Node | ast.AST_Terminal]):
        assembly = asm.Assembly()
        name_node, initialization_node = children
        name = name_node.lexeme.value
        modifiable = self.symbol_table.by_name(name)
        if isinstance(initialization_node, ast.AST_Terminal):
            operator_lexeme = initialization_node.lexeme
            log(LOG_VERB,
                f"Found postfix @ {operator_lexeme.stamp}!")
            assert operator_lexeme.tokenType \
                == tokens.TokenType.OPERATOR
            if operator_lexeme.value == "++":
                log(LOG_BASE, "Postfix type '++'")
                assembly.add_line(f"INC T{modifiable.var_t}")
            elif operator_lexeme.value == "--":
                log(LOG_BASE, "Postfix type '--'")
                assembly.add_line(f"DEC T{modifiable.var_t}")
            else:
                log(LOG_FAIL, f"Invalid postfix '{operator_lexeme.value}'")
                raise ValueError
        else:
            generator = CPL2CPC(
                initialization_node, self.symbol_table, self.scope, self.t,
                modifiable=modifiable.var_t
            )
            asm_code = generator.generate()
            self.t = generator.t
            self.result_t = generator.result_t
            assembly = assembly.fuse(asm_code)

        return assembly

    def init_assignment(self, children:
                        list[ast.AST_Node | ast.AST_Terminal]):
        # len 2
        # due to syntax, children[0] is an ast_terminal
        if children[0].lexeme.value != "=":
            raise NotImplementedError    # TODO: Implement assignment operators

        generator = CPL2CPC(
            children[1], self.symbol_table, self.scope, self.t
        )
        asm_code = generator.generate()
        self.t = generator.result_t-1
        self.result_t = self.modifiable
        op, target_t, *rest = generator.assembly[-1].split()
        generator.assembly.lines[-1] = \
            f"{op} T{self.modifiable}, {' '.join(rest)}"
        return asm_code

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
