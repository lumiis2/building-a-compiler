import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements the parser of arithmetic expressions. The same rules of
precedence and associativity from Lab 5: Visitors, apply.
 
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
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        123

        >>> parser = Parser([Token('True', TokenType.TRU)])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> parser = Parser([Token('False', TokenType.FLS)])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> tk0 = Token('~', TokenType.NEG)
        >>> tk1 = Token('123', TokenType.NUM)
        >>> parser = Parser([tk0, tk1])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        -123

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        12

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('~', TokenType.NEG)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        -12

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('/', TokenType.DIV)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        7

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('+', TokenType.ADD)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        7

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('-', TokenType.SUB)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        26

        >>> tk0 = Token('2', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('(', TokenType.LPR)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('4', TokenType.NUM)
        >>> tk6 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        14

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('==', TokenType.EQL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<=', TokenType.LEQ)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<', TokenType.LTH)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> tk0 = Token('not', TokenType.NOT)
        >>> tk1 = Token('4', TokenType.NUM)
        >>> tk2 = Token('<', TokenType.LTH)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> tk0 = Token('let', TokenType.LET)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('<-', TokenType.ASN)
        >>> tk3 = Token('42', TokenType.NUM)
        >>> tk4 = Token('in', TokenType.INX)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('end', TokenType.END)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
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
        >>> g = GenVisitor()
        >>> p = AsmModule.Program({}, [])
        >>> exp = parser.parse()
        >>> v = exp.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        42
        """

        expr = self.parse_comparison()
        if self.current_token.kind != TokenType.EOF:
            raise SyntaxError(f"Unexpected token {self.current_token.text}")
        return expr
        

    # comparison := addition comparison_tail
    def parse_comparison(self):
        # primeiro, trata o 'not'
        if self.current_token.kind == TokenType.NOT:
            self.advance()
            expr = self.parse_comparison()  # aplica not sobre a comparação inteira
            return Not(expr)
        
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
    
    # primary := INT | TRU | FLS | '(' expression ')' | let_expr
    def parse_primary(self):
        if self.current_token.kind == TokenType.NUM: # agora ta usando NUM
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

        exp_def = self.parse_comparison()

        if self.current_token.kind != TokenType.INX:
            raise SyntaxError("Expected 'in' in let binding")
        self.advance()

        exp_body = self.parse_comparison()

        if self.current_token.kind != TokenType.END:
            raise SyntaxError("Expected 'end' to close let expression")
        self.advance()

        return Let(var_name, exp_def, exp_body)
