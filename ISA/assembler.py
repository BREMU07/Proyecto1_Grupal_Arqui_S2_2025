class Assembler:
    def __init__(self):
        # Opcodes personalizados
        self.opcodes = {
            'lw': 0xA1,      # Load Word
            'sw': 0xB2,      # Store Word  
            'add': 0xC3,     # Addition
            'sub': 0xC3,     # Subtraction (mismo opcode que add, dif. funct7)
            'mul': 0xC3,     # Multiplication (mismo opcode que add, dif. funct7)
            'jal': 0xD4,     
            'beq': 0xE5,
            'and': 0xF6,
            'or': 0xF6,
            'ebreak': 0x88,
            # Instrucciones de bóveda
            'vwr': 0x90,     # Vault Write
            'vinit': 0x91,   # Vault Init
            'vsign': 0x92    # Vault Sign
        }

        self.funct3 = {
            'lw': 0x5, 'sw': 0x6, 'add': 0x1, 'sub': 0x2, 'mul': 0x3,
            'jal': 0x0, 'beq': 0x4, 'and': 0x1, 'or': 0x2, 'ebreak': 0x7,
            'vwr': 0x1, 'vinit': 0x2, 'vsign': 0x3
        }

        self.funct7 = {
            'add': 0x10, 'sub': 0x20, 'mul': 0x30, 'and': 0x40, 'or': 0x50
        }

    def parse_register(self, reg_str):
        if not reg_str or reg_str[0] != 'x':
            raise ValueError(f"Invalid register: {reg_str}")
        idx = int(reg_str[1:])
        if not (0 <= idx < 32):
            raise ValueError(f"Register out of range: {reg_str}")
        return idx

    def encode_r64(self, funct7, rs2, rs1, funct3, rd, opcode):
        funct7 &= 0x7F; rs2 &= 0x1F; rs1 &= 0x1F
        funct3 &= 0x7; rd &= 0x1F; opcode &= 0xFF
        return (funct7 << 57) | (rs2 << 52) | (rs1 << 47) | (funct3 << 44) | (rd << 39) | (opcode << 31)

    def encode_i64(self, imm, rs1, funct3, rd, opcode):
        imm &= 0xFFFFFFFFF; rs1 &= 0x1F; rd &= 0x1F
        funct3 &= 0x7; opcode &= 0xFF
        return (imm << 28) | (rs1 << 23) | (funct3 << 20) | (rd << 15) | (opcode << 7)

    def assemble(self, code):
        program = []
        for lineno, line in enumerate(code.strip().split('\n'), 1):
            line = line.split('#')[0].strip()
            if not line: continue
            parts = line.replace(',', ' ').split()
            inst = parts[0].lower()

            if inst in ['add', 'sub', 'mul', 'and', 'or']:
                rd = self.parse_register(parts[1])
                rs1 = self.parse_register(parts[2])
                rs2 = self.parse_register(parts[3])
                f7 = self.funct7.get(inst, 0)
                f3 = self.funct3.get(inst, 0)
                op = self.opcodes[inst]
                instr = self.encode_r64(f7, rs2, rs1, f3, rd, op)

            elif inst == 'lw':
                rd = self.parse_register(parts[1])
                off_str, rs1_str = parts[2].split('(')
                rs1 = self.parse_register(rs1_str[:-1])
                imm = int(off_str)
                instr = self.encode_i64(imm, rs1, self.funct3['lw'], rd, self.opcodes['lw'])

            elif inst == 'vwr':
                src = self.parse_register(parts[1])
                idx = int(parts[2])
                instr = self.encode_r64(0, idx, src, self.funct3['vwr'], 0, self.opcodes['vwr'])

            elif inst == 'vinit':
                src = self.parse_register(parts[1])
                idx = int(parts[2])
                instr = self.encode_r64(0, idx, src, self.funct3['vinit'], 0, self.opcodes['vinit'])

            elif inst == 'vsign':
                idx = int(parts[1])
                addr = int(parts[2])
                instr = self.encode_i64(addr, idx, self.funct3['vsign'], 0, self.opcodes['vsign'])

            else:
                raise ValueError(f"[line {lineno}] Unknown instruction: {inst}")

            program.append(instr & 0xFFFFFFFFFFFFFFFF)

        return program


# -------------------------
# Programa de prueba
# -------------------------
asm_code = """
add x1, x2, x3
add x1, x2, x4
sub x4, x5, x6
mul x7, x8, x9
and x10, x11, x12
or x13, x14, x15
lw x16, 100(x17)
"""

# -------------------------
# Ensamblar
# -------------------------
assembler = Assembler()
program = assembler.assemble(asm_code)

# -------------------------
# Mostrar instrucciones
# -------------------------
for i, instr in enumerate(program):
    print(f"Instr {i}: {instr:064b}")  # binario 64 bits
    print(f"Instr {i} hex: {instr:016X}")  # hexadecimal