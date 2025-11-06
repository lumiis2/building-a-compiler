from abc import ABC, abstractmethod
from Asm import *


class Optimizer(ABC):
    """
    This class implements an "Optimization Pass". The pass receives a sequence
    of instructions stored in a program, and produces a new sequence of
    instructions.
    """

    def __init__(self, prog):
        self.prog = prog

    @abstractmethod
    def optimize(self):
        pass


class RegAllocator(Optimizer):
    """This file implements the register allocation pass."""

    DEFAULT_REGS = {"x0", "sp", "ra"}

    def __init__(self, prog):
        super().__init__(prog)
        self.memory_counter = 0
        self.var_to_mem = {}
        self.var_to_reg = {}

        self.op_handlers = {
            "addi": self.handle_bin_immediate,
            "xori": self.handle_bin_immediate,
            "slti": self.handle_bin_immediate,
            "add": self.handle_bin_standard,
            "sub": self.handle_bin_standard,
            "mul": self.handle_bin_standard,
            "div": self.handle_bin_standard,
            "xor": self.handle_bin_standard,
            "slt": self.handle_bin_standard,
            "jal": self.handle_jump,
            "jalr": self.handle_jump,
            "beq": self.handle_branch,
            "lw": self.handle_memory_op,
            "sw": self.handle_memory_op,
        }

    def _next_memory_slot(self):
        self.memory_counter += 1
        return self.memory_counter

    def _ensure_memory(self, var):
        if var not in self.DEFAULT_REGS and var not in self.var_to_mem:
            self.var_to_mem[var] = self._next_memory_slot()

    def get_val(self, var):
        if var not in self.var_to_mem:
            raise ValueError(f"Variable {var} not declared in memory")
        return self.prog.get_mem(self.var_to_mem[var])

    def _load(self, var, target_reg, insts):
        if var in self.DEFAULT_REGS:
            return var
        insts.append(Lw("x0", self.var_to_mem[var], target_reg))
        return target_reg

    def _store(self, var, source_reg, insts):
        if var not in self.DEFAULT_REGS:
            insts.append(Sw("x0", self.var_to_mem[var], source_reg))

    def handle_jump(self, inst):
        self._ensure_memory(inst.rd)
        insts = []

        dest_reg = "a0" if inst.rd not in self.DEFAULT_REGS else inst.rd
        if inst.rd not in self.DEFAULT_REGS:
            self.var_to_reg[inst.rd] = "a0"
            insts.append(Addi("a0", "x0", self.prog.get_pc()))
            insts.append(Sw("x0", self.var_to_mem[inst.rd], "a0"))
            dest_reg = "x0"

        if inst.get_opcode() == "jal":
            insts.append(Jal(dest_reg, inst.lab))
        else:  # jalr
            src_reg = self._load(inst.rs, "a1", insts)
            insts.append(Jalr(dest_reg, src_reg, inst.offset))

        return insts

    def handle_branch(self, inst):
        insts = []
        rs1 = self._load(inst.rs1, "a0", insts)
        rs2 = self._load(inst.rs2, "a1", insts)
        insts.append(Beq(rs1, rs2, inst.lab))
        return insts

    def handle_memory_op(self, inst):
        insts = []
        opcode = inst.get_opcode()

        if opcode == "lw":
            self._ensure_memory(inst.reg)
            dest_reg = "a0" if inst.reg not in self.DEFAULT_REGS else inst.reg
            if inst.reg not in self.DEFAULT_REGS:
                self.var_to_reg[inst.reg] = "a0"
            base_reg = self._load(inst.rs1, "a1", insts)
            insts.append(Lw(base_reg, inst.offset, dest_reg))
            self._store(inst.reg, dest_reg, insts)

        else:  # sw
            val_reg = self._load(inst.reg, "a0", insts)
            base_reg = self._load(inst.rs1, "a1", insts)
            insts.append(Sw(base_reg, inst.offset, val_reg))

        return insts
    
    def handle_bin_immediate(self, inst):
        self._ensure_memory(inst.rd)
        insts = []

        dest_reg = "a0" if inst.rd not in self.DEFAULT_REGS else inst.rd
        if inst.rd not in self.DEFAULT_REGS:
            self.var_to_reg[inst.rd] = "a0"

        rs1 = self._load(inst.rs1, "a0", insts)
        op_class = {"addi": Addi, "xori": Xori, "slti": Slti}[inst.get_opcode()]
        insts.append(op_class(dest_reg, rs1, inst.imm))
        self._store(inst.rd, dest_reg, insts)

        return insts

    def handle_bin_standard(self, inst):
        self._ensure_memory(inst.rd)
        insts = []

        dest_reg = "a0" if inst.rd not in self.DEFAULT_REGS else inst.rd
        if inst.rd not in self.DEFAULT_REGS:
            self.var_to_reg[inst.rd] = "a0"

        rs1 = self._load(inst.rs1, "a0", insts)
        rs2 = self._load(inst.rs2, "a1", insts)

        op_class = {
            "add": Add, "sub": Sub, "mul": Mul, "div": Div, "xor": Xor, "slt": Slt
        }[inst.get_opcode()]
        insts.append(op_class(dest_reg, rs1, rs2))
        self._store(inst.rd, dest_reg, insts)

        return insts

    def optimize(self):
        """
        This function perform register allocation. It maps variables into
        memory, and changes instructions, so that they use one of the following
        registers:
        * x0: always the value zero. Can't change.
        * sp: the stack pointer. Starts with the memory size.
        * ra: the return address.
        * a0: function argument 0 (or return address)
        * a1: function argument 1
        * a2: function argument 2
        * a3: function argument 3

        Notice that next to each register we have suggested a usage. You can,
        of course, write on them and use them in other ways. But, at least x0
        and sp you should not overwrite. The first register you can't overwrite,
        actually. And sp is initialized with the number of memory addresses.
        It's good to use it to control the function stack.

        Examples:
        >>> insts = [Addi("a", "x0", 3)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> o.get_val("a")
        3

        >>> insts = [Addi("a", "x0", 1), Slti("b", "a", 2)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> o.get_val("b")
        1

        >>> insts = [Addi("a", "x0", 3), Slti("b", "a", 2), Xori("c", "b", 5)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> o.get_val("c")
        5

        >>> insts = [Addi("sp", "sp", -1),Addi("a", "x0", 7),Sw("sp", 0, "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_mem(p.get_val("sp"))
        7

        >>> insts = [Addi("sp", "sp", -1),Addi("a", "x0", 7),Sw("sp", 0, "a")]
        >>> insts += [Lw("sp", 0, "b"), Addi("c", "b", 6)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> o.get_val("c")
        13

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Add("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> o.get_val("c")
        7

        >>> insts = [Addi("a", "x0", 28),Addi("b", "x0", 4),Div("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> o.get_val("c")
        7

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Mul("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> o.get_val("c")
        12

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Xor("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> o.get_val("c")
        7

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Slt("c", "a", "b")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> o.get_val("c")
        1

        >>> insts = [Addi("a", "x0", 3),Addi("b", "x0", 4),Slt("c", "b", "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> o.get_val("c")
        0

        If you want, you can allocate Jal/Jalr/Beq instructions, but that's not
        necessary for this exercise.

        >>> insts = [Jal("a", 30)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> (p.get_pc(), o.get_val("a") > 0)
        (30, True)

        >>> insts = [Addi("a", "x0", 30), Jalr("b", "a")]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> (p.get_pc(), o.get_val("b") > 0)
        (30, True)

        >>> insts = [Addi("a", "x0", 3), Addi("b", "a", 0), Beq("a", "b", 30)]
        >>> p = Program(1000, env={}, insts=insts)
        >>> o = RegAllocator(p)
        >>> o.optimize()
        >>> p.eval()
        >>> p.get_pc()
        30
        """
        new_insts = []
        for inst in self.prog.get_insts():
            handler = self.op_handlers.get(inst.get_opcode())
            if handler:
                new_insts.extend(handler(inst))
        self.prog.set_insts(new_insts)