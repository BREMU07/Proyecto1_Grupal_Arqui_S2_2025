# vault_test_runner.py
# Runner de prueba para vault_test.asm
# Ensambla, carga datos en memoria, ejecuta pipeline y muestra resultados

import os
import time
from assembler import Assembler
from simple_pipeline import Simple_Pipeline

ASM_PATH = os.path.join(os.path.dirname(__file__), "vault_test.asm")

def prepare_data_blocks():
    """
    Devuelve una lista de 4 bloques de 8 bytes (enteros de 64 bits)
    que vamos a colocar en memoria consecutiva (little-endian).
    Cambia estos valores si quieres probar otros datos.
    """
    blocks = [
        0x1111111111111111,
        0x2222222222222222,
        0x3333333333333333,
        0x4444444444444444
    ]
    return blocks

def write_blocks_to_memory(mem, base_addr, blocks):
    """Escribe bloques (lista de ints 64-bit) en memoria bytearray mem a partir de base_addr."""
    for i, blk in enumerate(blocks):
        addr = base_addr + i*8
        mem[addr:addr+8] = int.to_bytes(blk & 0xFFFFFFFFFFFFFFFF, 8, 'little')

def main():
    print("Vault ISA test runner")
    print("=====================")

    # 1) Leer archivo de prueba ASM
    if not os.path.exists(ASM_PATH):
        print(f"ERROR: No se encuentra {ASM_PATH}")
        return

    with open(ASM_PATH, 'r', encoding='utf-8') as f:
        asm_code = f.read()

    # 2) Ensamblar
    assembler = Assembler()
    program = assembler.assemble(asm_code)
    print(f"Programa ensamblado: {len(program)} instrucciones")

    # 3) Crear pipeline y memoria
    pipeline = Simple_Pipeline(trace=True)
    #aumenta memoria
    if len(pipeline.memory) < 0x200:
        pipeline.memory = bytearray(1024 * 4)  # por ejemplo 4KB

    # 4) Prepara bloques de datos y los escribe en memoria en 0x100
    base_addr = 0x100
    blocks = prepare_data_blocks()
    write_blocks_to_memory(pipeline.memory, base_addr, blocks)
    print(f"Se escribieron {len(blocks)} bloques en memoria en 0x{base_addr:04X}")

    # 5) Carga programa en memoria (al comienzo)
    pipeline.load_program(program)
    print("Programa cargado en la memoria del pipeline.")


    # 6) Ejecuta el pipeline paso a paso hasta terminar o alcanzar límite
    max_steps = 1000
    step = 0
    start_time = time.time()
    try:
        while pipeline.is_pipeline_active() and step < max_steps:
            pipeline.step()
            step += 1
            #Debug print
            print(f"Step {step}: PC=0x{pipeline.pc:X}")
    except Exception as e:
        print("Error durante la ejecución del pipeline:", e)
        import traceback
        traceback.print_exc()

    end_time = time.time()
    print(f"Ejecutados {step} ciclos en {end_time - start_time:.4f} s")

    # 7) Lee resultados:
    # Leer la firma desde memoria después de los bloques
    sig_addr = base_addr + 4*8
    signature = [int.from_bytes(pipeline.memory[sig_addr + i*8 : sig_addr + (i+1)*8], 'little') for i in range(4)]
    print("Firma leída de memoria:")
    for i, val in enumerate(signature):
        print(f"  S{i}: 0x{val:016X}")

    # Leer la llave almacenada en la bóveda
    vault_key0 = None
    if hasattr(pipeline, 'vault') and hasattr(pipeline.vault, 'keys'):
        vault_key0 = pipeline.vault.keys[0]

    if vault_key0 is not None:
        print(f"Key0 (desde pipeline): 0x{vault_key0 & 0xFFFFFFFFFFFFFFFF:016X}")
        # Calcular la firma esperada
        # Repetir el algoritmo ToyMDMA para los bloques
        from vault import toy_mdma_hash_block
        A = pipeline.vault.inits[0] if pipeline.vault.inits[0] else 0x0123456789ABCDEF
        B = pipeline.vault.inits[1] if pipeline.vault.inits[1] else 0x0F0E0D0C0B0A0908
        C = pipeline.vault.inits[2] if pipeline.vault.inits[2] else 0x0011223344556677
        D = pipeline.vault.inits[3] if pipeline.vault.inits[3] else 0x8899AABBCCDDEEFF
        for blk in blocks:
            A, B, C, D = toy_mdma_hash_block(blk, A, B, C, D)
        expected_signature = [
            (A ^ vault_key0) & 0xFFFFFFFFFFFFFFFF,
            (B ^ vault_key0) & 0xFFFFFFFFFFFFFFFF,
            (C ^ vault_key0) & 0xFFFFFFFFFFFFFFFF,
            (D ^ vault_key0) & 0xFFFFFFFFFFFFFFFF,
        ]
        print("Firma esperada:")
        for i, val in enumerate(expected_signature):
            print(f"  S{i}: 0x{val:016X}")
        print("Coincide?", "SI" if signature == expected_signature else "NO")
    else:
        print("No se pudo leer la key desde pipeline (estructura diferente). "
              "Verifica implementación de bóveda en simple_pipeline.py")

if __name__ == "__main__":
    main()
