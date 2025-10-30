import sys

from Expression import *
from Lexer import Token, TokenType

"""
Precedence table:
    1: not ~ ()
    2: *   /
    3: +   -
    4: <   <=   >=   >
    5: =
    6: and
    7: or
    8: if-then-else

Notice that not 2 < 3 must be a type error, as we are trying to apply a boolean
operation (not) onto a number. However, in assembly code this program works,
because not 2 is 0. The bottom line is: don't worry about programs like this
one: the would have been ruled out by type verification anyway.

References:
    see https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm#classic
"""

class Parser:
    def __init__(self, tokens):
        """
        Initializes the parser. The parser keeps track of the list of tokens
        and the current token. For instance:
        """
        self.tokens = iter(tokens)  # iterador
        self.current_token = next(self.tokens, Token("", TokenType.EOF))

    def advance(self):
        self.current_token = next(self.tokens, Token("", TokenType.EOF))

    def parse(self):
        """
        Returns the expression associated with the stream of tokens.

        Examples:
        >>> parser = Parser([Token('123', TokenType.NUM)])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        123

        >>> parser = Parser([Token('True', TokenType.TRU)])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> parser = Parser([Token('False', TokenType.FLS)])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        False

        >>> tk0 = Token('~', TokenType.NEG)
        >>> tk1 = Token('123', TokenType.NUM)
        >>> parser = Parser([tk0, tk1])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        -123

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        12

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('~', TokenType.NEG)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        -12

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('/', TokenType.DIV)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        7

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('+', TokenType.ADD)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        7

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('-', TokenType.SUB)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        26

        >>> tk0 = Token('2', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('(', TokenType.LPR)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('4', TokenType.NUM)
        >>> tk6 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        14

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('==', TokenType.EQL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<=', TokenType.LEQ)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<', TokenType.LTH)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        False

        >>> tk0 = Token('not', TokenType.NOT)
        >>> tk1 = Token('(', TokenType.LPR)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> tk3 = Token('<', TokenType.LTH)
        >>> tk4 = Token('4', TokenType.NUM)
        >>> tk5 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('or', TokenType.ORX)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        True

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('and', TokenType.AND)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        False

        >>> tk0 = Token('let', TokenType.LET)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('<-', TokenType.ASN)
        >>> tk3 = Token('42', TokenType.NUM)
        >>> tk4 = Token('in', TokenType.INX)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('end', TokenType.END)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
        42

        >>> tk0 = Token('let', TokenType.LET)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('<-', TokenType.ASN)
        >>> tk3 = Token('21', TokenType.NUM)
        >>> tk4 = Token('in', TokenType.INX)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('+', TokenType.ADD)
        >>> tk7 = Token('v', TokenType.VAR)
        >>> tk8 = Token('end', TokenType.END)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7, tk8])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
        42

        >>> tk0 = Token('if', TokenType.IFX)
        >>> tk1 = Token('2', TokenType.NUM)
        >>> tk2 = Token('<', TokenType.LTH)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('then', TokenType.THN)
        >>> tk5 = Token('1', TokenType.NUM)
        >>> tk6 = Token('else', TokenType.ELS)
        >>> tk7 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        1

        >>> tk0 = Token('if', TokenType.IFX)
        >>> tk1 = Token('false', TokenType.FLS)
        >>> tk2 = Token('then', TokenType.THN)
        >>> tk3 = Token('1', TokenType.NUM)
        >>> tk4 = Token('else', TokenType.ELS)
        >>> tk5 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, None)
        2
        """
        expr = self.parse_if_then_else()
        if self.current_token.kind != TokenType.EOF:
            raise SyntaxError(f"Unexpected token {self.current_token.text}")
        return expr

    # Precedência 8: if-then-else (menor precedência)
    def parse_if_then_else(self):
        if self.current_token.kind == TokenType.IFX:
            self.advance()  # consume 'if'
            
            cond = self.parse_or()
            
            if self.current_token.kind != TokenType.THN:
                raise SyntaxError("Expected 'then' in if expression")
            self.advance()  # consume 'then'
            
            e0 = self.parse_if_then_else()
            
            if self.current_token.kind != TokenType.ELS:
                raise SyntaxError("Expected 'else' in if expression")
            self.advance()  # consume 'else'
            
            e1 = self.parse_if_then_else()
            
            return IfThenElse(cond, e0, e1)
        
        return self.parse_or()

    # Precedência 7: or
    def parse_or(self):
        left = self.parse_and()
        return self.parse_or_tail(left)
    
    def parse_or_tail(self, left):
        if self.current_token.kind == TokenType.ORX:
            self.advance()
            right = self.parse_and()
            left = Or(left, right)
            return self.parse_or_tail(left)
        return left

    # Precedência 6: and
    def parse_and(self):
        left = self.parse_equality()
        return self.parse_and_tail(left)
    
    def parse_and_tail(self, left):
        if self.current_token.kind == TokenType.AND:
            self.advance()
            right = self.parse_equality()
            left = And(left, right)
            return self.parse_and_tail(left)
        return left

    # Precedência 5: equality (==)
    def parse_equality(self):
        left = self.parse_comparison()
        return self.parse_equality_tail(left)
    
    def parse_equality_tail(self, left):
        if self.current_token.kind == TokenType.EQL:
            self.advance()
            right = self.parse_comparison()
            left = Eql(left, right)
            return self.parse_equality_tail(left)
        return left

    # Precedência 4: comparison (<, <=)
    def parse_comparison(self):
        left = self.parse_addition()
        return self.parse_comparison_tail(left)

    def parse_comparison_tail(self, left):
        if self.current_token.kind in [TokenType.LEQ, TokenType.LTH]:
            op = self.current_token
            self.advance()
            right = self.parse_addition()
            if op.kind == TokenType.LEQ:
                left = Leq(left, right)
            else:  # TokenType.LTH
                left = Lth(left, right)
            return self.parse_comparison_tail(left)
        return left

    # Precedência 3: addition (+, -)
    def parse_addition(self):
        left = self.parse_multiplication()
        return self.parse_addition_tail(left)
    
    def parse_addition_tail(self, left):
        if self.current_token.kind in [TokenType.ADD, TokenType.SUB]:
            op = self.current_token
            self.advance()
            right = self.parse_multiplication()
            if op.kind == TokenType.ADD:
                left = Add(left, right)
            else:  # TokenType.SUB
                left = Sub(left, right) 
            return self.parse_addition_tail(left)
        return left

    # Precedência 2: multiplication (*, /)
    def parse_multiplication(self):
        left = self.parse_unary()
        return self.parse_multiplication_tail(left)
    
    def parse_multiplication_tail(self, left):
        if self.current_token.kind in [TokenType.MUL, TokenType.DIV]:
            op = self.current_token
            self.advance()
            right = self.parse_unary()
            if op.kind == TokenType.MUL:
                left = Mul(left, right)
            else:  # TokenType.DIV
                left = Div(left, right)
            return self.parse_multiplication_tail(left)
        return left
    
    # Precedência 1: unary (not, ~)
    def parse_unary(self):
        if self.current_token.kind in [TokenType.NEG, TokenType.NOT]:
            op = self.current_token
            self.advance()
            operand = self.parse_unary()  
            if op.kind == TokenType.NEG:
                return Neg(operand)
            else:  # TokenType.NOT
                return Not(operand)
        return self.parse_primary()
    
    # primary := NUM | TRU | FLS | VAR | '(' expression ')' | let_expr
    def parse_primary(self):
        if self.current_token.kind == TokenType.NUM:
            num = Num(int(self.current_token.text))
            self.advance()
            return num
        elif self.current_token.kind == TokenType.TRU:
            tru = Bln(True)
            self.advance()
            return tru
        elif self.current_token.kind == TokenType.FLS:
            fls = Bln(False)
            self.advance()
            return fls
        elif self.current_token.kind == TokenType.LPR:
            self.advance()
            expr = self.parse_if_then_else()  # Permite qualquer expressão dentro de parênteses
            if self.current_token.kind != TokenType.RPR:
                raise SyntaxError("Expected ')'")
            self.advance()
            return expr
        elif self.current_token.kind == TokenType.LET:
            return self.parse_let()
        elif self.current_token.kind == TokenType.VAR:
            var = Var(self.current_token.text)
            self.advance()
            return var
        else:
            raise SyntaxError(f"Unexpected token {self.current_token.text}")
        
    def parse_let(self):
        # 'let' VAR '<-' expr 'in' expr 'end'
        self.advance()  # consume 'let'

        if self.current_token.kind != TokenType.VAR:
            raise SyntaxError("Expected variable after 'let'")
        var_name = self.current_token.text
        self.advance()

        if self.current_token.kind != TokenType.ASN:
            raise SyntaxError("Expected '<-' in let binding")
        self.advance()

        exp_def = self.parse_if_then_else()  # Permite qualquer expressão na definição

        if self.current_token.kind != TokenType.INX:
            raise SyntaxError("Expected 'in' in let binding")
        self.advance()

        exp_body = self.parse_if_then_else()  # Permite qualquer expressão no corpo

        if self.current_token.kind != TokenType.END:
            raise SyntaxError("Expected 'end' to close let expression")
        self.advance()

        return Let(var_name, exp_def, exp_body)