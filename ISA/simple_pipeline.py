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
        
        # ToyMDMA constants
        self.GOLDEN = 0x9e3779b97f4a7c15
        self.PRIME = 0xFFFFFFFB

    def load_program(self, program):
        for i, instr in enumerate(program):
            self.memory[i*8:(i+1)*8] = instr.to_bytes(8, 'little')
        self.pc = 0
        # Marcar el final del programa con una instruccion especial (NOP)
        end_addr = len(program) * 8
        if end_addr < len(self.memory):
            self.memory[end_addr:end_addr+8] = (0).to_bytes(8, 'little')

    def is_pipeline_active(self):
        # Verificar si hay actividad en el pipeline y que el PC no haya llegado al final
        has_valid_stages = self.IF_ID.valid or self.ID_EX.valid or self.EX_MEM.valid or self.MEM_WB.valid
        pc_in_bounds = self.pc < len(self.memory)
        
        # Verificar si encontramos una instruccion NOP (0x0) que indica fin del programa
        if pc_in_bounds and self.pc < len(self.memory) - 8:
            current_instr = int.from_bytes(self.memory[self.pc:self.pc+8], 'little')
            if current_instr == 0:  # NOP indica fin del programa
                return has_valid_stages  # Solo continuar si hay etapas validas
        
        return has_valid_stages or pc_in_bounds

    # -------------------------
    # Pipeline stages
    # -------------------------
    def IF_stage(self):
        if self.pc < len(self.memory) - 8:  # Asegurar que no leamos fuera de memoria
            current_instr = int.from_bytes(self.memory[self.pc:self.pc+8], 'little')
            
            # Si encontramos una instruccion NOP (0x0), detener el fetch
            if current_instr == 0:
                return
                
            self.IF_ID.instruction = current_instr
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
        
        # Nuevo formato unificado de 64 bits:
        # [63-56: opcode] [55-51: rd] [50-46: rs1] [45-41: rs2] [40-38: funct3] [37-31: funct7] [30-0: imm/unused]
        self.ID_EX.opcode = (instr >> 56) & 0xFF
        self.ID_EX.rd = (instr >> 51) & 0x1F
        self.ID_EX.rs1 = (instr >> 46) & 0x1F
        self.ID_EX.rs2 = (instr >> 41) & 0x1F
        self.ID_EX.funct3 = (instr >> 38) & 0x7
        self.ID_EX.funct7 = (instr >> 31) & 0x7F
        self.ID_EX.imm = instr & 0x7FFFFFFF  # 31 bits para inmediato

        self.ID_EX.valid = True
        self.ID_EX.stage = "ID"
        self.IF_ID.valid = False

    def EX_stage(self):
        if not self.ID_EX.valid:
            return

        op = self.ID_EX.opcode
        
        # Validar acceso a registros para evitar index out of range
        if self.ID_EX.rs1 >= len(self.registers):
            self.ID_EX.rs1 = 0
        if self.ID_EX.rs2 >= len(self.registers):
            self.ID_EX.rs2 = 0
            
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
        # I-type sw con nuevo opcode
        elif op == 0xB2:  # sw
            alu_result = rs1_val + self.ID_EX.imm
        # I-type addi (add immediate)
        elif op == 0xA9:  # addi rd, rs1, imm
            alu_result = (rs1_val + self.ID_EX.imm) & 0xFFFFFFFFFFFFFFFF
        # J-type jal con nuevo opcode
        elif op == 0xD4:  # jal rd, imm
            # Store return address (PC + 4) in rd, jump to PC + imm
            alu_result = self.ID_EX.pc + 8  # Return address (next instruction)
            # Jump to target address
            jump_target = self.ID_EX.pc + self.ID_EX.imm
            self.pc = jump_target
            # Invalidate pipeline stages after this instruction
            self.IF_ID.valid = False
        # B-type beq con nuevo opcode  
        elif op == 0xE5:  # beq rs1, rs2, imm
            # Branch if rs1 == rs2
            if rs1_val == rs2_val:
                # Take branch
                branch_target = self.ID_EX.pc + self.ID_EX.imm
                self.pc = branch_target
                # Invalidate pipeline stages after this instruction
                self.IF_ID.valid = False
            # ALU result not used for branch instructions
            alu_result = 0

