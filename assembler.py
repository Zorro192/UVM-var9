import sys, yaml, struct

def pack_bits_le(fields, total_bytes):

    v = 0
    shift = 0
    for val, bits in fields:
        mask = (1 << bits) - 1
        v |= (val & mask) << shift
        shift += bits
    return v.to_bytes(total_bytes, 'little')


def encode_load_const(A,B,C):
    return pack_bits_le([(A,4),(B,16),(C,7)],4)

def encode_read(A,B,C):
    return pack_bits_le([(A,4),(B,17),(C,7)],4) if False else pack_bits_le([(A,4),(B,17),(C,7)],4)

def encode_read_correct(A,B,C):
    return pack_bits_le([(A,4),(B,17),(C,7)],4)

def encode_write(A,B,C):
    return pack_bits_le([(A,4),(B,7),(C,7)],3)

def encode_bin_less(A,B,C,D):
    return pack_bits_le([(A,4),(B,7),(C,7),(D,8)],4)

def encode_instruction(instr):
    m = instr['mnemonic'].lower()
    if m == 'load_const' or m=='ldc' or m=='const':
        A = instr['A']; B=instr['B']; C=instr['C']
        return encode_load_const(A,B,C)
    if m == 'read':
        A=instr['A']; B=instr['B']; C=instr['C']
        return pack_bits_le([(A,4),(B,17),(C,7)],4)
    if m == 'write':
        A=instr['A']; B=instr['B']; C=instr['C']
        return encode_write(A,B,C)
    if m == 'lt' or m == '<':
        A=instr['A']; B=instr['B']; C=instr['C']; D=instr['D']
        return encode_bin_less(A,B,C,D)
    raise ValueError("Unknown mnemonic: "+m)

def assemble(yaml_path, out_path, test_mode=False):
    with open(yaml_path,'r',encoding='utf-8') as f:
        prog = yaml.safe_load(f)
    ir=[]
    for ins in prog:
        ir.append(ins)
    if test_mode:
        print("Intermediate representation (IR):")
        for i,ins in enumerate(ir):
            print(i, ins)
    b = bytearray()
    for ins in ir:
        enc = encode_instruction(ins)
        b.extend(enc)
    with open(out_path,'wb') as f:
        f.write(b)
    if test_mode:
        print("Binary bytes:", [hex(x) for x in b])
        print("Wrote", len(b), "bytes to", out_path)
    return b

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument('infile')
    p.add_argument('outfile')
    p.add_argument('--test', action='store_true')
    args=p.parse_args()
    assemble(args.infile, args.outfile, args.test)
