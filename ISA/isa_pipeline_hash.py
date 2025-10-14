#!/usr/bin/env python3

from assembler import Assembler
from simple_pipeline import Simple_Pipeline
from vault import Vault
import time
import os


class ISAPipelineHashProcessor:
    def __init__(self):
        self.assembler = Assembler()
        # default local private key (fallback). If a Vault is attached, prefer Vault keys.
        self.private_key = 0x123456789ABCDEF0
        self.pipeline = Simple_Pipeline(trace=False)
        self.program_loaded = False

    def _resolve_key(self, key):

        if isinstance(key, int):
            return key & 0xFFFFFFFFFFFFFFFF

        # request from vault
        if isinstance(key, dict) and key.get('use_vault', False):
            vault_index = key.get('vault_index', 0)
            if hasattr(self.pipeline, 'vault') and self.pipeline.vault is not None:
                v = self.pipeline.vault
            else:
                v = Vault()
                # attach to pipeline for future calls
                try:
                    self.pipeline.vault = v
                except Exception:
                    pass
            try:
                return int(v.keys[vault_index]) & 0xFFFFFFFFFFFFFFFF
            except Exception:
                return 0

        # no key provided: prefer pipeline vault if present
        if key is None:
            if hasattr(self.pipeline, 'vault') and self.pipeline.vault is not None:
                try:
                    return int(self.pipeline.vault.keys[0]) & 0xFFFFFFFFFFFFFFFF
                except Exception:
                    return self.private_key
            return self.private_key

        return self.private_key

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
        k = self._resolve_key(key)
        return (A ^ k, B ^ k, C ^ k, D ^ k)

    def sign_hash_with_vault(self, A, B, C, D, key_idx=0):
        """
        Usa la boveda del pipeline para firmar los 4 componentes del hash.
        Esto no expone la llave privada: se pide a la boveda que compute la firma
        (la boveda aplica XOR internamente con la llave almacenada).
        """
        # Prepare components
        components = [A & 0xFFFFFFFFFFFFFFFF, B & 0xFFFFFFFFFFFFFFFF,
                      C & 0xFFFFFFFFFFFFFFFF, D & 0xFFFFFFFFFFFFFFFF]
        # Ensure pipeline has a vault instance and attach it so signing and later verification
        # can reuse the same vault instance (avoid ephemeral vaults that lose keys).
        if not hasattr(self.pipeline, 'vault') or self.pipeline.vault is None:
            v = Vault()
            try:
                self.pipeline.vault = v
            except Exception:
                pass
        else:
            v = self.pipeline.vault
        # Use sign_components to XOR components with the key (no extra hashing)
        return tuple(v.sign_components(key_idx, components))

    def invert_signature(self, signature, key=None):
        """
        Dada una firma y la llave, recuperar los componentes A,B,C,D originales
        (como firma = componentes XOR llave, invertir es XOR con la misma llave).
        Si key es None se usa private_key del procesador.
        """
        k = self._resolve_key(key)
        return (signature[0] ^ k, signature[1] ^ k, signature[2] ^ k, signature[3] ^ k)

    def verify_signature(self, signature, A, B, C, D, key=None):
        k = self._resolve_key(key)
        return (signature[0] ^ k == A and
                signature[1] ^ k == B and
                signature[2] ^ k == C and
                signature[3] ^ k == D)

    # --- CREAR ARCHIVO FIRMADO ---
    def create_signed_file(self, original_file, signed_file, key=None):
        # By default sign with local private_key. If key is a dict with
        # {'use_vault': True, 'vault_index': n} then request signature from the vault.
        hash_info = self.calculate_hash_components(original_file)
        use_vault = False
        vault_index = 0
        if isinstance(key, dict):
            use_vault = key.get('use_vault', False)
            vault_index = key.get('vault_index', 0)

        # If no key specified but a Vault is attached to the pipeline, prefer using the Vault
        if key is None and hasattr(self.pipeline, 'vault') and self.pipeline.vault is not None:
            use_vault = True
            vault_index = 0

        if use_vault:
            signature = self.sign_hash_with_vault(hash_info["A"], hash_info["B"], hash_info["C"], hash_info["D"], vault_index)
            private_key_used = None
        else:
            signature = self.sign_hash(hash_info["A"], hash_info["B"], hash_info["C"], hash_info["D"], key)
            private_key_used = key if key is not None else self.private_key
        original_data = self.load_file(original_file)

        with open(signed_file, 'wb') as f:
            f.write(original_data)
            for s in signature:
                f.write(s.to_bytes(8, 'little'))

        return {
            "signed_file": signed_file,
            "signature": signature,
            "hash_components": {"A": hash_info["A"], "B": hash_info["B"], "C": hash_info["C"], "D": hash_info["D"]},
            "file_size": len(original_data),
            "private_key_used": private_key_used
        }

    # --- VERIFICAR ARCHIVO FIRMADO ---
    def verify_signed_file(self, signed_file, key=None):
        """
        Verifica un archivo firmado. Si `key` es un dict con {'use_vault': True, 'vault_index': n}
        la verificacion pedira a la boveda que produzca la firma esperada y la comparara.
        Si no, se usa la llave local (o proporcionada) para invertir la firma y comparar.
        """
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

        # Instead of recomputing the hash, run the reverse_hash.asm program on the pipeline
        # The reverse program will read the embedded signature placed in memory and recover A,B,C,D
        # Prepare pipeline and program
        rev_path = os.path.join(os.path.dirname(__file__), 'reverse_hash.asm')
        if not os.path.exists(rev_path):
            raise FileNotFoundError(f"reverse_hash.asm not found at {rev_path}")

        with open(rev_path, 'r', encoding='utf-8') as rf:
            rev_code = rf.read()

        # If caller didn't pass a key but the pipeline has a Vault attached,
        # prefer using the Vault for verification so the reverse program will
        # be provided with the correct key in memory.
        if key is None and hasattr(self.pipeline, 'vault') and self.pipeline.vault is not None:
            key = {'use_vault': True, 'vault_index': 0}

        # Assemble the reverse program and load into pipeline
        rev_program = self.assembler.assemble(rev_code)
        # reset pipeline but preserve any existing Vault instance so verification can use same keys
        existing_vault = None
        if hasattr(self.pipeline, 'vault') and self.pipeline.vault is not None:
            existing_vault = self.pipeline.vault
        self.program_loaded = False
        self.pipeline = Simple_Pipeline(trace=False)
        # restore existing vault onto the new pipeline if we had one
        if existing_vault is not None:
            try:
                self.pipeline.vault = existing_vault
            except Exception:
                pass
        self.pipeline.load_program(rev_program)

        # Load the signature into pipeline memory at base 0x400 (as reverse_hash.asm expects)
        base = 0x400
        # Ensure memory is large enough for base region (we need up to base+72)
        needed = base + 72
        if len(self.pipeline.memory) < needed:
            extra = needed - len(self.pipeline.memory)
            self.pipeline.memory += bytearray(b'\x00' * extra)

        # Note: don't write document_data at address 0 since program is loaded at 0
        # and writing the document would overwrite the reverse program. The reverse
        # program only needs the signature and the key placed at 'base'.

        # write signature into memory
        for i in range(4):
            self.pipeline.memory[base + i*8: base + (i+1)*8] = signature[i].to_bytes(8, 'little')

        # If verifying using the vault, ensure the pipeline has a vault instance
        # and write the vault's key into memory at base+64 (reverse_hash.asm will read it there).
        if isinstance(key, dict) and key.get('use_vault', False):
            vault_index = key.get('vault_index', 0)
            # attach or create vault on pipeline
            if not hasattr(self.pipeline, 'vault') or self.pipeline.vault is None:
                v = Vault()
                self.pipeline.vault = v
            else:
                v = self.pipeline.vault

            # Ensure pipeline memory is large enough to hold base+72 (we need up to base+71)
            needed = base + 72
            if len(self.pipeline.memory) < needed:
                # extend memory with zeros
                extra = needed - len(self.pipeline.memory)
                self.pipeline.memory += bytearray(b'\x00' * extra)

            # Vault stores keys internally in v.keys; read the key value and write little-endian
            try:
                key_val = v.keys[vault_index]
            except Exception:
                # If key index invalid, write zeros
                key_val = 0

            self.pipeline.memory[base + 64: base + 72] = int(key_val & 0xFFFFFFFFFFFFFFFF).to_bytes(8, 'little')

        # Ensure the reverse program sees the expected base register (x20)
        try:
            self.pipeline.registers[20] = base
        except Exception:
            pass

        # Run pipeline until it halts or reaches step limit
        steps = 0
        max_steps = 500
        while self.pipeline.is_pipeline_active() and steps < max_steps:
            self.pipeline.step()
            steps += 1
        if steps >= max_steps:
            raise RuntimeError('reverse_hash program exceeded step limit')

        # Read recovered components from memory (reverse_hash writes them at base+32..base+56)
        A = int.from_bytes(self.pipeline.memory[base + 32: base + 40], 'little')
        B = int.from_bytes(self.pipeline.memory[base + 40: base + 48], 'little')
        C = int.from_bytes(self.pipeline.memory[base + 48: base + 56], 'little')
        D = int.from_bytes(self.pipeline.memory[base + 56: base + 64], 'little')

        # If key is a dict and requests vault verification, ask the vault to produce expected signature
        if isinstance(key, dict) and key.get('use_vault', False):
            vault_index = key.get('vault_index', 0)
            # Ensure pipeline has a vault instance
            if not hasattr(self.pipeline, 'vault') or self.pipeline.vault is None:
                v = Vault()
            else:
                v = self.pipeline.vault
            # expected signature is simply XOR of components with key (use sign_components)
            expected_sig = tuple(v.sign_components(vault_index, [A, B, C, D]))
            is_valid = (expected_sig == signature)
            used_key = None
        else:
            # Use provided key or the processor's private key to invert signature
            used_key = key if key is not None else self.private_key
            recovered = self.invert_signature(signature, used_key)
            is_valid = (recovered[0] == A and recovered[1] == B and recovered[2] == C and recovered[3] == D)

        return {
            "valid": is_valid,
            "signature": signature,
            "hash_components": {"A": A, "B": B, "C": C, "D": D},
            "document_size": len(document_data),
            "vault_verification": isinstance(key, dict) and key.get('use_vault', False),
            "used_key": (None if isinstance(key, dict) and key.get('use_vault', False) else used_key)
        }


