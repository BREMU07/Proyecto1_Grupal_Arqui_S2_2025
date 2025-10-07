from assembler import Assembler
from simple_pipeline import Simple_Pipeline
import os


def rol64(x, r):
    r &= 63
    x &= 0xFFFFFFFFFFFFFFFF
    return ((x << r) | (x >> (64 - r))) & 0xFFFFFFFFFFFFFFFF


GOLDEN = 0x9e3779b97f4a7c15
PRIME = 0xFFFFFFFB


def toy_mdma_hash_block_py(block, A, B, C, D):
    A &= 0xFFFFFFFFFFFFFFFF
    B &= 0xFFFFFFFFFFFFFFFF
    C &= 0xFFFFFFFFFFFFFFFF
    D &= 0xFFFFFFFFFFFFFFFF

    f = (A & B) | (~A & C)
    g = (B & C) | (~B & D)
    h = A ^ B ^ C ^ D

    mul = (block * GOLDEN) & 0xFFFFFFFFFFFFFFFF

    A = (rol64((A + f + mul) & 0xFFFFFFFFFFFFFFFF, 7) + B) & 0xFFFFFFFFFFFFFFFF
    B = (rol64((B + g + block) & 0xFFFFFFFFFFFFFFFF, 11) + ((C * 3) & 0xFFFFFFFFFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF
    C = (rol64((C + h + mul) & 0xFFFFFFFFFFFFFFFF, 17) + (D % PRIME)) & 0xFFFFFFFFFFFFFFFF
    D = (rol64((D + A + block) & 0xFFFFFFFFFFFFFFFF, 19) ^ ((f * 5) & 0xFFFFFFFFFFFFFFFF)) & 0xFFFFFFFFFFFFFFFF

    return A, B, C, D


def run_pipeline_on_asm(asm_path, A, B, C, D, block):
    with open(asm_path, 'r') as f:
        asm_code = f.read()

    assembler = Assembler()
    program = assembler.assemble(asm_code)

    pipeline = Simple_Pipeline()
    pipeline.registers[1] = A
    pipeline.registers[2] = B
    pipeline.registers[3] = C
    pipeline.registers[4] = D
    pipeline.registers[5] = block

    pipeline.load_program(program)

    # write GOLDEN to memory at addr 512 so lw in asm can load it
    pipeline.memory[512:520] = (GOLDEN & 0xFFFFFFFFFFFFFFFF).to_bytes(8, 'little')

    # run
    steps = 0
    while pipeline.is_pipeline_active():
        pipeline.step()
        steps += 1
        if steps > 10000:
            raise RuntimeError('Pipeline did not finish after 10000 steps')

    return pipeline.registers[1], pipeline.registers[2], pipeline.registers[3], pipeline.registers[4]


def main():
    here = os.path.dirname(__file__)
    asm_path = os.path.join(here, 'toy_mdma.asm')
    if not os.path.exists(asm_path):
        print('toy_mdma.asm not found at', asm_path)
        return

    # test vector (same as run_toy_mdma.py)
    A0 = 0x0123456789ABCDEF
    B0 = 0x0FEDCBA987654321
    C0 = 0x0011223344556677
    D0 = 0x8899AABBCCDDEEFF
    block = 0x1122334455667788

    refA, refB, refC, refD = toy_mdma_hash_block_py(block, A0, B0, C0, D0)

    pipeA, pipeB, pipeC, pipeD = run_pipeline_on_asm(asm_path, A0, B0, C0, D0, block)

    print('Reference (py) result:')
    print(f' A = 0x{refA:016X}\n B = 0x{refB:016X}\n C = 0x{refC:016X}\n D = 0x{refD:016X}')
    print('\nPipeline result:')
    print(f' A = 0x{pipeA:016X}\n B = 0x{pipeB:016X}\n C = 0x{pipeC:016X}\n D = 0x{pipeD:016X}')

    ok = (refA == pipeA and refB == pipeB and refC == pipeC and refD == pipeD)
    print('\nMatch:' , ok)


if __name__ == "__main__":
    main()
