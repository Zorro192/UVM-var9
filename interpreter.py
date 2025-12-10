#!/usr/bin/env python3
"""
Interpreter for Variant 9 binary with registers.
Memory: 64 cells
Registers: 16 cells
"""

import sys, xml.etree.ElementTree as ET

# ---------------------------
#  MEMORY + REGISTERS
# ---------------------------

MEM_SIZE = 4096
REG_COUNT = 128

def make_mem():
    return [0] * MEM_SIZE

def make_regs():
    return [0] * REG_COUNT

def read_mem(mem, addr):
    if addr < 0 or addr >= MEM_SIZE:
        raise IndexError(f"Memory read OOB: {addr}")
    return mem[addr]

def write_mem(mem, addr, val):
    if addr < 0 or addr >= MEM_SIZE:
        raise IndexError(f"Memory write OOB: {addr}")
    mem[addr] = val & 0xFFFFFFFF

def read_reg(regs, r):
    if r < 0 or r >= REG_COUNT:
        raise IndexError(f"Register read OOB: R{r}")
    return regs[r]

def write_reg(regs, r, val):
    if r < 0 or r >= REG_COUNT:
        raise IndexError(f"Register write OOB: R{r}")
    regs[r] = val & 0xFFFFFFFF

# ---------------------------
#  PARSER
# ---------------------------

def parse_commands(bytearr):
    pc = 0
    cmds = []
    while pc < len(bytearr):

        first = bytearr[pc]
        A = first & 0x0F  # opcode

        if A in (1, 4, 9):     # 4-byte commands
            chunk = bytearr[pc:pc+4]
            val = int.from_bytes(chunk, "little")

            if A == 1:  # load_const: A4, B16, C7
                B = (val >> 4) & 0xFFFF
                C = (val >> 20) & 0x7F
                cmds.append(("load_const", B, C))

            elif A == 4:  # read: A4, B17, C7
                B = (val >> 4) & 0x1FFFF
                C = (val >> 21) & 0x7F
                cmds.append(("read", B, C))

            elif A == 9:  # lt: A4, B7, C7, D8
                B = (val >> 4) & 0x7F
                C = (val >> 11) & 0x7F
                D = (val >> 18) & 0xFF
                cmds.append(("lt", B, C, D))

            pc += 4

        else:  # 3-byte write (A == 15)
            chunk = bytearr[pc:pc+3]
            val = int.from_bytes(chunk, "little")
            B = (val >> 4) & 0x7F
            C = (val >> 11) & 0x7F
            cmds.append(("write", B, C))
            pc += 3

    return cmds

# ---------------------------
#  EXECUTION
# ---------------------------

def run_binary(binfile, dumpfile, start=0, end=64):

    with open(binfile, "rb") as f:
        bytearr = list(f.read())

    cmds = parse_commands(bytearr)

    mem = make_mem()
    regs = make_regs()

    for ins in cmds:

        if ins[0] == "load_const":
            _, B, C = ins
            write_reg(regs, C, B)

        elif ins[0] == "read":
            _, B, C = ins
            val = read_mem(mem, B)
            write_reg(regs, C, val)

        elif ins[0] == "write":
            _, B, C = ins
            val = read_reg(regs, B)
            addr = read_reg(regs, C)
            write_mem(mem, addr, val)

        elif ins[0] == "lt":
            _, B, C, D = ins
            base = read_reg(regs, C)
            addr = base + D
            op1 = read_mem(mem, addr)
            op2 = read_mem(mem, B)
            res = 1 if op1 < op2 else 0
            write_mem(mem, addr, res)

    # output
    root = ET.Element("memory")
    for i in range(start, min(end, MEM_SIZE)):
        cell = ET.SubElement(root, "cell", addr=str(i))
        cell.text = str(mem[i])

    tree = ET.ElementTree(root)
    tree.write(dumpfile, encoding="utf-8", xml_declaration=True)

    print("Program executed. Dump written to", dumpfile)

# ---------------------------
#  ENTRY POINT
# ---------------------------

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("binfile")
    p.add_argument("dumpfile")
    p.add_argument("--start", type=int, default=0)
    p.add_argument("--end", type=int, default=64)
    args = p.parse_args()
    run_binary(args.binfile, args.dumpfile, args.start, args.end)