<<<<<<< Updated upstream
=======
        # Instrucciones especiales de bóveda (Vault)
        elif op == 0x90:  # vwr rd, imm  -> escribe llave privada
            index = self.ID_EX.rd & 0x3     # índice de 0–3
            value = self.ID_EX.imm & 0xFFFFFFFFFFFFFFFF
            self.vault.write_key(index, value)
            alu_result = 0  # sin retorno

        elif op == 0x91:  # vinit rd, imm -> inicializa valor de hash
            index = self.ID_EX.rd & 0x3
            value = self.ID_EX.imm & 0xFFFFFFFFFFFFFFFF
            self.vault.write_init(index, value)
            alu_result = 0

        elif op == 0x92:  # vsign rd, rs1, rs2
            # Debug: show value of address register before signature
            print(f"[DEBUG EX_stage vsign] rs2 (x{self.ID_EX.rs2}) value: 0x{self.registers[self.ID_EX.rs2]:X}")
            alu_result = self.registers[self.ID_EX.rs2]

        elif op == 0x88:  # ebreak - Environment Break
            # Detener el pipeline estableciendo PC fuera de rango
            self.pc = len(self.memory)
            alu_result = 0

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            self.MEM_WB.alu_result = int.from_bytes(self.memory[addr:addr+8], 'little')
=======
            # Validar acceso a memoria
            if addr + 8 <= len(self.memory):
                self.MEM_WB.alu_result = int.from_bytes(self.memory[addr:addr+8], 'little')
            else:
                self.MEM_WB.alu_result = 0  # Valor por defecto si fuera de rango
        elif op == 0xB2:  # sw con nuevo opcode personalizado
            addr = self.EX_MEM.alu_result
            # Validar acceso a registros y memoria
            if self.EX_MEM.rs2 < len(self.registers) and addr + 8 <= len(self.memory):
                data = self.registers[self.EX_MEM.rs2]  # Datos a almacenar
                self.memory[addr:addr+8] = data.to_bytes(8, 'little')
            self.MEM_WB.alu_result = 0

        # Instrucciones de bóveda
        elif op == 0x90:  # vwr rd, imm
            key_index = self.EX_MEM.rd & 0x3  # Limitar a 0-3
            value = self.EX_MEM.imm
            self.vault.write_key(key_index, value)
            self.MEM_WB.alu_result = 0
        elif op == 0x91:  # vinit rd, imm
            key_index = self.EX_MEM.rd & 0x3  # Limitar a 0-3
            value = self.EX_MEM.imm
            self.vault.write_init(key_index, value)
            self.MEM_WB.alu_result = 0
        elif op == 0x92:  # vsign idx, addr
            addr = self.EX_MEM.alu_result
            key_idx = self.EX_MEM.rs1
            
            # Validar que la dirección y el índice de clave estén en rango
            if addr + 32 > len(self.memory):  # 4 bloques * 8 bytes = 32 bytes
                print(f"[ERROR] vsign: memoria fuera de rango addr=0x{addr:X}")
                self.MEM_WB.alu_result = 0
            elif not hasattr(self.vault, 'keys') or key_idx >= len(self.vault.keys):
                print(f"[ERROR] vsign: clave fuera de rango key_idx={key_idx}")
                self.MEM_WB.alu_result = 0
            else:
                # Leer 4 bloques de 8 bytes
                blocks = [
                    int.from_bytes(self.memory[addr + i*8 : addr + (i+1)*8], 'little')
                    for i in range(4)
                ]
                print(f"[DEBUG vsign] addr: 0x{addr:X}")
                print(f"[DEBUG vsign] blocks: {[hex(b) for b in blocks]}")
                print(f"[DEBUG vsign] key_idx: {key_idx}")
                if hasattr(self.vault, 'keys'):
                    print(f"[DEBUG vsign] vault key: 0x{self.vault.keys[key_idx]:016X}")
                if hasattr(self.vault, 'inits'):
                    print(f"[DEBUG vsign] vault inits: {[hex(v) for v in self.vault.inits]}")
            # Calcular firma con la bóveda
            S = self.vault.sign_block(key_idx, blocks)
            print(f"[DEBUG vsign] signature: {[hex(s) for s in S]}")
            # Escribir firma después del mensaje
            for i, val in enumerate(S):
                pos = addr + 4*8 + i*8
                self.memory[pos:pos+8] = val.to_bytes(8, 'little')
            self.MEM_WB.alu_result = 1  # éxito

