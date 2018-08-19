from dataclasses import dataclass
from contextlib import contextmanager

from atlas import *
from interfaces import *
from common import *
from regfile import *

@dataclass
class Inst(object):
    # Data to match against
    opcode : int
    funct3 : int
    funct7 : int

    # Output control signals
    itype : int

    # EX control signals
    alu_src : int
    alu_op : int

    # MEM control signals
    branch : bool
    mem_write : bool
    mem_read : bool

    # WB control signals
    mem_to_reg : bool


instructions = {

    #
    # R-Type Instructions
    #

    'add': Inst(0b0110011, 0b000, 0b0000000, ITypes.R, AluSrc.rs2, 0b10, False, False, False, False),
    'sub': Inst(0b0110011, 0b000, 0b0100000, ITypes.R, AluSrc.rs2, 0b10, False, False, False, False),
    'sll': Inst(0b0110011, 0b001, 0b0000000, ITypes.R, AluSrc.rs2, 0b10, False, False, False, False),
    'xor': Inst(0b0110011, 0b100, 0b0000000, ITypes.R, AluSrc.rs2, 0b10, False, False, False, False),
    'srl': Inst(0b0110011, 0b101, 0b0000000, ITypes.R, AluSrc.rs2, 0b10, False, False, False, False),
    'or': Inst(0b0110011, 0b110, 0b0000000, ITypes.R, AluSrc.rs2, 0b10, False, False, False, False),
    'and': Inst(0b0110011, 0b111, 0b0000000, ITypes.R, AluSrc.rs2, 0b10, False, False, False, False),
    # 'lr.d': Inst(0b0110011, 0b011, 0b0001000, ITypes.R, AluSrc.rs2, 0b10, False, False, False, False),
    # 'sc.d': Inst(0b0110011, 0b011, 0b0001100, ITypes.R, AluSrc.rs2, 0b10, False, False, False, False),

    #
    # I-Type Instructions
    #

    'lb': Inst(0b0000011, 0b000, None, ITypes.I, AluSrc.none, 0b00, False, False, True, True),
    'lh': Inst(0b0000011, 0b001, None, ITypes.I, AluSrc.none, 0b00, False, False, True, True),
    'lw': Inst(0b0000011, 0b010, None, ITypes.I, AluSrc.none, 0b00, False, False, True, True),
    'ld': Inst(0b0000011, 0b011, None, ITypes.I, AluSrc.none, 0b00, False, False, True, True),
    'lbu': Inst(0b0000011, 0b100, None, ITypes.I, AluSrc.none, 0b00, False, False, True, True),
    'lhu': Inst(0b0000011, 0b101, None, ITypes.I, AluSrc.none, 0b00, False, False, True, True),
    'lwu': Inst(0b0000011, 0b110, None, ITypes.I, AluSrc.none, 0b00, False, False, True, True),
    'addi': Inst(0b0010011, 0b000, None, ITypes.I, AluSrc.imm, 0b00, False, False, False, False),
    'slli': Inst(0b0010011, 0b001, 0b0000000, ITypes.I, AluSrc.imm, 0b00, False, False, False, False),
    'xori': Inst(0b0010011, 0b100, None, ITypes.I, AluSrc.imm, 0b00, False, False, False, False),
    'srli': Inst(0b0010011, 0b101, 0b0000000, ITypes.I, AluSrc.imm, 0b00, False, False, False, False),
    'srai': Inst(0b0010011, 0b101, 0b0100000, ITypes.I, AluSrc.imm, 0b00, False, False, False, False),
    'ori': Inst(0b0010011, 0b110, None, ITypes.I, AluSrc.imm, 0b00, False, False, False, False),
    'andi': Inst(0b0010011, 0b111, None, ITypes.I, AluSrc.imm, 0b00, False, False, False, False),
    'jalr': Inst(0b1100111, 0b000, None, ITypes.I, AluSrc.none, 0b00, False, False, False, False),

    #
    # S-Type Instructions
    #

    'sb': Inst(0b0100011, 0b000, None, ITypes.S, AluSrc.none, 0b00, False, True, False, False),
    'sh': Inst(0b0100011, 0b001, None, ITypes.S, AluSrc.none, 0b00, False, True, False, False),
    'sw': Inst(0b0100011, 0b010, None, ITypes.S, AluSrc.none, 0b00, False, True, False, False),
    'sd': Inst(0b0100011, 0b111, None, ITypes.S, AluSrc.none, 0b00, False, True, False, False),

    #
    # B-Type Instructions
    #

    'beq': Inst(0b1100011, 0b000, None, ITypes.B, AluSrc.none, 0b01, True, False, False, False),
    'bne': Inst(0b1100011, 0b001, None, ITypes.B, AluSrc.none, 0b01, True, False, False, False),
    'blt': Inst(0b1100011, 0b100, None, ITypes.B, AluSrc.none, 0b01, True, False, False, False),
    'bge': Inst(0b1100011, 0b101, None, ITypes.B, AluSrc.none, 0b01, True, False, False, False),
    'bltu': Inst(0b1100011, 0b110, None, ITypes.B, AluSrc.none, 0b01, True, False, False, False),
    'bgeu': Inst(0b1100011, 0b111, None, ITypes.B, AluSrc.none, 0b01, True, False, False, False),

    #
    # U-Type Instructions
    #

    'lui': Inst(0b0110111, None, None, ITypes.U, AluSrc.none, 0b00, False, False, False, False),

    #
    # J-Type Instructions
    #

    'jal': Inst(0b1101111, None, None, ITypes.J, AluSrc.none, 0b00, True, False, False, False),
}


