import sys
from abc import ABC, abstractmethod
from Expression import *
import Asm as AsmModule


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
    

class RenameVisitor(ABC):
    """
    This visitor traverses the AST of a program, renaming variables to ensure
    that they all have different names.

    Usage:
        >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
        >>> e1 = Let('x', e0, Mul(Var('x'), Num(10)))
        >>> e0.identifier == e1.identifier
        True

        >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
        >>> e1 = Let('x', e0, Mul(Var('x'), Num(10)))
        >>> r = RenameVisitor()
        >>> e1.accept(r, {})
        >>> e0.identifier == e1.identifier
        False

        >>> x0 = Var('x')
        >>> x1 = Var('x')
        >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
        >>> e1 = Let('x', e0, Mul(x1, Num(10)))
        >>> x0.identifier == x1.identifier
        True

        >>> x0 = Var('x')
        >>> x1 = Var('x')
        >>> e0 = Let('x', Num(2), Add(x0, Num(3)))
        >>> e1 = Let('x', e0, Mul(x1, Num(10)))
        >>> r = RenameVisitor()
        >>> e1.accept(r, {})
        >>> x0.identifier == x1.identifier
        False
    """
    
    def visit_var(self, exp, name_map):
        if exp.identifier in name_map:
            exp.identifier = name_map[exp.identifier]
        else:
            raise ValueError(f"Variavel inexistente {exp.identifier}")
        return

    def visit_bln(self, exp, name_map):
        pass

    def visit_num(self, exp, name_map):
        pass

    def visit_eql(self, exp, name_map):
        exp.left.accept(self, name_map)
        exp.right.accept(self, name_map)

    def visit_add(self, exp, name_map):
        exp.left.accept(self, name_map)
        exp.right.accept(self, name_map)

    def visit_sub(self, exp, name_map):
        exp.left.accept(self, name_map)
        exp.right.accept(self, name_map)

    def visit_mul(self, exp, name_map):
        exp.left.accept(self, name_map)
        exp.right.accept(self, name_map)

    def visit_div(self, exp, name_map):
        exp.left.accept(self, name_map)
        exp.right.accept(self, name_map)

    def visit_leq(self, exp, name_map):
        exp.left.accept(self, name_map)
        exp.right.accept(self, name_map)

    def visit_lth(self, exp, name_map):
        exp.left.accept(self, name_map)
        exp.right.accept(self, name_map)

    def visit_neg(self, exp, name_map):
        exp.exp.accept(self, name_map)

    def visit_not(self, exp, name_map):
        exp.exp.accept(self, name_map)

    def visit_let(self, exp, name_map):
        fresh_name = f"{exp.identifier}_{id(exp)}"
        old_name = exp.identifier
        exp.identifier = fresh_name
        new_map = name_map.copy()
        new_map[old_name] = fresh_name
        exp.exp_def.accept(self, name_map)
        exp.exp_body.accept(self, new_map)


