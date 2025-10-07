from assembler import Assembler
from simple_pipeline import Simple_Pipeline

# Read toy_mdma.asm
import os
here = os.path.dirname(__file__)
asm_path = os.path.join(here, 'toy_mdma.asm')
if not os.path.exists(asm_path):
    raise FileNotFoundError(f"toy_mdma.asm not found at {asm_path}")
with open(asm_path, 'r') as f:
    asm_code = f.read()

assembler = Assembler()
program = assembler.assemble(asm_code)

pipeline = Simple_Pipeline()

# Initialize A,B,C,D and block
pipeline.registers[1] = 0x0123456789ABCDEF  # A
pipeline.registers[2] = 0x0FEDCBA987654321  # B
pipeline.registers[3] = 0x0011223344556677  # C
pipeline.registers[4] = 0x8899AABBCCDDEEFF  # D
pipeline.registers[5] = 0x1122334455667788  # block

pipeline.load_program(program)

# write GOLDEN to memory at addr 512 (8 bytes little-endian)
pipeline.memory[512:520] = (0x9e3779b97f4a7c15 & 0xFFFFFFFFFFFFFFFF).to_bytes(8, 'little')

# Run until pipeline drains
while pipeline.is_pipeline_active():
    pipeline.step()

print('Final state:')
print(f'A (x1) = 0x{pipeline.registers[1]:016X}')
print(f'B (x2) = 0x{pipeline.registers[2]:016X}')
print(f'C (x3) = 0x{pipeline.registers[3]:016X}')
print(f'D (x4) = 0x{pipeline.registers[4]:016X}')
