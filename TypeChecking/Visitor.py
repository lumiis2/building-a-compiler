import sys
from abc import ABC, abstractmethod
from Expression import *

class Visitor(ABC):
    """
    The visitor pattern consists of two abstract classes: the Expression and the
    Visitor. The Expression class defines on method: 'accept(visitor, args)'.
    This method takes in an implementation of a visitor, and the arguments that
    are passed from expression to expression. The Visitor class defines one
    specific method for each subclass of Expression. Each instance of such a
    subclasse will invoke the right visiting method.
    """
    @abstractmethod
    def visit_var(self, exp, arg):
        pass

    @abstractmethod
    def visit_bln(self, exp, arg):
        pass

    @abstractmethod
    def visit_num(self, exp, arg):
        pass

    @abstractmethod
    def visit_eql(self, exp, arg):
        pass

    @abstractmethod
    def visit_add(self, exp, arg):
        pass

    @abstractmethod
    def visit_sub(self, exp, arg):
        pass

    @abstractmethod
    def visit_mul(self, exp, arg):
        pass

    @abstractmethod
    def visit_div(self, exp, arg):
        pass

    @abstractmethod
    def visit_leq(self, exp, arg):
        pass

    @abstractmethod
    def visit_lth(self, exp, arg):
        pass

    @abstractmethod
    def visit_neg(self, exp, arg):
        pass

    @abstractmethod
    def visit_not(self, exp, arg):
        pass

    @abstractmethod
    def visit_let(self, exp, arg):
        pass

    @abstractmethod
    def visit_or(self, exp, arg):
        pass

    @abstractmethod
    def visit_and(self, exp, arg):
        pass

    @abstractmethod
    def visit_ifThenElse(self, exp, arg):
        pass

