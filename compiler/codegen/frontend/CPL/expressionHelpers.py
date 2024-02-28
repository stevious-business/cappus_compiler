class ExpressionHelper:
    def logical_or(self, a: int, b: int) -> int:
        return a or b
    
    def logical_and(self, a: int, b: int) -> int:
        return a and b
    
    def bw_or(self, a: int, b: int) -> int:
        return a | b
    
    def bw_and(self, a: int, b: int) -> int:
        return a & b
    
    def bw_xor(self, a: int, b: int) -> int:
        return a ^ b
    
    def eq(self, a: int, b: int) -> int:
        return a == b
    
    def neq(self, a: int, b: int) -> int:
        return a != b
    
    def lt(self, a: int, b: int) -> int:
        return a < b
    
    def gt(self, a: int, b: int) -> int:
        return a > b
    
    def le(self, a: int, b: int) -> int:
        return a <= b
    
    def ge(self, a: int, b: int) -> int:
        return a >= b
    
    def lsh(self, a: int, b: int) -> int:
        return a << b
    
    def rsh(self, a: int, b: int) -> int:
        return a >> b
    
    def add(self, a: int, b: int) -> int:
        return a + b
    
    def sub(self, a: int, b: int) -> int:
        return a - b
    
    def mul(self, a: int, b: int) -> int:
        return a * b
    
    def div(self, a: int, b: int) -> int:
        return a // b
    
    def mod(self, a: int, b: int) -> int:
        return a % b
    
    def pow(self, a: int, b: int) -> int:
        return a ** b
