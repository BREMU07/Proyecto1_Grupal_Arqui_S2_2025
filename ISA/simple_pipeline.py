# simple_pipeline.py
class PipelinedRegister:
    def __init__(self):
        self.instruction = 0
        self.pc = 0
        self.valid = False
        self.rd = 0
        self.rs1 = 0
        self.rs2 = 0
        self.funct3 = 0
        self.funct7 = 0
        self.imm = 0
        self.opcode = 0
        self.alu_result = 0
        self.stage = ""

class Simple_Pipeline:
    def __init__(self, trace=False):
        self.memory = bytearray(1024)  # 1KB
        self.registers = [0] * 32
        self.pc = 0
        self.cycle = 0
        self.trace = trace

        # Pipeline registers
        self.IF_ID = PipelinedRegister()
        self.ID_EX = PipelinedRegister()
        self.EX_MEM = PipelinedRegister()
        self.MEM_WB = PipelinedRegister()

    def load_program(self, program):
        for i, instr in enumerate(program):
            self.memory[i*8:(i+1)*8] = instr.to_bytes(8, 'little')
        self.pc = 0

    def is_pipeline_active(self):
        return self.IF_ID.valid or self.ID_EX.valid or self.EX_MEM.valid or self.MEM_WB.valid or self.pc < len(self.memory)

    # -------------------------
    # Pipeline stages
    # -------------------------
    def IF_stage(self):
        if self.pc < len(self.memory):
            self.IF_ID.instruction = int.from_bytes(self.memory[self.pc:self.pc+8], 'little')
            self.IF_ID.pc = self.pc
            self.IF_ID.valid = True
            self.IF_ID.stage = "IF"
            self.pc += 8

    def ID_stage(self):
        if not self.IF_ID.valid:
            return

        instr = self.IF_ID.instruction
        self.ID_EX.instruction = instr
        self.ID_EX.pc = self.IF_ID.pc
        self.ID_EX.opcode = (instr >> 31) & 0xFF
        self.ID_EX.rd = (instr >> 39) & 0x1F
        self.ID_EX.rs1 = (instr >> 47) & 0x1F
        self.ID_EX.rs2 = (instr >> 52) & 0x1F
        self.ID_EX.funct3 = (instr >> 44) & 0x7
        self.ID_EX.funct7 = (instr >> 57) & 0x7F

        # Inmediato para I-type (lw) - Nuevo opcode personalizado
        if self.ID_EX.opcode == 0xA1:  # lw con nuevo opcode
            self.ID_EX.imm = (instr >> 28) & 0xFFFFFFFFF
        # Inmediatos para nuevas instrucciones I-type: rol(0xAA), muli(0xAB), modi(0xAC)
        elif self.ID_EX.opcode in (0xAA, 0xAB, 0xAC):
            self.ID_EX.imm = (instr >> 28) & 0xFFFFFFFFF

        self.ID_EX.valid = True
        self.ID_EX.stage = "ID"
        self.IF_ID.valid = False

    def EX_stage(self):
        if not self.ID_EX.valid:
            return

        op = self.ID_EX.opcode
        rs1_val = self.registers[self.ID_EX.rs1]
        rs2_val = self.registers[self.ID_EX.rs2]

        alu_result = 0
        # R-type con nuevos opcodes personalizados
        if op == 0xC3:  # add/sub/mul con nuevo opcode
            if self.ID_EX.funct3 == 0x1 and self.ID_EX.funct7 == 0x10:   # add
                alu_result = (rs1_val + rs2_val) & 0xFFFFFFFFFFFFFFFF
            elif self.ID_EX.funct3 == 0x2 and self.ID_EX.funct7 == 0x20: # sub
                alu_result = (rs1_val - rs2_val) & 0xFFFFFFFFFFFFFFFF
            elif self.ID_EX.funct3 == 0x3 and self.ID_EX.funct7 == 0x30: # mul
                alu_result = (rs1_val * rs2_val) & 0xFFFFFFFFFFFFFFFF
        elif op == 0xF6:  # and/or con nuevo opcode
            if self.ID_EX.funct3 == 0x1 and self.ID_EX.funct7 == 0x40: # and
                alu_result = rs1_val & rs2_val
            elif self.ID_EX.funct3 == 0x2 and self.ID_EX.funct7 == 0x50: # or
                alu_result = rs1_val | rs2_val
        elif op == 0xF7:  # xor/not custom opcode
            if self.ID_EX.funct3 == 0x3 and self.ID_EX.funct7 == 0x60:  # xor
                alu_result = rs1_val ^ rs2_val
            elif self.ID_EX.funct3 == 0x4 and self.ID_EX.funct7 == 0x70:  # not (unary on rs1)
                alu_result = (~rs1_val) & 0xFFFFFFFFFFFFFFFF
        # I-type custom toy instructions
        elif op == 0xAA:  # rol rd, rs1, imm
            # rotate left 64-bit
            r = self.ID_EX.imm & 0x3F
            val = (rs1_val & 0xFFFFFFFFFFFFFFFF)
            alu_result = ((val << r) | (val >> (64 - r))) & 0xFFFFFFFFFFFFFFFF
        elif op == 0xAB:  # muli rd, rs1, imm
            imm = self.ID_EX.imm & 0xFFFFFFFFFFFFFFFF
            alu_result = (rs1_val * imm) & 0xFFFFFFFFFFFFFFFF
        elif op == 0xAC:  # modi rd, rs1, imm
            imm = self.ID_EX.imm & 0xFFFFFFFFFFFFFFFF
            if imm == 0:
                alu_result = 0
            else:
                alu_result = rs1_val % imm
        # I-type lw con nuevo opcode
        elif op == 0xA1:  # lw
            alu_result = rs1_val + self.ID_EX.imm

        # ensure 64-bit wraparound for any result
        alu_result &= 0xFFFFFFFFFFFFFFFF

        if self.trace:
            try:
                f7 = self.ID_EX.funct7
                f3 = self.ID_EX.funct3
            except Exception:
                f7 = 0
                f3 = 0
            print(f"EX: pc={self.ID_EX.pc} opcode=0x{op:02X} f7=0x{f7:02X} f3=0x{f3:01X} rd=x{self.ID_EX.rd} rs1=x{self.ID_EX.rs1} rs2=x{self.ID_EX.rs2} imm=0x{self.ID_EX.imm:X} rs1_val=0x{rs1_val:016X} rs2_val=0x{rs2_val:016X} -> alu=0x{alu_result:016X}")

        self.EX_MEM.alu_result = alu_result
        self.EX_MEM.rd = self.ID_EX.rd
        self.EX_MEM.opcode = self.ID_EX.opcode
        self.EX_MEM.rs2 = self.ID_EX.rs2
        self.EX_MEM.valid = True
        self.EX_MEM.stage = "EX"
        self.ID_EX.valid = False

    def MEM_stage(self):
        if not self.EX_MEM.valid:
            return

        op = self.EX_MEM.opcode
        if op == 0xA1:  # lw con nuevo opcode personalizado
            addr = self.EX_MEM.alu_result
            self.MEM_WB.alu_result = int.from_bytes(self.memory[addr:addr+8], 'little')
        else:  # R-type (opcodes 0xC3 y 0xF6)
            self.MEM_WB.alu_result = self.EX_MEM.alu_result

        self.MEM_WB.rd = self.EX_MEM.rd
        self.MEM_WB.opcode = op
        self.MEM_WB.valid = True
        self.MEM_WB.stage = "MEM"
        self.EX_MEM.valid = False

    def WB_stage(self):
        if not self.MEM_WB.valid:
            return

        if self.MEM_WB.rd != 0:  # x0 nunca cambia
            self.registers[self.MEM_WB.rd] = self.MEM_WB.alu_result

        self.MEM_WB.valid = False
        self.MEM_WB.stage = "WB"

    # -------------------------
    # Ejecutar un ciclo
    # -------------------------
    def step(self):
        self.WB_stage()
        self.MEM_stage()
        self.EX_stage()
        self.ID_stage()
        self.IF_stage()
