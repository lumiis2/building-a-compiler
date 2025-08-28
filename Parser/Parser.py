import sys

from Expression import *
from Lexer import Token, TokenType, Lexer

"""
This file implements the parser of arithmetic expressions.

References:
    see https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
"""

class Parser:

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos] if self.tokens else None

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = Token("", TokenType.EOF)


    def parse(self):
        """
        Returns the expression associated with the stream of tokens.

        Examples:
        >>> parser = Parser([Token('123', TokenType.INT)])
        >>> exp = parser.parse()
        >>> exp.eval()
        123

        >>> parser = Parser([Token('True', TokenType.TRU)])
        >>> exp = parser.parse()
        >>> exp.eval()
        True

        >>> parser = Parser([Token('False', TokenType.FLS)])
        >>> exp = parser.parse()
        >>> exp.eval()
        False

        >>> tk0 = Token('~', TokenType.NEG)
        >>> tk1 = Token('123', TokenType.INT)
        >>> parser = Parser([tk0, tk1])
        >>> exp = parser.parse()
        >>> exp.eval()
        -123

        >>> tk0 = Token('3', TokenType.INT)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('4', TokenType.INT)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        12

        >>> tk0 = Token('3', TokenType.INT)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('~', TokenType.NEG)
        >>> tk3 = Token('4', TokenType.INT)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> exp = parser.parse()
        >>> exp.eval()
        -12

        >>> tk0 = Token('30', TokenType.INT)
        >>> tk1 = Token('/', TokenType.DIV)
        >>> tk2 = Token('4', TokenType.INT)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        7

        >>> tk0 = Token('3', TokenType.INT)
        >>> tk1 = Token('+', TokenType.ADD)
        >>> tk2 = Token('4', TokenType.INT)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        7

        >>> tk0 = Token('30', TokenType.INT)
        >>> tk1 = Token('-', TokenType.SUB)
        >>> tk2 = Token('4', TokenType.INT)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        26

        >>> tk0 = Token('2', TokenType.INT)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('(', TokenType.LPR)
        >>> tk3 = Token('3', TokenType.INT)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('4', TokenType.INT)
        >>> tk6 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> exp = parser.parse()
        >>> exp.eval()
        14

        >>> tk0 = Token('4', TokenType.INT)
        >>> tk1 = Token('==', TokenType.EQL)
        >>> tk2 = Token('4', TokenType.INT)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        True

        >>> tk0 = Token('4', TokenType.INT)
        >>> tk1 = Token('<=', TokenType.LEQ)
        >>> tk2 = Token('4', TokenType.INT)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        True

        >>> tk0 = Token('4', TokenType.INT)
        >>> tk1 = Token('<', TokenType.LTH)
        >>> tk2 = Token('4', TokenType.INT)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> exp.eval()
        False

        >>> tk0 = Token('not', TokenType.NOT)
        >>> tk1 = Token('4', TokenType.INT)
        >>> tk2 = Token('<', TokenType.LTH)
        >>> tk3 = Token('4', TokenType.INT)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> exp = parser.parse()
        >>> exp.eval()
        True
        """

        expr = self.parse_comparison()
        if self.current_token.kind != TokenType.EOF:
            raise SyntaxError(f"Unexpected token {self.current_token.text}")
        return expr
        

    # comparison := addition comparison_tail
    def parse_comparison(self):
        left = self.parse_addition()
        return self.parse_comparison_tail(left)

    def parse_comparison_tail(self, left):
        if self.current_token.kind in [TokenType.LEQ, TokenType.LTH, TokenType.EQL]:
            op = self.current_token
            self.advance()
            right = self.parse_addition()
            if op.kind == TokenType.LEQ:
                left = Leq(left, right)
            elif op.kind == TokenType.LTH:
                left = Lth(left, right)
            else: # TokenType.EQL
                left = Eql(left, right)
            return self.parse_comparison_tail(left)
        return left  

    # addition := multiplication addition_tail
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

    # multiplication := unary multiplication_tail
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
    
    # unary := ( '-' | 'not') unary | primary
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
    
    # primary := INT | TRU | FLS | '(' expression ')'
    def parse_primary(self):
        if self.current_token.kind == TokenType.INT:
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
            expr = self.parse_comparison()
            if self.current_token.kind != TokenType.RPR:
                raise SyntaxError("Expected ')'")
            self.advance()
            return expr
        else:
            raise SyntaxError(f"Unexpected token {self.current_token.text}")
    