
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
            'xor': 0xF7,     # Bitwise XOR (new)
            'not': 0xF7,     # Bitwise NOT (new, same opcode as xor, differentiated by funct3)
            'ebreak': 0x88,   # Environment Break
            'addi': 0xA9,    # Add immediate
            'rol': 0xAA,     # Rotate left immediate
            'muli': 0xAB,    # Multiply by immediate (for mul mix step)
            'modi': 0xAC     # Modular reduce immediate (for modulo prime)
        }
        
        # Codigos funct3 personalizados
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
            'xor': 0x3,
            'not': 0x4,
            'ebreak': 0x7,   # System break function
            'addi': 0x1,     # Add immediate function
            'rol': 0x3,
            'muli': 0x4,
            'modi': 0x5
        }
        
        # Codigos funct7 personalizados
        self.funct7 = {
            'add': 0x10,     # Addition extended function
            'sub': 0x20,     # Subtraction extended function
            'mul': 0x30,     # Multiplication extended function
            'and': 0x40,     # AND extended function
            'or': 0x50,     # OR extended function
            'xor': 0x60,    # XOR extended function
            'not': 0x70     # NOT extended function
        }

    def parse_register(self, reg_str):
        if not reg_str or reg_str[0] != 'x':
            raise ValueError(f"Invalid register format: {reg_str}")
        val = int(reg_str[1:])
        if not (0 <= val < 32):
            raise ValueError(f"Register out of range (0-31): {reg_str}")
        return val

    # Encoding helpers para 64 bits - Formato unificado
    # [63-56: opcode] [55-51: rd] [50-46: rs1] [45-41: rs2] [40-38: funct3] [37-31: funct7] [30-0: imm/unused]
    
    def encode_r64(self, funct7, rs2, rs1, funct3, rd, opcode):
        """Codifica instruccion R-type con formato unificado"""
        funct7 &= 0x7F
        rs2 &= 0x1F
        rs1 &= 0x1F
        funct3 &= 0x7
        rd &= 0x1F
        opcode &= 0xFF
        instr = (opcode << 56) | (rd << 51) | (rs1 << 46) | (rs2 << 41) | (funct3 << 38) | (funct7 << 31)
        return instr

    def encode_i64(self, imm, rs1, funct3, rd, opcode):
        """Codifica instruccion I-type con formato unificado (rs2=0 para I-type)"""
        imm &= 0x7FFFFFFF      # 31 bits para inmediato
        rs1 &= 0x1F
        funct3 &= 0x7
        rd &= 0x1F
        opcode &= 0xFF
        # rs2 = 0 para instrucciones I-type, funct7 = 0 para I-type
        instr = (opcode << 56) | (rd << 51) | (rs1 << 46) | (funct3 << 38) | imm
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
            if inst in ['add', 'sub', 'mul', 'and', 'or', 'xor', 'not']:
                # allow `not rd, rs1` (unary) as well as 3-operand R-type
                if inst == 'not':
                    if len(parts) < 3:
                        raise ValueError(f"[line {lineno}] Instruction {inst} missing operands.")
                    rd = self.parse_register(parts[1])
                    rs1 = self.parse_register(parts[2])
                    rs2 = 0
                else:
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
                try:
                    offset = int(offset_str, 0)
                except ValueError:
                    raise ValueError(f"[line {lineno}] Invalid lw offset: {offset_str}")
                instruction = self.encode_i64(offset, rs1, self.funct3['lw'], rd, self.opcodes['lw'])

            # I-type immediate instructions: addi, rol, muli, modi
            elif inst in ['addi', 'rol', 'muli', 'modi']:
                # syntax: addi rd, rs1, imm
                if len(parts) < 4:
                    raise ValueError(f"[line {lineno}] Instruction {inst} missing operands.")
                rd = self.parse_register(parts[1])
                rs1 = self.parse_register(parts[2])
                # accept decimal or hex immediates (e.g. 123 or 0x7B)
                try:
                    imm = int(parts[3], 0)
                except ValueError:
                    raise ValueError(f"[line {lineno}] Invalid immediate value: {parts[3]}")
                f3 = self.funct3.get(inst, 0)
                opcode = self.opcodes.get(inst)
                instruction = self.encode_i64(imm, rs1, f3, rd, opcode)

            # J-type instruction: jal rd, imm
            elif inst == 'jal':
                if len(parts) < 3:
                    raise ValueError(f"[line {lineno}] Instruction {inst} missing operands.")
                rd = self.parse_register(parts[1])
                try:
                    imm = int(parts[2], 0)
                except ValueError:
                    raise ValueError(f"[line {lineno}] Invalid immediate value: {parts[2]}")
                f3 = self.funct3.get(inst, 0)
                opcode = self.opcodes.get(inst)
                # Use I-type encoding for JAL (immediate in lower 31 bits)
                instruction = self.encode_i64(imm, 0, f3, rd, opcode)

            # B-type instruction: beq rs1, rs2, imm
            elif inst == 'beq':
                if len(parts) < 4:
                    raise ValueError(f"[line {lineno}] Instruction {inst} missing operands.")
                rs1 = self.parse_register(parts[1])
                rs2 = self.parse_register(parts[2])
                try:
                    imm = int(parts[3], 0)
                except ValueError:
                    raise ValueError(f"[line {lineno}] Invalid immediate value: {parts[3]}")
                f3 = self.funct3.get(inst, 0)
                opcode = self.opcodes.get(inst)
                # Use R-type encoding with immediate in funct7 field and lower bits
                # Store imm in bits [30-0], use rd=0 for branch instructions
                instruction = self.encode_r64(0, rs2, rs1, f3, 0, opcode) | (imm & 0x7FFFFFFF)

            else:
                raise ValueError(f"[line {lineno}] Unknown instruction: {inst}")

            program.append(instruction & 0xFFFFFFFFFFFFFFFF)  # asegurar 64 bits

        return program

