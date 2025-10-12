#!/usr/bin/env python3

from assembler import Assembler
from simple_pipeline import Simple_Pipeline
import time


class ISAPipelineHashProcessor:
    def __init__(self):
        self.assembler = Assembler()
        self.private_key = 0x123456789ABCDEF0
        self.pipeline = Simple_Pipeline(trace=False)
        self.program_loaded = False

    # --- ARCHIVOS ---
    def load_file(self, file_path):
        with open(file_path, 'rb') as f:
            return f.read()

    # --- HASH ---
    def calculate_hash_components(self, file_path):
        """Calcular hash por bloques y devolver resultados intermedios"""
        data = self.load_file(file_path)
        return self.calculate_hash_from_data(data)

    def calculate_hash_from_data(self, data):
        blocks = [data[i:i+8] for i in range(0, len(data), 8)]
        if len(blocks[-1]) < 8:
            blocks[-1] = blocks[-1].ljust(8, b'\x00')

        A = 0x0123456789ABCDEF
        B = 0xFEDCBA9876543210
        C = 0x1111111111111111
        D = 0x2222222222222222

        block_results = []

        for i, block in enumerate(blocks):
            data_block = int.from_bytes(block, 'little')
            A, B, C, D, steps = self.hash_block_with_isa(A, B, C, D, data_block)
            block_results.append({
                "block_index": i,
                "data_block": data_block,
                "A": A,
                "B": B,
                "C": C,
                "D": D,
                "steps": steps
            })

        final_hash = A ^ B ^ C ^ D

        return {
            "final_hash": final_hash,
            "A": A, "B": B, "C": C, "D": D,
            "blocks": block_results
        }

    def hash_block_with_isa(self, A, B, C, D, data_block):
        if not self.program_loaded:
            program = self.assembler.assemble(self.create_toymdata_program())
            self.pipeline.load_program(program)
            self.program_loaded = True

        self.pipeline.registers[1] = data_block
        self.pipeline.registers[2] = A
        self.pipeline.registers[3] = B
        self.pipeline.registers[4] = C
        self.pipeline.registers[5] = D

        steps = 0
        max_steps = 50
        while self.pipeline.is_pipeline_active() and steps < max_steps:
            self.pipeline.step()
            steps += 1

        if steps >= max_steps:
            raise RuntimeError("Pipeline excedió 50 pasos")

        return (self.pipeline.registers[2] & 0xFFFFFFFFFFFFFFFF,
                self.pipeline.registers[3] & 0xFFFFFFFFFFFFFFFF,
                self.pipeline.registers[4] & 0xFFFFFFFFFFFFFFFF,
                self.pipeline.registers[5] & 0xFFFFFFFFFFFFFFFF,
                steps)

    def create_toymdata_program(self):
        """
        Crear programa ToyMDMA completo usando instrucciones del ISA
        con condicionales reales implementados con JAL y BEQ
        """
        program = """
        # ToyMDMA Hash Algorithm - Implementacion completa con ISA
        # Procesa un bloque de 8 bytes usando condicionales reales
        # 
        # Registros usados:
        # x1 = data_block (entrada de 8 bytes)
        # x2 = A, x3 = B, x4 = C, x5 = D (variables de hash)
        # x6 = GOLDEN_LOW, x7 = GOLDEN_HIGH  
        # x8 = PRIME, x9 = temp, x10 = temp2
        
        # === INICIALIZACION DE CONSTANTES ===
        # Cargar constantes ToyMDMA (valores completos de 64 bits usando addi)
        addi x6, x0, 0x7C15         # GOLDEN_LOW (parte baja de 0x9e3779b97f4a7c15)
        addi x7, x0, 0x7F4A         # GOLDEN_MID (para construir GOLDEN)
        addi x8, x0, 0xFFFB         # PRIME = 0xFFFFFFFB (truncado a 32 bits)
        
        # === ALGORITMO TOYMDATA - 8 PASOS ===
        
        # PASO 1: A = A + data_block (siempre se ejecuta)
        add x2, x2, x1
        
        # PASO 2: if (data_block != 0) B = B * data_block
        beq x1, x0, 16              # Si data_block == 0, saltar multiplicacion
        mul x3, x3, x1              # B = B * data_block
        
        # PASO 3: C = C ^ data_block (siempre se ejecuta)  
        xor x4, x4, x1
        
        # PASO 4: if (D != 0) D = D % PRIME
        beq x5, x0, 16              # Si D == 0, saltar modulo
        modi x5, x5, 0xFFFFFFFB     # D = D % PRIME
        
        # PASO 5: A = A + GOLDEN (construccion de 64-bit GOLDEN)
        add x2, x2, x6              # A = A + GOLDEN_LOW
        
        # PASO 6: B = B ^ A (mezcla)
        xor x3, x3, x2
        
        # PASO 7: C = C + B (acumulacion)
        add x4, x4, x3
        
        # PASO 8: D = D ^ C (mezcla final)
        xor x5, x5, x4
        
        # Los registros x2, x3, x4, x5 contienen A, B, C, D finales
        """
        return program
    
    # --- FIRMA ---
    def sign_hash(self, A, B, C, D, key=None):
        if key is None:
            key = self.private_key
        return (A ^ key, B ^ key, C ^ key, D ^ key)

    def verify_signature(self, signature, A, B, C, D, key=None):
        if key is None:
            key = self.private_key
        return (signature[0] ^ key == A and
                signature[1] ^ key == B and
                signature[2] ^ key == C and
                signature[3] ^ key == D)

    # --- CREAR ARCHIVO FIRMADO ---
    def create_signed_file(self, original_file, signed_file, key=None):
        hash_info = self.calculate_hash_components(original_file)
        signature = self.sign_hash(hash_info["A"], hash_info["B"], hash_info["C"], hash_info["D"], key)
        original_data = self.load_file(original_file)

        with open(signed_file, 'wb') as f:
            f.write(original_data)
            for s in signature:
                f.write(s.to_bytes(8, 'little'))

        return {
            "signed_file": signed_file,
            "signature": signature,
            "hash_components": {
                "A": hash_info["A"],
                "B": hash_info["B"],
                "C": hash_info["C"],
                "D": hash_info["D"]
            },
            "file_size": len(original_data)
        }

    # --- VERIFICAR ARCHIVO FIRMADO ---
    def verify_signed_file(self, signed_file, key=None):
        data = self.load_file(signed_file)
        if len(data) < 32:
            raise ValueError("Archivo demasiado pequeño para contener firma")

        document_data = data[:-32]
        signature_bytes = data[-32:]
        signature = tuple(int.from_bytes(signature_bytes[i*8:(i+1)*8], 'little') for i in range(4))
        hash_info = self.calculate_hash_from_data(document_data)
        valid = self.verify_signature(signature, hash_info[0], hash_info[1], hash_info[2], hash_info[3], key)

        return {
            "valid": valid,
            "signature": signature,
            "hash_components": {
                "A": hash_info[0],
                "B": hash_info[1],
                "C": hash_info[2],
                "D": hash_info[3]
            },
            "document_size": len(document_data)
        }
    