class EvalVisitor(Visitor):
    """
    The EvalVisitor class evaluates logical and arithmetic expressions. The
    result of evaluating an expression is the value of that expression. The
    inherited attribute propagated throughout visits is the environment that
    associates the names of variables with values.

    Examples:
    >>> e0 = Let('v', Add(Num(40), Num(2)), Mul(Var('v'), Var('v')))
    >>> e1 = Not(Eql(e0, Num(1764)))
    >>> ev = EvalVisitor()
    >>> e1.accept(ev, {})
    False

    >>> e0 = Let('v', Add(Num(40), Num(2)), Sub(Var('v'), Num(2)))
    >>> e1 = Lth(e0, Var('x'))
    >>> ev = EvalVisitor()
    >>> e1.accept(ev, {'x': 41})
    True
    """
    def visit_var(self, exp, env):
        if exp.identifier not in env:
            sys.exit("Def error")
        return env[exp.identifier]

    def visit_bln(self, exp, env):
        val = exp.bln
        if type(val) is not bool:
            sys.exit("Type error")
        return val

    def visit_num(self, exp, env):
        val = exp.num
        if type(val) is not int:
            sys.exit("Type error")
        return val

    def visit_eql(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        if type(left) != type(right):
            sys.exit("Type error")
        return left == right

    def visit_add(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        if type(left) is not int or type(right) is not int:
            sys.exit("Type error")
        return left + right   

    def visit_sub(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        if type(left) is not int or type(right) is not int:
            sys.exit("Type error")
        return left - right

    def visit_mul(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        if type(left) is not int or type(right) is not int:
            sys.exit("Type error")
        return left * right

    def visit_div(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        if type(left) is not int or type(right) is not int:
            sys.exit("Type error")
        return left // right

    def visit_leq(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        if type(left) is not int or type(right) is not int:
            sys.exit("Type error")
        return left <= right

    def visit_lth(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        if type(left) is not int or type(right) is not int:
            sys.exit("Type error")
        return left < right

    def visit_or(self, exp, env):
        left_val = exp.left.accept(self, env)
        if left_val:
            return True
        return exp.right.accept(self, env)

    def visit_and(self, exp, env):
        left_val = exp.left.accept(self, env)
        if not left_val:
            return False
        return exp.right.accept(self, env)

    def visit_not(self, exp, env):
        val = exp.exp.accept(self, env)
        if type(val) is not bool:
            sys.exit("Type error")
        return not val

    def visit_neg(self, exp, env):
        val = exp.exp.accept(self, env)
        if type(val) is not int:
            sys.exit("Type error")
        return -val

    
    def visit_ifThenElse(self, exp, env):
        cond_val = exp.cond.accept(self, env)
        if cond_val:
            return exp.e0.accept(self, env)
        else:
            return exp.e1.accept(self, env)

    def visit_let(self, exp, env):
        new_env = dict(env) if env is not None else {}
        new_env[exp.identifier] = exp.exp_def.accept(self, env)
        return exp.exp_body.accept(self, new_env)

class UseDefVisitor(Visitor):
    """
    The EvalVisitor class evaluates logical and arithmetic expressions. The
    result of evaluating an expression is the value of that expression. The
    inherited attribute propagated throughout visits is the environment that
    associates the names of variables with values.
    
    Notice that this implementation must perform type verification. If some
    verification fail, then it invokes sys.exit with the correct error
    message. We expect two different messages:
    
    1. sys.exit("Type error")
    2. sys.exit("Def error")

    Examples:
    >>> e0 = Let('v', Add(Num(40), Num(2)), Mul(Var('v'), Var('v')))
    >>> e1 = Not(Eql(e0, Num(1764)))
    >>> ev = EvalVisitor()
    >>> e1.accept(ev, {})
    False

    >>> e0 = Let('v', Add(Num(40), Num(2)), Sub(Var('v'), Num(2)))
    >>> e1 = Lth(e0, Var('x'))
    >>> ev = EvalVisitor()
    >>> e1.accept(ev, {'x': 41})
    True
    """
    def visit_var(self, exp, defined):
        if exp.identifier in defined:
            return set()
        else:
            return {exp.identifier}

    def visit_bln(self, exp, defined):
        return set()

    def visit_num(self, exp, defined):
        return set()

    def visit_eql(self, exp, defined):
        return exp.left.accept(self, defined) | exp.right.accept(self, defined)

    def visit_add(self, exp, defined):
        return exp.left.accept(self, defined) | exp.right.accept(self, defined)     

    def visit_sub(self, exp, defined):
        return exp.left.accept(self, defined) | exp.right.accept(self, defined)

    def visit_mul(self, exp, defined):
        return exp.left.accept(self, defined) | exp.right.accept(self, defined)

    def visit_div(self, exp, defined):
        return exp.left.accept(self, defined) | exp.right.accept(self, defined)

    def visit_leq(self, exp, defined):
        return exp.left.accept(self, defined) | exp.right.accept(self, defined)

    def visit_lth(self, exp, defined):
        return exp.left.accept(self, defined) | exp.right.accept(self, defined)

    def visit_neg(self, exp, defined):
        return exp.exp.accept(self, defined)
        
    def visit_not(self, exp, defined):
        return exp.exp.accept(self, defined)
    
    def visit_and(self, exp, defined):
        return exp.left.accept(self, defined) | exp.right.accept(self, defined)

    def visit_or(self, exp, defined):
        return exp.left.accept(self, defined) | exp.right.accept(self, defined)

    def visit_ifThenElse(self, exp, defined):
        return (exp.cond.accept(self, defined) |
                exp.e0.accept(self, defined) |
                exp.e1.accept(self, defined))

    def visit_let(self, exp, defined):
        used_in_value = exp.exp_def.accept(self, defined)
        new_defined = defined | {exp.identifier}
        used_in_body = exp.exp_body.accept(self, new_defined)
        return used_in_value | used_in_body

def safe_eval(exp):
    """
    This method applies one simple semantic analysis onto an expression, before
    evaluating it: it checks if the expression contains free variables, there
    is, variables used without being defined.

    Example:
    >>> e0 = Let('v', Add(Num(40), Num(2)), Mul(Var('v'), Var('v')))
    >>> e1 = Not(Eql(e0, Num(1764)))
    >>> safe_eval(e1)
    Value is False

    >>> e0 = Let('v', Add(Num(40), Num(2)), Sub(Var('v'), Num(2)))
    >>> e1 = Lth(e0, Var('x'))
    >>> safe_eval(e1)
    Error: expression contains undefined variables.
    """
    use_def_visitor = UseDefVisitor()
    undefined_vars = exp.accept(use_def_visitor, set())
    if undefined_vars:
        print("Error: expression contains undefined variables.")
    else:
        eval_visitor = EvalVisitor()
        value = exp.accept(eval_visitor, {})
        print("Value is", value)


class TypeVisitor(Visitor):
    """
    Visitor para checagem de tipos. Retorna o tipo da expressão (int ou bool).
    Em caso de erro de tipo, encerra o programa com 'Type error'.
    """

    def visit_var(self, exp, env):
        if exp.identifier not in env:
            sys.exit("Def error")
        return env[exp.identifier]

    def visit_bln(self, exp, env):
        return bool

    def visit_num(self, exp, env):
        return int

    def visit_eql(self, exp, env):
        t1 = exp.left.accept(self, env)
        t2 = exp.right.accept(self, env)
        if t1 != t2:
            sys.exit("Type error")
        return bool

    def visit_add(self, exp, env):
        t1 = exp.left.accept(self, env)
        t2 = exp.right.accept(self, env)
        if t1 != int or t2 != int:
            sys.exit("Type error")
        return int

    def visit_sub(self, exp, env):
        t1 = exp.left.accept(self, env)
        t2 = exp.right.accept(self, env)
        if t1 != int or t2 != int:
            sys.exit("Type error")
        return int

    def visit_mul(self, exp, env):
        t1 = exp.left.accept(self, env)
        t2 = exp.right.accept(self, env)
        if t1 != int or t2 != int:
            sys.exit("Type error")
        return int

    def visit_div(self, exp, env):
        t1 = exp.left.accept(self, env)
        t2 = exp.right.accept(self, env)
        if t1 != int or t2 != int:
            sys.exit("Type error")
        return int

    def visit_leq(self, exp, env):
        t1 = exp.left.accept(self, env)
        t2 = exp.right.accept(self, env)
        if t1 != int or t2 != int:
            sys.exit("Type error")
        return bool

    def visit_lth(self, exp, env):
        t1 = exp.left.accept(self, env)
        t2 = exp.right.accept(self, env)
        if t1 != int or t2 != int:
            sys.exit("Type error")
        return bool

    def visit_neg(self, exp, env):
        t = exp.exp.accept(self, env)
        if t != int:
            sys.exit("Type error")
        return int

    def visit_not(self, exp, env):
        t = exp.exp.accept(self, env)
        if t != bool:
            sys.exit("Type error")
        return bool

    def visit_or(self, exp, env):
        t1 = exp.left.accept(self, env)
        t2 = exp.right.accept(self, env)
        if t1 != bool or t2 != bool:
            sys.exit("Type error")
        return bool

    def visit_and(self, exp, env):
        t1 = exp.left.accept(self, env)
        t2 = exp.right.accept(self, env)
        if t1 != bool or t2 != bool:
            sys.exit("Type error")
        return bool

    def visit_ifThenElse(self, exp, env):
        t_cond = exp.cond.accept(self, env)
        t_then = exp.e0.accept(self, env)
        t_else = exp.e1.accept(self, env)
        if t_cond != bool or t_then != t_else:
            sys.exit("Type error")
        return t_then

    def visit_let(self, exp, env):
        t_def = exp.exp_def.accept(self, env)
        new_env = dict(env)
        new_env[exp.identifier] = t_def
        return exp.exp_body.accept(self, new_env)