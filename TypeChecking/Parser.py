import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements the parser of arithmetic expressions.

References:
    see https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm
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

        expr = self.parse_if()  # <-- Use parse_if aqui!
        if self.current_token.kind != TokenType.EOF:
            sys.exit("Parse error")
        return expr
        
    # if_expr := 'if' expr 'then' expr 'else' expr | or_expr
    def parse_if(self):
        if self.current_token.kind == TokenType.IFX:
            self.advance()
            cond = self.parse_if()
            if self.current_token.kind != TokenType.THN:
                sys.exit("Parse error")
            self.advance()
            then_expr = self.parse_if()
            if self.current_token.kind != TokenType.ELS:
                sys.exit("Parse error")
            self.advance()
            else_expr = self.parse_if()
            return IfThenElse(cond, then_expr, else_expr)
        else:
            return self.parse_or()
        # or_expr := and_expr ('or' and_expr)*

    def parse_or(self):
        left = self.parse_and()
        while self.current_token.kind == TokenType.ORX:
            self.advance()
            right = self.parse_and()
            left = Or(left, right)
        return left
    
    # and_expr := eql_expr ('and' eql_expr)*
    def parse_and(self):
        left = self.parse_eql()
        while self.current_token.kind == TokenType.AND:
            self.advance()
            right = self.parse_eql()
            left = And(left, right)
        return left


    def parse_eql(self):
        left = self.parse_comparison()
        while self.current_token.kind == TokenType.EQL:
            self.advance()
            right = self.parse_comparison()
            left = Eql(left, right)
        return left

    # comparison := addition (('<=' | '<') addition)*
    def parse_comparison(self):
        left = self.parse_addition()
        while self.current_token.kind in [TokenType.LEQ, TokenType.LTH]:
            op = self.current_token
            self.advance()
            right = self.parse_addition()
            if op.kind == TokenType.LEQ:
                left = Leq(left, right)
            else:
                left = Lth(left, right)
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
            expr = self.parse_if()
            if self.current_token.kind != TokenType.RPR:
                sys.exit("Parse error")
            self.advance()
            return expr
        elif self.current_token.kind == TokenType.LET:
            return self.parse_let()
        elif self.current_token.kind == TokenType.VAR:
            var = Var(self.current_token.text)
            self.advance()
            return var
        else:
            sys.exit("Parse error")
        
    def parse_let(self):
        # 'let' VAR '<-' expr 'in' expr 'end'
        self.advance()  # consume 'let'

        if self.current_token.kind != TokenType.VAR:
            sys.exit("Parse error")
        var_name = self.current_token.text
        self.advance()

        if self.current_token.kind != TokenType.ASN:
            sys.exit("Parse error")
        self.advance()

        exp_def = self.parse_if()

        if self.current_token.kind != TokenType.INX:
            sys.exit("Parse error")
        self.advance()

        exp_body = self.parse_if()

        if self.current_token.kind != TokenType.END:
            sys.exit("Parse error")
        self.advance()

        return Let(var_name, exp_def, exp_body)