class GenVisitor(Visitor):
    """
    The GenVisitor class compiles arithmetic expressions into a low-level
    language.
    """

    def __init__(self):
        self.next_var_counter = 0

    def next_var_name(self):
        self.next_var_counter += 1
        return f"v{self.next_var_counter}"

    def visit_var(self, exp, prog):
        """
        Usage:
            >>> e = Var('x')
            >>> p = AsmModule.Program(10, {"x":1}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1
        """
        return exp.identifier

    def visit_bln(self, exp, prog):
        """
        Usage:
            >>> e = Bln(True)
            >>> p = AsmModule.Program(10, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1

            >>> e = Bln(False)
            >>> p = AsmModule.Program(10, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            0
        """
        # Aloca um registrador físico ou memória para a variável
        var = self.next_var_name()
        val = 1 if exp.bln else 0
        prog.add_inst(AsmModule.Addi(var, "x0", val))
        return var

    def visit_num(self, exp, prog):
        """
        Usage:
            >>> e = Num(13)
            >>> p = AsmModule.Program(10, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            13
        """
        var = self.next_var_name()
        prog.add_inst(AsmModule.Addi(var, "x0", int(exp.num)))
        return var

    def visit_eql(self, exp, prog):
        """
        >>> e = Eql(Num(13), Num(13))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Eql(Num(13), Num(10))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Eql(Num(-1), Num(1))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        left = exp.left.accept(self, prog)
        right = exp.right.accept(self, prog)
        diff = self.next_var_name()
        prog.add_inst(AsmModule.Sub(diff, left, right))
        tmp = self.next_var_name()                   # esse método é para que funcione com números negativos
        prog.add_inst(AsmModule.Slti(tmp, diff, 1))  # tmp = (diff < 1)
        tmp2 = self.next_var_name()
        prog.add_inst(AsmModule.Slti(tmp2, diff, 0)) # tmp2 = (diff < 0)
        result = self.next_var_name()
        prog.add_inst(AsmModule.Sub(result, tmp, tmp2)) # result = (diff < 1) - (diff < 0)
        return result

    def visit_add(self, exp, prog):
        """
        >>> e = Add(Num(13), Num(-13))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Add(Num(13), Num(10))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        23
        """
        left_var = exp.left.accept(self, prog)
        right_var = exp.right.accept(self, prog)
        var = self.next_var_name()
        prog.add_inst(AsmModule.Add(var, left_var, right_var))
        return var

    def visit_sub(self, exp, prog):
        """
        >>> e = Sub(Num(13), Num(-13))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        26

        >>> e = Sub(Num(13), Num(10))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3
        """
        left = exp.left.accept(self, prog)
        right = exp.right.accept(self, prog)
        var = self.next_var_name()
        prog.add_inst(AsmModule.Sub(var, left, right))
        return var

    def visit_mul(self, exp, prog):
        """
        >>> e = Mul(Num(13), Num(2))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        26

        >>> e = Mul(Num(13), Num(10))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        130
        """
        left = exp.left.accept(self, prog)
        right = exp.right.accept(self, prog)
        var = self.next_var_name()
        prog.add_inst(AsmModule.Mul(var, left, right))
        return var

    def visit_div(self, exp, prog):
        """
        >>> e = Div(Num(13), Num(2))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        6

        >>> e = Div(Num(13), Num(10))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1
        """
        left = exp.left.accept(self, prog)
        right = exp.right.accept(self, prog)
        var = self.next_var_name()
        prog.add_inst(AsmModule.Div(var, left, right))
        return var

    def visit_leq(self, exp, prog):
        """
        >>> e = Leq(Num(3), Num(2))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Leq(Num(3), Num(3))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(2), Num(3))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-3), Num(-2))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-3), Num(-3))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Leq(Num(-2), Num(-3))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        left = exp.left.accept(self, prog)
        right = exp.right.accept(self, prog)
        tmp = self.next_var_name()
        prog.add_inst(AsmModule.Slt(tmp, right, left))  # right < left
        result = self.next_var_name()
        prog.add_inst(AsmModule.Xori(result, tmp, 1))  # leq = not(right < left)
        return result

    def visit_lth(self, exp, prog):
        """
        >>> e = Lth(Num(3), Num(2))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Lth(Num(3), Num(3))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Lth(Num(2), Num(3))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1
        """
        left = exp.left.accept(self, prog)
        right = exp.right.accept(self, prog)
        var = self.next_var_name()
        prog.add_inst(AsmModule.Slt(var, left, right))
        return var

    def visit_neg(self, exp, prog):
        """
        >>> e = Neg(Num(3))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        -3

        >>> e = Neg(Num(0))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Neg(Num(-3))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        3
        """
        val = exp.exp.accept(self, prog)
        var = self.next_var_name()
        prog.add_inst(AsmModule.Sub(var, "x0", val))
        return var

    def visit_not(self, exp, prog):
        """
        >>> e = Not(Bln(True))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Not(Bln(False))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Not(Num(0))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        1

        >>> e = Not(Num(-2))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0

        >>> e = Not(Num(2))
        >>> p = AsmModule.Program(10, {}, [])
        >>> g = GenVisitor()
        >>> v = e.accept(g, p)
        >>> p.eval()
        >>> p.get_val(v)
        0
        """
        val = exp.exp.accept(self, prog)
        tmp = self.next_var_name()
        prog.add_inst(AsmModule.Slt(tmp, "x0", val))  # tmp = (0 < val) ? 1 : 0  is positive
        tmp2 = self.next_var_name()
        prog.add_inst(AsmModule.Slt(tmp2, val, "x0")) # tmp2 = (val < 0) ? 1 : 0 is negative
        norm = self.next_var_name()
        prog.add_inst(AsmModule.Add(norm, tmp, tmp2))    # norm = (val > 0) + (val < 0) => 1 if val != 0 else 0  is 0 our not
        var = self.next_var_name()
        prog.add_inst(AsmModule.Xori(var, norm, 1))      # var = not(norm) inverts
        return var


    def visit_let(self, exp, prog):
        """
        Usage:
            >>> e = Let('v', Not(Bln(False)), Var('v'))
            >>> p = AsmModule.Program(10, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            1

            >>> e = Let('v', Num(2), Add(Var('v'), Num(3)))
            >>> p = AsmModule.Program(10, {}, [])
            >>> g = GenVisitor()
            >>> v = e.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            5

            >>> e0 = Let('x', Num(2), Add(Var('x'), Num(3)))
            >>> e1 = Let('y', e0, Mul(Var('y'), Num(10)))
            >>> p = AsmModule.Program(10, {}, [])
            >>> g = GenVisitor()
            >>> v = e1.accept(g, p)
            >>> p.eval()
            >>> p.get_val(v)
            50
        """

        var_exp_def = exp.exp_def.accept(self, prog)
        prog.add_inst(AsmModule.Add(exp.identifier, "x0", var_exp_def))
        var = self.next_var_name()
        var_exp_body = exp.exp_body.accept(self, prog)
        prog.add_inst(AsmModule.Add(var, "x0", var_exp_body))
        return var