Opcode = lambda inst: inst(6, 0)
Rd = lambda inst: inst(11, 7)
Rs1 = lambda inst: inst(19, 15)
Rs2 = lambda inst: inst(24, 20)
Funct3 = lambda inst: inst(14, 12)
Funct7 = lambda inst: inst(31, 25)

def SetControlSignals(inst_spec, itype, ex_ctrl, mem_ctrl, wb_ctrl):
    itype <<= inst_spec.itype

    ex_ctrl.alu_src <<= inst_spec.alu_src
    ex_ctrl.alu_op <<= inst_spec.alu_op

    mem_ctrl.branch <<= 1 if inst_spec.branch else 0
    mem_ctrl.mem_write <<= 1 if inst_spec.mem_write else 0
    mem_ctrl.mem_read <<= 1 if inst_spec.mem_read else 0

    wb_ctrl.mem_to_reg <<= 1 if inst_spec.mem_to_reg else 0

def Control(inst, itype, ex_ctrl, mem_ctrl, wb_ctrl):
    itype <<= 0

    ex_ctrl.alu_src <<= 0
    ex_ctrl.alu_op <<= 0

    mem_ctrl.branch <<= 0
    mem_ctrl.mem_write <<= 0
    mem_ctrl.mem_read <<= 0

    wb_ctrl.mem_to_reg <<= 0

    opcode = Opcode(inst)
    funct3 = Funct3(inst)
    funct7 = Funct7(inst)

    for name in instructions:
        inst_spec = instructions[name]
        print(f'Instruction {name}: {inst_spec}')

        opcode_match = opcode == inst_spec.opcode
        funct3_match = 1 if inst_spec.funct3 is None else funct3 == inst_spec.funct3
        funct7_match = 1 if inst_spec.funct7 is None else funct7 == inst_spec.funct7

        with opcode_match & funct3_match & funct7_match:
            SetControlSignals(inst_spec, itype, ex_ctrl, mem_ctrl, wb_ctrl)

def GenerateImmediate(inst, itype):
    imm = Wire(Bits(32))
    zero = Wire(Bits(1))
    zero <<= 0

    #
    # N.B. This is taken directly from the RV spec.
    #

    imm <<= 0

    with itype == ITypes.I:
        imm <<= Cat([
            Fill(inst(31, 31), 21),
            inst(30, 25),
            inst(24, 21),
            inst(20, 20)
        ])

    with itype == ITypes.S:
        imm <<= Cat([
            Fill(inst(31, 31), 21),
            inst(30, 25),
            inst(11, 8),
            inst(7, 7)
        ])

    with itype == ITypes.B:
        imm <<= Cat([
            Fill(inst(31, 31), 20),
            inst(7, 7),
            inst(30, 25),
            inst(11, 8),
            zero
        ])

    with itype == ITypes.U:
        imm <<= Cat([
            inst(31, 31),
            inst(30, 20),
            inst(19, 12),
            Fill(zero, 13)
        ])

    with itype == ITypes.J:
        imm <<= Cat([
            Fill(inst(31, 31), 12),
            inst(19, 12),
            inst(20, 20),
            inst(30, 25),
            inst(24, 21),
            zero
        ])

    NameSignals(locals())
    return Cat([Fill(inst(31, 31), 32), imm])

@Module
def IDecodeStage():
    io = Io({
        'in_data': Input(if_id_bundle),
        'reg_write': Input(reg_write_bundle),
        'out_data': Output(id_ex_bundle)
    })

    regfile = Instance(RegisterFile())

    itype = Wire(Bits(ITypes.itype_width))

    regfile.r0_addr <<= Rs1(io.in_data.inst)
    regfile.r1_addr <<= Rs2(io.in_data.inst)

    regfile.w0_addr <<= io.reg_write.w_addr
    regfile.w0_en <<= io.reg_write.w_en
    regfile.w0_data <<= io.reg_write.w_data

    io.out_data.rs1_data <<= regfile.r0_data
    io.out_data.rs2_data <<= regfile.r1_data

    Control(
        io.in_data.inst,
        itype,
        io.out_data.ex_ctrl,
        io.out_data.mem_ctrl,
        io.out_data.wb_ctrl)

    io.out_data.imm <<= GenerateImmediate(io.in_data.inst, itype)

    NameSignals(locals())