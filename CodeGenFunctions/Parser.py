import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements a parser for SML with anonymous functions. The grammar is
as follows:

fn_exp  ::= fn <var> => fn_exp
          | if_exp
if_exp  ::= <if> if_exp <then> fn_exp <else> fn_exp
          | or_exp
or_exp  ::= and_exp (or and_exp)*
and_exp ::= eq_exp (and eq_exp)*
eq_exp  ::= cmp_exp (= cmp_exp)*
cmp_exp ::= add_exp ([<=|<] add_exp)*
add_exp ::= mul_exp ([+|-] mul_exp)*
mul_exp ::= unary_exp ([*|/] unary_exp)*
unary_exp ::= <not> unary_exp
             | ~ unary_exp
             | let_exp
let_exp ::= <let> <var> <- fn_exp <in> fn_exp <end>
          | val_exp
val_exp ::= val_tk (val_tk)*
val_tk ::= <var> | ( fn_exp ) | <num> | <true> | <false>

References:
    see https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm#classic
"""


class Parser:
    def __init__(self, tokens):
        """
        Initializes the parser. The parser keeps track of the list of tokens
        and the current token. For instance:
        """
        self.tokens = list(tokens)
        self.cur_token_idx = 0 # This is just a suggestion!

    def eat(self, token_type: TokenType) -> None: 
        if (self.tokens[self.cur_token_idx].kind == token_type):
            self.cur_token_idx += 1
        else:
            raise ValueError(f"Parse Error")

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

        >>> tk0 = Token('fn', TokenType.FNX)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token('=>', TokenType.ARW)
        >>> tk3 = Token('v', TokenType.VAR)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('1', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> print(exp.accept(ev, None))
        Fn(v)

        >>> tk0 = Token('(', TokenType.LPR)
        >>> tk1 = Token('fn', TokenType.FNX)
        >>> tk2 = Token('v', TokenType.VAR)
        >>> tk3 = Token('=>', TokenType.ARW)
        >>> tk4 = Token('v', TokenType.VAR)
        >>> tk5 = Token('+', TokenType.ADD)
        >>> tk6 = Token('1', TokenType.NUM)
        >>> tk7 = Token(')', TokenType.RPR)
        >>> tk8 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7, tk8])
        >>> exp = parser.parse()
        >>> ev = EvalVisitor()
        >>> exp.accept(ev, {})
        3
        """
        return self.parse_function_expression()
    

    def parse_function_expression(self):
        token = self.tokens[self.cur_token_idx]
        if token.kind == TokenType.FNX:
            self.eat(TokenType.FNX)
            if self.cur_token_idx >= len(self.tokens):
                sys.exit("Parse error")
            identifier_token = self.tokens[self.cur_token_idx]
            self.eat(TokenType.VAR)
            identifier_token = identifier_token.text
            self.eat(TokenType.ARW)
            body = self.parse_function_expression()
            return Fn(identifier_token, body)
        return self.parse_if_expression()

    def parse_if_expression(self):
        token = self.tokens[self.cur_token_idx]
        if token.kind == TokenType.IFX:
            self.eat(TokenType.IFX)
            cond = self.parse_if_expression()
            self.eat(TokenType.THN)
            e0 = self.parse_function_expression()
            self.eat(TokenType.ELS)
            e1 = self.parse_function_expression()
            return IfThenElse(cond, e0, e1)
        return self.parse_or_expression()

    def parse_or_expression(self):
        left = self.parse_and_expression()
        return self.parse_or_tail(left)

    def parse_or_tail(self, left):
        if self.cur_token_idx < len(self.tokens):
            token = self.tokens[self.cur_token_idx]
        else:
            return left
        if token.kind == TokenType.ORX:
            self.eat(TokenType.ORX)
            right = self.parse_and_expression()
            return self.parse_or_tail(Or(left, right))
        return left

    def parse_and_expression(self):
        left = self.parse_equality_expression()
        return self.parse_and_tail(left)

    def parse_and_tail(self, left):
        if self.cur_token_idx < len(self.tokens):
            token = self.tokens[self.cur_token_idx]
        else:
            return left
        if token.kind == TokenType.AND:
            self.eat(TokenType.AND)
            right = self.parse_equality_expression()
            return self.parse_and_tail(And(left, right))
        return left

    def parse_equality_expression(self):
        left = self.parse_comparison_expression()
        return self.parse_equality_tail(left)

    def parse_equality_tail(self, left):
        if self.cur_token_idx < len(self.tokens):
            token = self.tokens[self.cur_token_idx]
        else:
            return left
        if token.kind == TokenType.EQL:
            self.eat(TokenType.EQL)
            right = self.parse_comparison_expression()
            return self.parse_equality_tail(Eql(left=left, right=right))
        return left

    def parse_comparison_expression(self):
        left = self.parse_addition_expression()
        return self.parse_comparison_tail(left)

    def parse_comparison_tail(self, left):
        if self.cur_token_idx < len(self.tokens):
            token = self.tokens[self.cur_token_idx]
        else:
            return left
        if token.kind == TokenType.LEQ:
            self.eat(TokenType.LEQ)
            right = self.parse_addition_expression()
            return self.parse_comparison_tail(Leq(left, right))
        elif token.kind == TokenType.LTH:
            self.eat(TokenType.LTH)
            right = self.parse_addition_expression()
            return self.parse_comparison_tail(Lth(left, right))
        return left

    def parse_addition_expression(self):
        left = self.parse_term_expression()
        return self.parse_addition_tail(left)

    def parse_addition_tail(self, left):
        if self.cur_token_idx < len(self.tokens):
            token = self.tokens[self.cur_token_idx]
        else:
            return left
        if token.kind == TokenType.ADD:
            self.eat(TokenType.ADD)
            right = self.parse_term_expression()
            return self.parse_addition_tail(Add(left, right))
        elif token.kind == TokenType.SUB:
            self.eat(TokenType.SUB)
            right = self.parse_term_expression()
            return self.parse_addition_tail(Sub(left, right))
        return left

    def parse_term_expression(self):
        left = self.parse_unary_expression()
        return self.parse_term_tail(left)

    def parse_term_tail(self, left):
        if self.cur_token_idx < len(self.tokens):
            token = self.tokens[self.cur_token_idx]
        else:
            return left
        if token.kind == TokenType.MUL:
            self.eat(TokenType.MUL)
            right = self.parse_unary_expression()
            return self.parse_term_tail(Mul(left, right))
        elif token.kind == TokenType.DIV:
            self.eat(TokenType.DIV)
            right = self.parse_unary_expression()
            return self.parse_term_tail(Div(left, right))
        return left

    def parse_unary_expression(self):
        token = self.tokens[self.cur_token_idx]
        if token.kind == TokenType.NEG:
            self.eat(TokenType.NEG)
            exp = self.parse_unary_expression()
            return Neg(exp)
        elif token.kind == TokenType.NOT:
            self.eat(TokenType.NOT)
            exp = self.parse_unary_expression()
            return Not(exp)
        return self.parse_let_expression()

    def parse_let_expression(self):
        token = self.tokens[self.cur_token_idx]
        if token.kind == TokenType.LET:
            self.eat(TokenType.LET)
            identifier_token = self.tokens[self.cur_token_idx]
            self.eat(TokenType.VAR)
            identifier_token = identifier_token.text
            self.eat(TokenType.ASN)
            exp_def = self.parse_function_expression()
            self.eat(TokenType.INX)
            exp_body = self.parse_function_expression()
            self.eat(TokenType.END)
            return Let(identifier_token, exp_def, exp_body)
        return self.parse_application_expression()

    def parse_application_expression(self):
        left = self.parse_factor()
        return self.parse_application_tail(left)

    def parse_application_tail(self, left):
        if self.cur_token_idx < len(self.tokens):
            token = self.tokens[self.cur_token_idx]
        else:
            return left
        if token.kind in {TokenType.NUM, TokenType.TRU, TokenType.FLS, TokenType.VAR, TokenType.LPR}:
            right = self.parse_factor()
            return self.parse_application_tail(App(left, right))
        return left

    def parse_factor(self):
        token = self.tokens[self.cur_token_idx]
        if token.kind == TokenType.NUM:
            self.eat(TokenType.NUM)
            return Num(int(token.text))
        elif token.kind == TokenType.TRU:
            self.eat(TokenType.TRU)
            return Bln(True)
        elif token.kind == TokenType.FLS:
            self.eat(TokenType.FLS)
            return Bln(False)
        elif token.kind == TokenType.VAR:
            self.eat(TokenType.VAR)
            return Var(token.text)
        elif token.kind == TokenType.LPR:
            self.eat(TokenType.LPR)
            exp = self.parse_function_expression()
            self.eat(TokenType.RPR)
            return exp
        else:
            sys.exit("Parse error")