class EvalVisitor(Visitor):
    """
    The EvalVisitor class evaluates expressions and returns their values.
    This visitor is used for testing the parser.
    """

    def visit_var(self, exp, env):
        if env and exp.identifier in env:
            return env[exp.identifier]
        else:
            raise NameError(f"Variable {exp.identifier} not defined")

    def visit_bln(self, exp, env):
        return exp.bln

    def visit_num(self, exp, env):
        return exp.num

    def visit_eql(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        return left == right

    def visit_and(self, exp, env):
        left = exp.left.accept(self, env)
        if not left:
            return False
        right = exp.right.accept(self, env)
        return bool(left and right)

    def visit_or(self, exp, env):
        left = exp.left.accept(self, env)
        if left:
            return True
        right = exp.right.accept(self, env)
        return bool(left or right)

    def visit_add(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        return left + right

    def visit_sub(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        return left - right

    def visit_mul(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        return left * right

    def visit_div(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        return left // right

    def visit_leq(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        return left <= right

    def visit_lth(self, exp, env):
        left = exp.left.accept(self, env)
        right = exp.right.accept(self, env)
        return left < right

    def visit_neg(self, exp, env):
        val = exp.exp.accept(self, env)
        return -val

    def visit_not(self, exp, env):
        val = exp.exp.accept(self, env)
        return not val

    def visit_let(self, exp, env):
        if env is None:
            env = {}
        val = exp.exp_def.accept(self, env)
        new_env = env.copy()
        new_env[exp.identifier] = val
        return exp.exp_body.accept(self, new_env)

    def visit_ifThenElse(self, exp, env):
        cond = exp.cond.accept(self, env)
        if cond:
            return exp.e0.accept(self, env)
        else:
            return exp.e1.accept(self, env)