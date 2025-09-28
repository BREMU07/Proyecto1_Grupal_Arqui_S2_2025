# -------------------------
# main.py
# -------------------------
from assembler import Assembler
from simple_pipeline import Simple_Pipeline

# -------------------------
# Programa de prueba
# -------------------------
asm_code = """
add x1, x2, x3
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

# Cargar programa en memoria
pipeline.load_program(program)

# -------------------------
# Ejecutar pipeline
# -------------------------
print("Ejecutando pipeline...\n")
while pipeline.is_pipeline_active():
    pipeline.step()

# -------------------------
# Mostrar resultados finales
# -------------------------
print("\nResultados finales de registros:")
print("x1  =", pipeline.registers[1])    # 10 + 5 = 15
print("x4  =", pipeline.registers[4])    # 20 - 8 = 12
print("x7  =", pipeline.registers[7])    # 2 * 3 = 6
print("x10 =", pipeline.registers[10])  # 12 & 5 = 4
print("x13 =", pipeline.registers[13])  # 1 | 7 = 7
print("x16 =", pipeline.registers[16])  # MEM[300] = 1234
