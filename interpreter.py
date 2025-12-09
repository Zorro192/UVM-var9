
import sys, xml.etree.ElementTree as ET


MEMORY_SIZE = 4096
def make_mem():
    return [0]*MEMORY_SIZE

def read_word(mem, addr):
    if addr<0 or addr>=MEMORY_SIZE: raise IndexError("mem read out of range "+str(addr))
    return mem[addr]
def write_word(mem, addr, val):
    if addr<0 or addr>=MEMORY_SIZE: raise IndexError("mem write out of range "+str(addr))
    mem[addr] = val & 0xFFFFFFFF


def parse_commands(bytearr):
    pc = 0
    cmds=[]
    while pc < len(bytearr):
        first = bytearr[pc]
        A = first & 0x0F
        if A in (1,4,9): # 4-byte commands
            chunk = bytearr[pc:pc+4]
            val = int.from_bytes(chunk,'little')
            if A==1:
                B = (val >> 4) & ((1<<16)-1)
                C = (val >> 20) & ((1<<7)-1)
                cmds.append(('load_const',A,B,C))
            elif A==4:
                B = (val >> 4) & ((1<<17)-1)
                C = (val >> 21) & ((1<<7)-1)
                cmds.append(('read',A,B,C))
            elif A==9:
                B = (val >> 4) & ((1<<7)-1)
                C = (val >> 11) & ((1<<7)-1)
                D = (val >> 18) & ((1<<8)-1)
                cmds.append(('lt',A,B,C,D))
            pc += 4
        else:
            chunk = bytearr[pc:pc+3]
            val = int.from_bytes(chunk,'little')
            B = (val >> 4) & ((1<<7)-1)
            C = (val >> 11) & ((1<<7)-1)
            cmds.append(('write',A,B,C))
            pc += 3
    return cmds

def run_binary(bin_path, dump_xml_path, dump_start=0, dump_end=64):
    with open(bin_path,'rb') as f:
        data = f.read()
    bytes_arr = list(data)
    cmds = parse_commands(bytes_arr)
    mem = make_mem()
    for ins in cmds:
        if ins[0]=='load_const':
            _,A,B,C = ins
            const = B
            regaddr = C
            write_word(mem, regaddr, const)
        elif ins[0]=='read':
            _,A,B,C = ins
            addr = B
            val = read_word(mem, addr)
            write_word(mem, C, val)
        elif ins[0]=='write':
            _,A,B,C = ins
            val = read_word(mem, B)
            dest_addr = read_word(mem, C)
            write_word(mem, dest_addr, val)
        elif ins[0]=='lt':
            _,A,B,C,D = ins
            base = read_word(mem, C)
            addr = base + D
            op1 = read_word(mem, addr)
            op2 = read_word(mem, B)
            res = 1 if op1 < op2 else 0
            write_word(mem, addr, res)
        else:
            raise RuntimeError("Unknown instruction "+str(ins))
    root = ET.Element('memory')
    for addr in range(dump_start, min(dump_end, len(mem))):
        cell = ET.SubElement(root, 'cell', addr=str(addr))
        cell.text = str(mem[addr])
    tree = ET.ElementTree(root)
    tree.write(dump_xml_path, encoding='utf-8', xml_declaration=True)
    print("Executed", len(cmds), "instructions. Memory dumped to", dump_xml_path)

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('binfile')
    p.add_argument('dumpfile')
    p.add_argument('--start', type=int, default=0)
    p.add_argument('--end', type=int, default=64)
    args=p.parse_args()
    run_binary(args.binfile, args.dumpfile, args.start, args.end)
