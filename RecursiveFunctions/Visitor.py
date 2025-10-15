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
    def visit_and(self, exp, arg):
        pass

    @abstractmethod
    def visit_or(self, exp, arg):
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
    def visit_mod(self, exp, arg):
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
    def visit_ifThenElse(self, exp, arg):
        pass

    @abstractmethod
    def visit_fn(self, exp, arg):
        pass

    @abstractmethod
    def visit_fun(self, exp, arg):
        pass

    @abstractmethod
    def visit_app(self, exp, arg):
        pass


class Function:
    """
    This is the class that represents functions. This class lets us distinguish
    the three types that now exist in the language: numbers, booleans and
    functions. Notice that the evaluation of an expression can now be a
    function. For instance:

        >>> f = Fn('v', Mul(Var('v'), Var('v')))
        >>> ev = EvalVisitor()
        >>> fval = f.accept(ev, {})
        >>> type(fval)
        <class 'Visitor.Function'>
    """

    def __init__(self, formal, body, env):
        self.formal = formal
        self.body = body
        self.env = env

    def __str__(self):
        return f"Fn({self.formal})"


class RecFunction(Function):
    """
    This is the class that represents named functions. The key different between
    named and anonymous functions is exactly the "name" :)

        >>> f = Fun('f', 'v', Mul(Var('v'), Var('v')))
        >>> ev = EvalVisitor()
        >>> fval = f.accept(ev, {})
        >>> type(fval)
        <class 'Visitor.RecFunction'>
    """

    def __init__(self, name, formal, body, env):
        super().__init__(formal, body, env)
        self.name = name

    def __str__(self):
        return f"Fun {self.name}({self.formal})"


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

    >>> e0 = Fn('v', Mul(Var('v'), Var('v')))
    >>> ev = EvalVisitor()
    >>> print(e0.accept(ev, {}))
    Fn(v)

    >>> e0 = Fn('v', Mul(Var('v'), Var('v')))
    >>> e1 = Add(Num(3), Num(4))
    >>> e2 = App(e0, e1)
    >>> ev = EvalVisitor()
    >>> print(e2.accept(ev, {}))
    49

    >>> e0 = Fun('f', 'v', Mul(Var('v'), Var('v')))
    >>> ev = EvalVisitor()
    >>> print(e0.accept(ev, {}))
    Fun f(v)

    >>> e0 = Fun('f', 'v', Mul(Var('v'), Var('v')))
    >>> e1 = Add(Num(3), Num(4))
    >>> e2 = App(e0, e1)
    >>> ev = EvalVisitor()
    >>> print(e2.accept(ev, {}))
    49
    """

    def visit_var(self, exp, env):
        if exp.identifier in env:
            return env[exp.identifier]
        else:
            sys.exit("Def error")

    def visit_bln(self, exp, env):
        return exp.bln

    def visit_num(self, exp, env):
        return exp.num

    def visit_eql(self, exp, env):
        val_left = exp.left.accept(self, env)
        val_right = exp.right.accept(self, env)
        if type(val_left) == type(val_right):
            return val_left == val_right
        else:
            sys.exit("Type error")

    def visit_and(self, exp, env):
        left_val = exp.left.accept(self, env)
        if not left_val:
            return False
        return exp.right.accept(self, env)

    def visit_or(self, exp, env):
        left_val = exp.left.accept(self, env)
        if left_val:
            return True
        return exp.right.accept(self, env)

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

    def visit_mod(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        if type(left) is not int or type(right) is not int:
            sys.exit("Type error")
        return left % right

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

    def visit_neg(self, exp, env):
        val = exp.exp.accept(self, env)
        if type(val) is not int:
            sys.exit("Type error")
        return -val

    def visit_not(self, exp, env):
        val = exp.exp.accept(self, env)
        if type(val) is not bool:
            sys.exit("Type error")
        return not val
    
    def visit_let(self, exp, env):
        new_env = dict(env) if env is not None else {}
        new_env[exp.identifier] = exp.exp_def.accept(self, env)
        return exp.exp_body.accept(self, new_env)

    def visit_ifThenElse(self, exp, env):
        cond = exp.cond.accept(self, env)
        if type(cond) is not bool:
            sys.exit("Type error")
        if cond:
            return exp.e0.accept(self, env)
        else:
            return exp.e1.accept(self, env)
        
    def visit_fn(self, exp, env):
        """
        The evaluation of a function is the function itself. Remember: in our
        language, functions are values as well. So, now we have four kinds of
        values: numbers, booleans, anonymous functions and named functions.
        """
        return Function(exp.formal, exp.body, env)

    def visit_fun(self, exp, env):
        """
        The evaluation of a named function returns a value that is the function
        itself. However, we use a different type of value: RecFunction. In this
        way, we have access to the name of the named function (and that's why
        they are called named functions :).
        """
        return RecFunction(exp.name, exp.formal, exp.body, env)

    def visit_app(self, exp, env):
        """
        The application of function to actual parameter must contain two cases:
        1. An anonymous function is applied: (fn x => x + 1) 2
        2. A named function is applied: f 2, where f is fun f a = a + a
        The only difference between these two cases is that in the second we
        must augment the environment with the name of the named function.

        Example:
        >>> f = Fun('f', 'v', Mul(Var('v'), Var('v')))
        >>> e0 = Let('f', f, App(Var('f'), Num(2)))
        >>> ev = EvalVisitor()
        >>> e0.accept(ev, {})
        4
        """
        fval = exp.function.accept(self, env)
        arg_value = exp.actual.accept(self, env)
        if isinstance(fval, RecFunction):
            # Caso recursivo: adiciona o nome da função ao ambiente
            new_env = dict(fval.env) if fval.env else {}
            new_env[fval.name] = fval
            new_env[fval.formal] = arg_value
            return fval.body.accept(self, new_env)
        elif isinstance(fval, Function):
            # Caso função anônima
            new_env = dict(fval.env) if fval.env else {}
            new_env[fval.formal] = arg_value
            return fval.body.accept(self, new_env)
        else:
            sys.exit("Type error")
    

class UseDefVisitor(Visitor):

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
    
    def visit_app(self, exp, defined):
        return exp.function.accept(self, defined) | exp.actual.accept(self, defined)
    
    def visit_fn(self, exp, defined):
        new_defined = defined | {exp.formal}
        return exp.body.accept(self, new_defined)
    
def safe_eval(exp):

    use_def_visitor = UseDefVisitor()
    undefined_vars = exp.accept(use_def_visitor, set())
    if undefined_vars:
        print("Error: expression contains undefined variables.")
    else:
        eval_visitor = EvalVisitor()
        value = exp.accept(eval_visitor, {})
        print("Value is", value)

class TypeVisitor(Visitor):
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
    
    def visit_app(self, exp, env):
        # For simplicity, we'll just return int for now - this would need a proper type system
        func_type = exp.function.accept(self, env)
        arg_type = exp.actual.accept(self, env)
        return int  # This is a simplified implementation
    
    def visit_fn(self, exp, env):
        # For simplicity, we'll return a function type representation
        return "function"  # This is a simplified implementation