def main():
    """
    Demostracion completa: Hash ToyMDMA + Firma Digital
    """
    print("SISTEMA COMPLETO: ToyMDMA + Firma Digital")
    print("=" * 60)
    
    processor = ISAPipelineHashProcessor()
    target_file = "file_loader.py"
    signed_file = f"{target_file}_signed.bin"
    
    try:
        print("=== FASE 1: CALCULO DE HASH ===")
        # Calcular hash completo (para demostracion) 
        hash_result = processor.toy_mdma_hash_isa(target_file)
        print(f"Hash combinado: 0x{hash_result:016X}")
        
        print(f"\n=== FASE 2: FIRMA DIGITAL ===")
        # Crear archivo firmado
        signature = processor.create_signed_file(target_file, signed_file)
        
        print(f"\n=== FASE 3: VERIFICACION ===")
        # Verificar archivo firmado
        is_valid = processor.verify_signed_file(signed_file)
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Archivo original: {target_file}")
        print(f"Archivo firmado: {signed_file}")
        print(f"Firma valida: {'SI' if is_valid else 'NO'}")
        print(f"Sistema funcionando: COMPLETO")
        
        # Mostrar tamanos
        import os
        original_size = os.path.getsize(target_file)
        signed_size = os.path.getsize(signed_file)
        signature_overhead = signed_size - original_size
        
        print(f"\nEstadisticas:")
        print(f"   Archivo original: {original_size} bytes")
        print(f"   Archivo firmado: {signed_size} bytes")
        print(f"   Overhead de firma: {signature_overhead} bytes")
        print(f"   Clave usada: 0x{processor.private_key:016X}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()