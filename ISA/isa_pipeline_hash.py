#!/usr/bin/env python3

from assembler import Assembler
from simple_pipeline import Simple_Pipeline
import os


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
        data = self.load_file(file_path)
        return self.calculate_hash_from_data(data)

    def calculate_hash_from_data(self, data):
        # --- REINICIAR PIPELINE PARA VERIFICACION LIMPIA ---
        self.program_loaded = False
        self.pipeline = Simple_Pipeline(trace=False)

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
                "A": A, "B": B, "C": C, "D": D,
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
        # ToyMDMA completo (igual que antes)
        program = """
        # ToyMDMA Hash Algorithm
        addi x6, x0, 0x7C15
        addi x7, x0, 0x7F4A
        addi x8, x0, 0xFFFB
        add x2, x2, x1
        beq x1, x0, 16
        mul x3, x3, x1
        xor x4, x4, x1
        beq x5, x0, 16
        modi x5, x5, 0xFFFFFFFB
        add x2, x2, x6
        xor x3, x3, x2
        add x4, x4, x3
        xor x5, x5, x4
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
            "hash_components": {"A": hash_info["A"], "B": hash_info["B"], "C": hash_info["C"], "D": hash_info["D"]},
            "file_size": len(original_data)
        }

    # --- VERIFICAR ARCHIVO FIRMADO ---
    def verify_signed_file(self, signed_file, key=None):
        with open(signed_file, 'rb') as f:
            data = f.read()

        if len(data) < 32:
            raise ValueError("Archivo demasiado pequeno para contener firma")

        document_data = data[:-32]
        signature_data = data[-32:]

        signature = []
        for i in range(4):
            sig_bytes = signature_data[i*8:(i+1)*8]
            sig_component = int.from_bytes(sig_bytes, 'little')
            signature.append(sig_component)
        signature = tuple(signature)

        # --- REINICIAR PIPELINE PARA VERIFICACION LIMPIA ---
        hash_result = self.calculate_hash_from_data(document_data)
        A = hash_result["A"]
        B = hash_result["B"]
        C = hash_result["C"]
        D = hash_result["D"]

        is_valid = self.verify_signature(signature, A, B, C, D, key)

        return {
            "valid": is_valid,
            "signature": signature,
            "hash_components": {"A": A, "B": B, "C": C, "D": D},
            "document_size": len(document_data)
        }


def main():
    processor = ISAPipelineHashProcessor()
    target_file = "file_loader.py"
    signed_file = f"{target_file}_signed.bin"

    print("=== FASE 1: CALCULO DE HASH ===")
    hash_result = processor.calculate_hash_components(target_file)
    print(f"Hash final: 0x{hash_result['final_hash']:016X}")

    print("=== FASE 2: CREAR ARCHIVO FIRMADO ===")
    signature_info = processor.create_signed_file(target_file, signed_file)
    print(f"Archivo firmado: {signed_file}")
    print(f"Firma: {signature_info['signature']}")

    print("=== FASE 3: VERIFICAR ===")
    verify_info = processor.verify_signed_file(signed_file)
    print(f"Verificación: {'VÁLIDA' if verify_info['valid'] else 'INVÁLIDA'}")
    print(f"Componentes hash: {verify_info['hash_components']}")


if __name__ == "__main__":
    main()