>>>>>>> Stashed changes
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

        if self.MEM_WB.rd != 0 and self.MEM_WB.rd < len(self.registers):  # x0 nunca cambia y validar rango
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

        self.cycle += 1
    
    # -------------------------
    # Procesador Universal ISA
    # -------------------------
    
    def reset_processor(self):
        """Reiniciar el procesador a estado inicial"""
        self.memory = bytearray(4096)
        self.registers = [0] * 32
        self.pc = 0
        self.cycle = 0
        
        # Limpiar pipeline
        self.IF_ID = PipelinedRegister()
        self.ID_EX = PipelinedRegister()
        self.EX_MEM = PipelinedRegister()
        self.MEM_WB = PipelinedRegister()
        
        # Reiniciar estadisticas
        self.execution_stats = {
            'cycles': 0,
            'instructions_executed': 0,
            'branches_taken': 0,
            'pipeline_stalls': 0
        }
    
    def execute_assembly_code(self, assembly_code, initial_registers=None, trace=False):
        """
        Ejecutar codigo assembly directamente
        
        Args:
            assembly_code: String con codigo assembly
            initial_registers: Dict con valores iniciales {reg_num: valor}
            trace: Mostrar traza de ejecucion
            
        Returns:
            dict: Estado final del procesador
        """
        # Reiniciar procesador
        self.reset_processor()
        self.trace = trace
        
        try:
            # Compilar assembly
            instructions = self.assembler.assemble(assembly_code)
            
            # Cargar programa
            self.load_program(instructions)
            
            # Establecer registros iniciales
            if initial_registers:
                for reg_num, value in initial_registers.items():
                    if 0 <= reg_num < 32:
                        self.registers[reg_num] = value & 0xFFFFFFFFFFFFFFFF
            
            # Ejecutar programa
            cycles_executed = self.run_program()
            
            # Preparar resultados
            result = {
                'success': True,
                'cycles': cycles_executed,
                'registers': {f'x{i}': self.registers[i] for i in range(32) if self.registers[i] != 0},
                'pc_final': self.pc,
                'memory_used': len([b for b in self.memory if b != 0]),
                'stats': self.execution_stats.copy()
            }
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'cycles': self.cycle,
                'registers': {f'x{i}': self.registers[i] for i in range(32) if self.registers[i] != 0}
            }
    
    def run_program(self, max_cycles=10000):
        """
        Ejecutar programa cargado hasta completarse
        
        Args:
            max_cycles: Limite de ciclos para evitar bucles infinitos
            
        Returns:
            int: Numero de ciclos ejecutados
        """
        start_cycle = self.cycle
        
        while self.is_pipeline_active() and (self.cycle - start_cycle) < max_cycles:            
            self.step()
            
            # Actualizar estadisticas
            if self.MEM_WB.valid:
                self.execution_stats['instructions_executed'] += 1
        
        self.execution_stats['cycles'] = self.cycle - start_cycle
        
        if (self.cycle - start_cycle) >= max_cycles:
            raise RuntimeError(f"Programa excedio {max_cycles} ciclos - posible bucle infinito")
        
        return self.cycle - start_cycle

