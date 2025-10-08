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


class CtrGenVisitor(Visitor):
    """
    This visitor creates constraints for a type-inference engine. Basically,
    it traverses the abstract-syntax tree of expressions, producing pairs like
    (type0, type1) on the way. A pair like (type0, type1) indicates that these
    two type variables are the same.

    Examples:
        >>> e = Let('v', Num(40), Let('w', Num(2), Add(Var('v'), Var('w'))))
        >>> ev = CtrGenVisitor()
        >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
        ["('TV_1', 'TV_2')", "('TV_2', 'TV_3')", "('v', <class 'int'>)", "('w', <class 'int'>)", "(<class 'int'>, 'TV_3')", "(<class 'int'>, 'v')", "(<class 'int'>, 'w')"]
    """

    def __init__(self):
        self.fresh_type_counter = 0

    def fresh_type_var(self):
        """
        Create a new type var using the current value of the fresh_type_counter.
        Two successive calls to this method will return different type names.
        Notice that the name of a type variable is always TV_x, where x is
        some integer number. That means that probably we would run into
        errors if someone declares a variable called, say, TV_1 or TV_2, as in
        "let TV_1 <- 1 in TV_1 end". But you can assume that such would never
        happen in the test cases. In practice, we should define a new class
        to represent type variables. But let's keep the implementation as
        simple as possible.

        Example:
            >>> ev = CtrGenVisitor()
            >>> [ev.fresh_type_var(), ev.fresh_type_var()]
            ['TV_1', 'TV_2']
        """
        self.fresh_type_counter += 1
        return f"TV_{self.fresh_type_counter}"

    """
    The CtrGenVisitor class creates constraints that, once solved, will give
    us the type of the different variables. Every accept method takes in
    two arguments (in addition to self):
    
    exp: is the expression that is being analyzed.
    type_var: that is a name that works as a placeholder for the type of the
    expression. Whenever we visit a new expression, we create a type variable
    to represent its type (you can do that with the method fresh_type_var).
    The only exception is the type of Var expressions. In this case, the type
    of a Var expression is the identifier of that expression.
    """

    def visit_var(self, exp, type_var):
        """
        Example:
            >>> e = Var('v')
            >>> ev = CtrGenVisitor()
            >>> e.accept(ev, ev.fresh_type_var())
            {('v', 'TV_1')}
        """
        return {(exp.identifier, type_var)}

    def visit_bln(self, exp, type_var):
        """
        Example:
            >>> e = Bln(True)
            >>> ev = CtrGenVisitor()
            >>> e.accept(ev, ev.fresh_type_var())
            {(<class 'bool'>, 'TV_1')}
        """
        return {(type(True), type_var)}

    def visit_num(self, exp, type_var):
        """
        Example:
            >>> e = Num(1)
            >>> ev = CtrGenVisitor()
            >>> e.accept(ev, ev.fresh_type_var())
            {(<class 'int'>, 'TV_1')}
        """
        return {(type(1), type_var)}

    def visit_eql(self, exp, type_var):
        """
        Example:
            >>> e = Eql(Num(1), Bln(True))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'bool'>, 'TV_2')", "(<class 'int'>, 'TV_2')"]

        Notice that if we have repeated constraints, they only appear once in
        the set of constraints (after all, it's a set!). As an example, we
        would have two occurrences of the pair (TV_2, int) in the following
        example:
            >>> e = Eql(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'int'>, 'TV_2')"]
        """
        # Create fresh type variables for operands
        left_type_var = self.fresh_type_var()
        right_type_var = self.fresh_type_var()
        
        # Get constraints from operands
        left_constraints = exp.left.accept(self, left_type_var)
        right_constraints = exp.right.accept(self, right_type_var)
        
        # Equality operation requires both operands to have the same type
        # The result is always boolean
        result_constraints = {
            (type(True), type_var),  # Result is boolean
            (left_type_var, right_type_var)  # Both operands must have same type
        }
        
        return left_constraints | right_constraints | result_constraints

    def visit_and(self, exp, type_var):
        """
        Example:
            >>> e = And(Bln(False), Bln(True))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'bool'>, <class 'bool'>)"]

        In the above example, notice that we ended up getting a trivial
        constraint, e.g.: (<class 'bool'>, <class 'bool'>). That's alright:
        don't worry about these trivial constraints at this point. We can
        remove them from the set of constraints later on, when we try to
        solve them.
        """
        # Create fresh type variables for operands
        left_type_var = self.fresh_type_var()
        right_type_var = self.fresh_type_var()
        
        # Get constraints from operands
        left_constraints = exp.left.accept(self, left_type_var)
        right_constraints = exp.right.accept(self, right_type_var)
        
        # And operation requires both operands to be boolean
        # The result is also boolean
        result_constraints = {
            (type(True), type_var),        # Result is boolean
            (type(True), left_type_var),   # Left operand must be boolean
            (type(True), right_type_var)   # Right operand must be boolean
        }
        
        return left_constraints | right_constraints | result_constraints

    def visit_or(self, exp, type_var):
        """
        Example:
            >>> e = Or(Bln(False), Bln(True))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'bool'>, <class 'bool'>)"]
        """
        # Create fresh type variables for operands
        left_type_var = self.fresh_type_var()
        right_type_var = self.fresh_type_var()
        
        # Get constraints from operands
        left_constraints = exp.left.accept(self, left_type_var)
        right_constraints = exp.right.accept(self, right_type_var)
        
        # Or operation requires both operands to be boolean
        # The result is also boolean
        result_constraints = {
            (type(True), type_var),        # Result is boolean
            (type(True), left_type_var),   # Left operand must be boolean
            (type(True), right_type_var)   # Right operand must be boolean
        }
        
        return left_constraints | right_constraints | result_constraints

    def visit_add(self, exp, type_var):
        """
        Example:
            >>> e = Add(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'int'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        # Create fresh type variables for operands
        left_type_var = self.fresh_type_var()
        right_type_var = self.fresh_type_var()
        
        # Get constraints from operands
        left_constraints = exp.left.accept(self, left_type_var)
        right_constraints = exp.right.accept(self, right_type_var)
        
        # Add operation requires both operands to be integers
        # The result is also integer
        result_constraints = {
            (type(1), type_var),        # Result is integer
            (type(1), left_type_var),   # Left operand must be integer
            (type(1), right_type_var)   # Right operand must be integer
        }
        
        return left_constraints | right_constraints | result_constraints

    def visit_sub(self, exp, type_var):
        """
        Example:
            >>> e = Sub(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'int'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        # Create fresh type variables for operands
        left_type_var = self.fresh_type_var()
        right_type_var = self.fresh_type_var()
        
        # Get constraints from operands
        left_constraints = exp.left.accept(self, left_type_var)
        right_constraints = exp.right.accept(self, right_type_var)
        
        # Sub operation requires both operands to be integers
        # The result is also integer
        result_constraints = {
            (type(1), type_var),        # Result is integer
            (type(1), left_type_var),   # Left operand must be integer
            (type(1), right_type_var)   # Right operand must be integer
        }
        
        return left_constraints | right_constraints | result_constraints

    def visit_mul(self, exp, type_var):
        """
        Example:
            >>> e = Mul(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'int'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        # Create fresh type variables for operands
        left_type_var = self.fresh_type_var()
        right_type_var = self.fresh_type_var()
        
        # Get constraints from operands
        left_constraints = exp.left.accept(self, left_type_var)
        right_constraints = exp.right.accept(self, right_type_var)
        
        # Mul operation requires both operands to be integers
        # The result is also integer
        result_constraints = {
            (type(1), type_var),        # Result is integer
            (type(1), left_type_var),   # Left operand must be integer
            (type(1), right_type_var)   # Right operand must be integer
        }
        
        return left_constraints | right_constraints | result_constraints

    def visit_div(self, exp, type_var):
        """
        Example:
            >>> e = Div(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'int'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        # Create fresh type variables for operands
        left_type_var = self.fresh_type_var()
        right_type_var = self.fresh_type_var()
        
        # Get constraints from operands
        left_constraints = exp.left.accept(self, left_type_var)
        right_constraints = exp.right.accept(self, right_type_var)
        
        # Div operation requires both operands to be integers
        # The result is also integer
        result_constraints = {
            (type(1), type_var),        # Result is integer
            (type(1), left_type_var),   # Left operand must be integer
            (type(1), right_type_var)   # Right operand must be integer
        }
        
        return left_constraints | right_constraints | result_constraints

    def visit_leq(self, exp, type_var):
        """
        Example:
            >>> e = Leq(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        # Create fresh type variables for operands
        left_type_var = self.fresh_type_var()
        right_type_var = self.fresh_type_var()
        
        # Get constraints from operands
        left_constraints = exp.left.accept(self, left_type_var)
        right_constraints = exp.right.accept(self, right_type_var)
        
        # Leq operation requires both operands to be integers
        # The result is boolean
        result_constraints = {
            (type(True), type_var),     # Result is boolean
            (type(1), left_type_var),   # Left operand must be integer
            (type(1), right_type_var)   # Right operand must be integer
        }
        
        return left_constraints | right_constraints | result_constraints

    def visit_lth(self, exp, type_var):
        """
        Example:
            >>> e = Lth(Num(1), Num(2))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        # Create fresh type variables for operands
        left_type_var = self.fresh_type_var()
        right_type_var = self.fresh_type_var()
        
        # Get constraints from operands
        left_constraints = exp.left.accept(self, left_type_var)
        right_constraints = exp.right.accept(self, right_type_var)
        
        # Lth operation requires both operands to be integers
        # The result is boolean
        result_constraints = {
            (type(True), type_var),     # Result is boolean
            (type(1), left_type_var),   # Left operand must be integer
            (type(1), right_type_var)   # Right operand must be integer
        }
        
        return left_constraints | right_constraints | result_constraints

    def visit_neg(self, exp, type_var):
        """
        Example:
            >>> e = Neg(Num(1))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'int'>, 'TV_1')", "(<class 'int'>, <class 'int'>)"]
        """
        # Create fresh type variable for operand
        operand_type_var = self.fresh_type_var()
        
        # Get constraints from operand
        operand_constraints = exp.exp.accept(self, operand_type_var)
        
        # Neg operation requires operand to be integer
        # The result is also integer
        result_constraints = {
            (type(1), type_var),        # Result is integer
            (type(1), operand_type_var) # Operand must be integer
        }
        
        return operand_constraints | result_constraints

    def visit_not(self, exp, type_var):
        """
        Example:
            >>> e = Not(Bln(True))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["(<class 'bool'>, 'TV_1')", "(<class 'bool'>, <class 'bool'>)"]
        """
        # Create fresh type variable for operand
        operand_type_var = self.fresh_type_var()
        
        # Get constraints from operand
        operand_constraints = exp.exp.accept(self, operand_type_var)
        
        # Not operation requires operand to be boolean
        # The result is also boolean
        result_constraints = {
            (type(True), type_var),        # Result is boolean
            (type(True), operand_type_var) # Operand must be boolean
        }
        
        return operand_constraints | result_constraints

    def visit_let(self, exp, type_var):
        """
        Example:
            >>> e = Let('v', Num(42), Var('v'))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["('TV_1', 'TV_2')", "('v', 'TV_2')", "(<class 'int'>, 'v')"]
        """
        # Create fresh type variables
        def_type_var = self.fresh_type_var()
        body_type_var = self.fresh_type_var()
        
        # Get constraints from definition and body
        def_constraints = exp.exp_def.accept(self, def_type_var)
        body_constraints = exp.exp_body.accept(self, body_type_var)
        
        # Let constraints:
        # 1. The variable has the same type as its definition
        # 2. The result has the same type as the body
        result_constraints = {
            (exp.identifier, def_type_var),  # Variable type = definition type
            (type_var, body_type_var)        # Result type = body type
        }
        
        return def_constraints | body_constraints | result_constraints

    def visit_ifThenElse(self, exp, type_var):
        """
        Example:
            >>> e = IfThenElse(Bln(True), Num(42), Num(30))
            >>> ev = CtrGenVisitor()
            >>> sorted([str(ct) for ct in e.accept(ev, ev.fresh_type_var())])
            ["('TV_1', 'TV_2')", "(<class 'bool'>, <class 'bool'>)", "(<class 'int'>, 'TV_2')"]
        """
        # Create fresh type variables
        cond_type_var = self.fresh_type_var()
        then_type_var = self.fresh_type_var()
        else_type_var = self.fresh_type_var()
        
        # Get constraints from all branches
        cond_constraints = exp.cond.accept(self, cond_type_var)
        then_constraints = exp.e0.accept(self, then_type_var)
        else_constraints = exp.e1.accept(self, else_type_var)
        
        # IfThenElse constraints:
        # 1. Condition must be boolean
        # 2. Both branches must have the same type
        # 3. Result has the same type as both branches
        result_constraints = {
            (type(True), cond_type_var),  # Condition must be boolean
            (then_type_var, else_type_var),  # Both branches same type
            (type_var, then_type_var)     # Result type = branch type
        }
        
        return cond_constraints | then_constraints | else_constraints | result_constraints