def main():
    processor = ISAPipelineHashProcessor()
    target_file = "file_loader.py"
    signed_file = f"{target_file}_signed.bin"
    # For demo purposes: attach a Vault and write a test key so the script
    # demonstrates signing/verifying using the boveda rather than the hardcoded key.
    v = Vault()
    demo_key = 0xFEEDC0FFEE123456
    v.write_key(0, demo_key)
    try:
        processor.pipeline.vault = v
    except Exception:
        pass

    print("=== FASE 1: CALCULO DE HASH ===")
    # If target_file does not exist, fall back to a small temp file
    if not os.path.exists(target_file):
        with open(target_file, 'wb') as f:
            f.write(b'demo')

    hash_result = processor.calculate_hash_components(target_file)
    print(f"Hash final: 0x{hash_result['final_hash']:016X}")

    print("=== FASE 2: CREAR ARCHIVO FIRMADO (USANDO VAULT) ===")
    signature_info = processor.create_signed_file(target_file, signed_file)
    print(f"Archivo firmado: {signed_file}")
    print(f"Firma: {signature_info['signature']}")
    print(f"Clave usada (private_key_used): {signature_info['private_key_used']}")

    print("=== FASE 3: VERIFICAR (USANDO VAULT) ===")
    verify_info = processor.verify_signed_file(signed_file, key={'use_vault': True, 'vault_index': 0})
    print(f"Verificación: {'VÁLIDA' if verify_info['valid'] else 'INVÁLIDA'}")
    print(f"Componentes hash: {verify_info['hash_components']}")


if __name__ == "__main__":
    main()
