import sys

from Expression import *
from Lexer import Token, TokenType

"""
This file implements a parser for SML with anonymous functions and type
annotations. The grammar is as follows:

fn_exp  ::= fn <var>: types => fn_exp
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
let_exp ::= <let> <var>: types <- fn_exp <in> fn_exp <end>
          | val_exp
val_exp ::= val_tk (val_tk)*
val_tk ::= <var> | ( fn_exp ) | <num> | <true> | <false>

types ::= type -> types | type

type ::= int | bool | ( types )

References:
    see https://www.engr.mun.ca/~theo/Misc/exp_parsing.htm#classic
"""

class Parser:
    def advance(self):
        self.cur_token_idx += 1
        if self.cur_token_idx < len(self.tokens):
            self.current_token = self.tokens[self.cur_token_idx]
        else:
            self.current_token = Token("", TokenType.EOF)

    def match_and_consume(self, kind):
        if self.current_token.kind == kind:
            self.advance()
            return True
        return False

    def type(self):
        if self.current_token.kind == TokenType.INT:
            self.advance()
            return type(1)
        elif self.current_token.kind == TokenType.LGC:
            self.advance()
            return type(True)
        elif self.current_token.kind == TokenType.LPR:
            self.advance()
            tp = self.types()
            if self.current_token.kind != TokenType.RPR:
                sys.exit("Parse error")
            self.advance()
            return tp
        else:
            sys.exit("Parse error: expected type annotation")

    def types(self):
        tp = self.type()
        if self.match_and_consume(TokenType.TPF):
            tp = ArrowType(tp, self.types())
        return tp
    def __init__(self, tokens):
        """
        Initializes the parser. The parser keeps track of the list of tokens
        and the current token.
        """
        self.tokens = list(tokens)
        self.cur_token_idx = 0
        if self.tokens:
            self.current_token = self.tokens[0]
        else:
            self.current_token = Token("", TokenType.EOF)

    def parse(self):
        """
        Returns the expression associated with the stream of tokens.

        Examples:
        >>> parser = Parser([Token('123', TokenType.NUM)])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> parser = Parser([Token('True', TokenType.TRU)])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> parser = Parser([Token('False', TokenType.FLS)])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('~', TokenType.NEG)
        >>> tk1 = Token('123', TokenType.NUM)
        >>> parser = Parser([tk0, tk1])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('~', TokenType.NEG)
        >>> tk3 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('/', TokenType.DIV)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('3', TokenType.NUM)
        >>> tk1 = Token('+', TokenType.ADD)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('30', TokenType.NUM)
        >>> tk1 = Token('-', TokenType.SUB)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('2', TokenType.NUM)
        >>> tk1 = Token('*', TokenType.MUL)
        >>> tk2 = Token('(', TokenType.LPR)
        >>> tk3 = Token('3', TokenType.NUM)
        >>> tk4 = Token('+', TokenType.ADD)
        >>> tk5 = Token('4', TokenType.NUM)
        >>> tk6 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('==', TokenType.EQL)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<=', TokenType.LEQ)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('4', TokenType.NUM)
        >>> tk1 = Token('<', TokenType.LTH)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('not', TokenType.NOT)
        >>> tk1 = Token('(', TokenType.LPR)
        >>> tk2 = Token('4', TokenType.NUM)
        >>> tk3 = Token('<', TokenType.LTH)
        >>> tk4 = Token('4', TokenType.NUM)
        >>> tk5 = Token(')', TokenType.RPR)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('or', TokenType.ORX)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> tk0 = Token('true', TokenType.TRU)
        >>> tk1 = Token('and', TokenType.AND)
        >>> tk2 = Token('false', TokenType.FLS)
        >>> parser = Parser([tk0, tk1, tk2])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'bool'>

        >>> t0 = Token('let', TokenType.LET)
        >>> t1 = Token('v', TokenType.VAR)
        >>> t2 = Token(':', TokenType.COL)
        >>> t3 = Token('int', TokenType.INT)
        >>> t4 = Token('<-', TokenType.ASN)
        >>> t5 = Token('42', TokenType.NUM)
        >>> t6 = Token('in', TokenType.INX)
        >>> t7 = Token('v', TokenType.VAR)
        >>> t8 = Token('end', TokenType.END)
        >>> parser = Parser([t0, t1, t2, t3, t4, t5, t6, t7, t8])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, {})
        <class 'int'>

        >>> t0 = Token('let', TokenType.LET)
        >>> t1 = Token('v', TokenType.VAR)
        >>> t2 = Token(':', TokenType.COL)
        >>> t3 = Token('int', TokenType.INT)
        >>> t4 = Token('<-', TokenType.ASN)
        >>> t5 = Token('21', TokenType.NUM)
        >>> t6 = Token('in', TokenType.INX)
        >>> t7 = Token('v', TokenType.VAR)
        >>> t8 = Token('+', TokenType.ADD)
        >>> t9 = Token('v', TokenType.VAR)
        >>> tA = Token('end', TokenType.END)
        >>> parser = Parser([t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, tA])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, {})
        <class 'int'>

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
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('if', TokenType.IFX)
        >>> tk1 = Token('false', TokenType.FLS)
        >>> tk2 = Token('then', TokenType.THN)
        >>> tk3 = Token('1', TokenType.NUM)
        >>> tk4 = Token('else', TokenType.ELS)
        >>> tk5 = Token('2', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, None)
        <class 'int'>

        >>> tk0 = Token('fn', TokenType.FNX)
        >>> tk1 = Token('v', TokenType.VAR)
        >>> tk2 = Token(':', TokenType.COL)
        >>> tk3 = Token('int', TokenType.INT)
        >>> tk4 = Token('=>', TokenType.ARW)
        >>> tk5 = Token('v', TokenType.VAR)
        >>> tk6 = Token('+', TokenType.ADD)
        >>> tk7 = Token('1', TokenType.NUM)
        >>> parser = Parser([tk0, tk1, tk2, tk3, tk4, tk5, tk6, tk7])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> print(exp.accept(ev, {}))
        <class 'int'> -> <class 'int'>

        >>> t0 = Token('(', TokenType.LPR)
        >>> t1 = Token('fn', TokenType.FNX)
        >>> t2 = Token('v', TokenType.VAR)
        >>> t3 = Token(':', TokenType.COL)
        >>> t4 = Token('int', TokenType.INT)
        >>> t5 = Token('=>', TokenType.ARW)
        >>> t6 = Token('v', TokenType.VAR)
        >>> t7 = Token('+', TokenType.ADD)
        >>> t8 = Token('1', TokenType.NUM)
        >>> t9 = Token(')', TokenType.RPR)
        >>> tA = Token('2', TokenType.NUM)
        >>> parser = Parser([t0, t1, t2, t3, t4, t5, t6, t7, t8, t9, tA])
        >>> exp = parser.parse()
        >>> ev = TypeCheckVisitor()
        >>> exp.accept(ev, {})
        <class 'int'>
        """
        expr = self.parse_fn()  
        if self.current_token.kind != TokenType.EOF:
            sys.exit("Parse error")
        return expr
        
    # fn_exp  ::= fn <var> => fn_exp | if_exp
    def parse_fn(self):
        if self.current_token.kind == TokenType.FNX:
            self.advance()  # consume 'fn'
            if self.current_token.kind != TokenType.VAR:
                sys.exit("Parse error")
            formal = self.current_token.text
            self.advance()
            if self.current_token.kind != TokenType.COL:
                sys.exit("Parse error: expected ':' after parameter name")
            self.advance()
            tp_var = self.types()
            if self.current_token.kind != TokenType.ARW:
                sys.exit("Parse error: expected '=>' after type annotation")
            self.advance()  # consume '=>'
            body = self.parse_fn()
            return Fn(formal, tp_var, body)
        else:
            return self.parse_if()
        
    # if_expr := 'if' if_expr 'then' fn_expr 'else' fn_expr | or_expr
    def parse_if(self):
        if self.current_token.kind == TokenType.IFX:
            self.advance()
            cond = self.parse_if()
            if self.current_token.kind != TokenType.THN:
                sys.exit("Parse error")
            self.advance()
            then_expr = self.parse_fn()
            if self.current_token.kind != TokenType.ELS:
                sys.exit("Parse error")
            self.advance()
            else_expr = self.parse_fn()
            return IfThenElse(cond, then_expr, else_expr)
        else:
            return self.parse_or()

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
    
    # unary := ( '-' | 'not') unary | app_expr
    def parse_unary(self):
        if self.current_token.kind in [TokenType.NEG, TokenType.NOT]:
            op = self.current_token
            self.advance()
            operand = self.parse_unary()  
            if op.kind == TokenType.NEG:
                return Neg(operand)
            else:  # TokenType.NOT
                return Not(operand)
        return self.parse_application()
    
    # app_expr := primary (primary)*
    def parse_application(self):
        left = self.parse_primary()
        while self.current_token.kind in [TokenType.NUM, TokenType.TRU, TokenType.FLS, 
                                         TokenType.VAR, TokenType.LPR]:
            right = self.parse_primary()
            left = App(left, right)
        return left
    
    # primary := INT | TRU | FLS | '(' fn_expr ')' | let_expr | VAR
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
            expr = self.parse_fn()
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
        # 'let' VAR : types <- fn_expr in fn_expr end
        self.advance()  # consume 'let'
        if self.current_token.kind != TokenType.VAR:
            sys.exit("Parse error")
        var_name = self.current_token.text
        self.advance()
        if self.current_token.kind != TokenType.COL:
            sys.exit("Parse error: expected ':' after let variable name")
        self.advance()
        tp_var = self.types()
        if self.current_token.kind != TokenType.ASN:
            sys.exit("Parse error: expected '<-' after type annotation in let")
        self.advance()
        exp_def = self.parse_fn()
        if self.current_token.kind != TokenType.INX:
            sys.exit("Parse error: expected 'in' in let expression")
        self.advance()
        exp_body = self.parse_fn()
        if self.current_token.kind != TokenType.END:
            sys.exit("Parse error: expected 'end' in let expression")
        self.advance()
        return Let(var_name, tp_var, exp_def, exp_body)
