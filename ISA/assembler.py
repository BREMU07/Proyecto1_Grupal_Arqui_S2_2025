class Assembler:
    def __init__(self):
        # Opcodes personalizados completamente diferentes a RISC-V
        self.opcodes = {
            'lw': 0xA1,      # Load Word
            'sw': 0xB2,      # Store Word  
            'add': 0xC3,     # Addition
            'sub': 0xC3,     # Subtraction (mismo opcode que add, diferenciado por funct7)
            'mul': 0xC3,     # Multiplication (mismo opcode que add, diferenciado por funct7)
            'jal': 0xD4,     # Jump and Link
            'beq': 0xE5,     # Branch if Equal
            'and': 0xF6,     # Bitwise AND
            'or': 0xF6,      # Bitwise OR (mismo opcode que and, diferenciado por funct3)
            'ebreak': 0x88   # Environment Break
        }
        
        # Códigos funct3 personalizados
        self.funct3 = {
            'lw': 0x5,       # Load Word function
            'sw': 0x6,       # Store Word function
            'add': 0x1,      # Addition function
            'sub': 0x2,      # Subtraction function
            'mul': 0x3,      # Multiplication function
            'jal': 0x0,      # Jump function
            'beq': 0x4,      # Branch Equal function
            'and': 0x1,      # AND function
            'or': 0x2,       # OR function
            'ebreak': 0x7    # System break function
        }
        
        # Códigos funct7 personalizados
        self.funct7 = {
            'add': 0x10,     # Addition extended function
            'sub': 0x20,     # Subtraction extended function
            'mul': 0x30,     # Multiplication extended function
            'and': 0x40,     # AND extended function
            'or': 0x50      # OR extended function
        }

    def parse_register(self, reg_str):
        if not reg_str or reg_str[0] != 'x':
            raise ValueError(f"Invalid register format: {reg_str}")
        val = int(reg_str[1:])
        if not (0 <= val < 32):
            raise ValueError(f"Register out of range (0-31): {reg_str}")
        return val

    # Encoding helpers para 64 bits
    def encode_r64(self, funct7, rs2, rs1, funct3, rd, opcode):
        funct7 &= 0x7F
        rs2 &= 0x1F
        rs1 &= 0x1F
        funct3 &= 0x7
        rd &= 0x1F
        opcode &= 0xFF  
        # 32 bits superiores como 0 por ahora
        instr = (funct7 << 57) | (rs2 << 52) | (rs1 << 47) | (funct3 << 44) | (rd << 39) | (opcode << 31)
        return instr

    def encode_i64(self, imm, rs1, funct3, rd, opcode):
        imm &= 0xFFFFFFFFF  # 36 bits para inmediato
        rs1 &= 0x1F
        rd &= 0x1F
        funct3 &= 0x7
        opcode &= 0xFF
        instr = (imm << 28) | (rs1 << 23) | (funct3 << 20) | (rd << 15) | (opcode << 7)
        return instr

    # Main assemble
    def assemble(self, code):
        lines = code.strip().split('\n')
        program = []
        for lineno, line in enumerate(lines, start=1):
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
            parts = line.replace(',', ' ').split()
            inst = parts[0].lower()

            # R-type instructions
            if inst in ['add', 'sub', 'mul', 'and', 'or']:
                if len(parts) < 4:
                    raise ValueError(f"[line {lineno}] Instruction {inst} missing operands.")
                rd = self.parse_register(parts[1])
                rs1 = self.parse_register(parts[2])
                rs2 = self.parse_register(parts[3])
                f7 = self.funct7.get(inst, 0)
                f3 = self.funct3.get(inst, 0)
                opcode = self.opcodes.get(inst)
                instruction = self.encode_r64(f7, rs2, rs1, f3, rd, opcode)

            # I-type lw
            elif inst == 'lw':
                rd = self.parse_register(parts[1])
                offset_rs = parts[2]
                if '(' not in offset_rs or ')' not in offset_rs:
                    raise ValueError(f"[line {lineno}] Invalid lw syntax: {line}")
                offset_str, rs1_str = offset_rs.split('(')
                rs1 = self.parse_register(rs1_str[:-1])
                offset = int(offset_str)
                instruction = self.encode_i64(offset, rs1, self.funct3['lw'], rd, self.opcodes['lw'])

            else:
                raise ValueError(f"[line {lineno}] Unknown instruction: {inst}")

            program.append(instruction & 0xFFFFFFFFFFFFFFFF)  # asegurar 64 bits

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