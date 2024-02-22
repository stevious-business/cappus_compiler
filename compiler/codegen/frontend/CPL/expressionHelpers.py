from typing import Any

class ExpressionHelper:
    def logical_or(a: int, b: int) -> int:
        return a or b
    
    def logical_and(a: int, b: int) -> int:
        return a and b
    
    def bw_or(a: int, b: int) -> int:
        return a | b
    
    def bw_and(a: int, b: int) -> int:
        return a & b
    
    def bw_xor(a: int, b: int) -> int:
        return a ^ b
    
    def eq(a: int, b: int) -> int:
        return a == b
    
    def neq(a: int, b: int) -> int:
        return a != b
    
    def lt(a: int, b: int) -> int:
        return a < b
    
    def gt(a: int, b: int) -> int:
        return a > b
    
    def le(a: int, b: int) -> int:
        return a <= b
    
    def ge(a: int, b: int) -> int:
        return a >= b
    
    def lsh(a: int, b: int) -> int:
        return a << b
    
    def rsh(a: int, b: int) -> int:
        return a >> b
    
    def add(a: int, b: int) -> int:
        return a + b
    
    def sub(a: int, b: int) -> int:
        return a - b
    
    def mul(a: int, b: int) -> int:
        return a * b
    
    def div(a: int, b: int) -> int:
        return a // b
    
    def mod(a: int, b: int) -> int:
        return a % b
    
    def pow(a: int, b: int) -> int:
        return a ** b