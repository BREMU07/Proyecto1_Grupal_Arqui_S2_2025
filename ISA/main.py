# -------------------------
# main.py
# -------------------------
from assembler import Assembler
from simple_pipeline import Simple_Pipeline

# Programa de prueba
asm_code = """
add x1, x2, x3   
sub x4, x5, x6    
mul x7, x8, x9    
and x10, x11, x12 
or x13, x14, x15  
lw x16, 100(x17)  

# Nuevas instrucciones de bóveda
vwr x1, 0         # Cargar llave privada K0
vinit x2, 0       # Cargar valor inicial A
vsign 0, 400      # Firmar 4 bloques desde dirección 400
"""

# -------------------------
# Ensamblar
# -------------------------
assembler = Assembler()
program = assembler.assemble(asm_code)

# Mostrar las instrucciones generadas
print("Instrucciones generadas:")
for i, instr in enumerate(program):
    print(f"Instr {i}: 0x{instr:016X}")
print()

# -------------------------
# Inicializar pipeline
# -------------------------
pipeline = Simple_Pipeline()

# Inicializar registros con valores de prueba
pipeline.registers[2] = 10
pipeline.registers[3] = 5
pipeline.registers[5] = 20
pipeline.registers[6] = 8
pipeline.registers[8] = 2
pipeline.registers[9] = 3
pipeline.registers[11] = 12
pipeline.registers[12] = 5
pipeline.registers[14] = 1
pipeline.registers[15] = 7
pipeline.registers[17] = 200

# Inicializar memoria para LW (8 bytes)
pipeline.memory[300:308] = (1234).to_bytes(8, 'little')

# Inicializar registros usados por la bóveda
pipeline.registers[1] = 0xDEADBEEFCAFEBABE  # llave privada
pipeline.registers[2] = 0x0123456789ABCDEF  # valor inicial del hash

# Preparar 4 bloques de datos en memoria (mensaje a firmar)
msg_blocks = [0x1111111111111111, 0x2222222222222222, 0x3333333333333333, 0x4444444444444444]
for i, b in enumerate(msg_blocks):
    pipeline.memory[400 + i*8:400 + (i+1)*8] = b.to_bytes(8, 'little')

# Cargar programa en memoria
pipeline.load_program(program)

# -------------------------
# Ejecutar pipeline
# -------------------------
print("Ejecutando pipeline...\n")
cycle_count = 0
while pipeline.is_pipeline_active():
    pipeline.step()
    cycle_count += 1

print(f"Pipeline completado en {cycle_count} ciclos")

# -------------------------
# Mostrar resultados finales
# -------------------------
print("\n=== Resultados finales de registros ===")
print(f"x1  = {pipeline.registers[1]:>8} (add: 10 + 5)")      # 10 + 5 = 15
print(f"x4  = {pipeline.registers[4]:>8} (sub: 20 - 8)")      # 20 - 8 = 12
print(f"x7  = {pipeline.registers[7]:>8} (mul: 2 * 3)")       # 2 * 3 = 6
print(f"x10 = {pipeline.registers[10]:>8} (and: 12 & 5)")     # 12 & 5 = 4
print(f"x13 = {pipeline.registers[13]:>8} (or: 1 | 7)")       # 1 | 7 = 7
print(f"x16 = {pipeline.registers[16]:>8} (lw: MEM[300])")    # MEM[300] = 1234

# Mostrar estado de la bóveda y firma generada
print("\n=== Estado de la bóveda ===")
for i, key in enumerate(pipeline.vault.keys):
    print(f"Vault Key[{i}] = 0x{key:016X}")
for i, init in enumerate(pipeline.vault.inits):
    print(f"Vault Init[{i}] = 0x{init:016X}")

# Leer la firma generada en memoria (32 bytes después del mensaje)
sig_addr = 400 + 4*8
signature = [
    int.from_bytes(pipeline.memory[sig_addr + i*8:sig_addr + (i+1)*8], 'little')
    for i in range(4)
]
print("\n=== Firma generada ===")
for i, val in enumerate(signature):
    print(f"S[{i}] = 0x{val:016X}")


