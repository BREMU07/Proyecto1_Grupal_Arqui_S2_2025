# Proyecto1_Grupal_Arqui_S2_2025

## Descripcion

Modelo funcional de software de un CPU con arquitectura de conjunto de instrucciones (ISA) personalizada. Incluye simulacion de pipeline segmentado, sistema de boveda segura para almacenamiento de claves, y algoritmo de hash ToyMDMA con capacidades de firmado digital.

## Arquitectura del Sistema

### Componentes Principales

- **ISA Personalizada**: Conjunto de instrucciones de 64 bits con soporte para operaciones aritmeticas, logicas, de memoria y control de flujo
- **Pipeline Segmentado**: Implementacion de pipeline de 5 etapas (IF, ID, EX, MEM, WB) sin riesgos
- **Boveda Segura**: Sistema de almacenamiento seguro para claves privadas y valores de inicializacion
- **ToyMDMA Hash**: Algoritmo de hash personalizado con capacidades de firmado digital
- **Verificador de Firmas**: Sistema de verificacion de firmas digitales usando claves de boveda

### Estructura de Archivos

```
ISA/
├── main.py                     # Aplicacion principal con interfaz grafica
├── simple_pipeline.py          # Implementacion del pipeline segmentado
├── assembler.py               # Ensamblador para codigo assembly
├── vault.py                   # Implementacion de boveda segura
├── isa_pipeline_hash.py       # Procesador de hash ToyMDMA con ISA
├── verificador_boveda.py      # Verificador de firmas de boveda
├── file_loader.py             # Utilitario para carga de archivos
├── execution_statistics.py    # Estadisticas de ejecucion
├── interfaz/
│   ├── main_window.py         # Ventana principal de la aplicacion
│   └── pipeline_simple_window.py  # Interfaz del simulador de pipeline
├── program.asm                # Programa de ejemplo en assembly
├── vault_test.asm            # Programa de prueba para boveda
└── reverse_hash.asm # Programa de proceso inverso para verificacion

```

## Comandos de Compilacion y Ejecucion

### Requisitos Previos

- Python 3.8 o superior
- Tkinter (incluido en la mayoria de instalaciones de Python)

### Ejecucion del Sistema Completo

```bash
# Navegar al directorio ISA
cd ISA

# Ejecutar la aplicacion principal con interfaz grafica
python main.py
```

### Ejecucion de Componentes Individuales

#### Simulador de Pipeline

```bash
# Ejecutar simulador de pipeline directamente
cd ISA
python -c "
from interfaz.pipeline_simple_window import Simple_Pipeline_Window
import tkinter as tk
root = tk.Tk()
app = Simple_Pipeline_Window(root)
root.mainloop()
"
```

#### Ensamblador

```bash
# Ensamblar un programa assembly
cd ISA
python -c "
from assembler import Assembler
assembler = Assembler()
with open('program.asm', 'r') as f:
    code = f.read()
instructions = assembler.assemble(code)
print('Programa ensamblado exitosamente')
print(f'Instrucciones generadas: {len(instructions)}')
"
```

#### Procesador de Hash ToyMDMA

```bash
# Calcular hash de un archivo usando ISA
cd ISA
python -c "
from isa_pipeline_hash import ISAPipelineHashProcessor
processor = ISAPipelineHashProcessor()
# Cambiar 'archivo.txt' por el archivo deseado
result = processor.calculate_hash_components('archivo.txt')
print(f'Hash calculado: A={result[0]:016X}, B={result[1]:016X}, C={result[2]:016X}, D={result[3]:016X}')
"
```

#### Verificador de Boveda

```bash
# Verificar firma de un archivo
cd ISA
python verificador_boveda.py archivo_firmado.bin

# O usando el modulo directamente
python -c "
from verificador_boveda import VerificadorBoveda
verificador = VerificadorBoveda()
es_valida = verificador.verificar_firma('archivo_firmado.bin')
print('Resultado de verificacion:', es_valida)
"
```

#### Sistema de Boveda

```bash
# Probar sistema de boveda
cd ISA
python -c "
from vault import Vault
boveda = Vault()
boveda.write_key(0, 0x123456789ABCDEF0)
boveda.write_init(0, 0x0123456789ABCDEF)
print('Boveda configurada exitosamente')
print(f'Clave almacenada: {boveda.keys[0]:016X}')
"
```

### Scripts de Prueba

#### Prueba Completa del Sistema

```bash
cd ISA
python -c "
# Prueba completa del sistema
from simple_pipeline import Simple_Pipeline
from assembler import Assembler
from vault import Vault

# Inicializar componentes
pipeline = Simple_Pipeline()
assembler = Assembler()
boveda = Vault()

# Configurar boveda
boveda.write_key(0, 0x123456789ABCDEF0)

# Programa de prueba simple
program_code = '''
addi x1, x0, 42
addi x2, x1, 10
add x3, x1, x2
'''

# Ensamblar y ejecutar
instructions = assembler.assemble(program_code)
pipeline.load_program(instructions)

# Ejecutar programa
cycles = 0
while cycles < 10 and pipeline.pc < len(instructions) * 8:
    pipeline.cycle_step()
    cycles += 1

print(f'Programa ejecutado en {cycles} ciclos')
print(f'Registro x1: {pipeline.registers[1]}')
print(f'Registro x2: {pipeline.registers[2]}')
print(f'Registro x3: {pipeline.registers[3]}')
"
```

#### Prueba de Hash y Firmado

```bash
cd ISA
python -c "
# Crear archivo de prueba
with open('test_file.txt', 'w') as f:
    f.write('Contenido de prueba para hash')

# Procesar con ToyMDMA
from isa_pipeline_hash import ISAPipelineHashProcessor
processor = ISAPipelineHashProcessor()

# Calcular hash
hash_result = processor.calculate_hash_components('test_file.txt')
print(f'Hash: {[hex(h) for h in hash_result]}')

# Crear archivo firmado
signed_info = processor.create_signed_file('test_file.txt', 'test_file_signed.bin')
print(f'Archivo firmado creado: test_file_signed.bin')
print(f'Firma: {[hex(s) for s in signed_info[\"signature\"]]}')

# Verificar firma
verification = processor.verify_signed_file('test_file_signed.bin')
print(f'Verificacion: {verification[\"valid\"]}')

# Limpiar archivos de prueba
import os
os.remove('test_file.txt')
os.remove('test_file_signed.bin')
"
```

### Casos de Uso Comunes

#### 1. Cargar y Ejecutar Programa Assembly

```bash
cd ISA
# Editar program.asm con tu codigo
# Luego ejecutar:
python main.py
# En la interfaz: Load Program -> Seleccionar program.asm -> Run Program
```

#### 2. Procesar Archivo con Hash y Firmado

```bash
cd ISA
python main.py
# En la interfaz: Load & Hash File -> Seleccionar archivo -> Ver resultados
```

#### 3. Verificar Firma de Boveda

```bash
cd ISA
python main.py
# En Pipeline Window: Verificar Boveda -> Seleccionar archivo .bin firmado
```

## Estructura del ISA

### Formato de Instrucciones (64 bits)

```
Tipo R: [funct7:7][rs2:5][rs1:5][funct3:3][rd:5][opcode:7][reserved:32]
Tipo I: [imm:12][rs1:5][funct3:3][rd:5][opcode:7][reserved:32]
```

### Conjunto de Instrucciones Soportadas

**Aritmeticas:**
- ADD, SUB, MUL, DIV, MOD
- ADDI, SUBI, MULI, DIVI, MODI

**Logicas:**
- AND, OR, XOR, NOT
- ANDI, ORI, XORI

**Memoria:**
- LW, SW (Load/Store Word)

**Control de Flujo:**
- BEQ, BNE, BLT, BGE (Branches)
- JAL, JALR (Jumps)

**Boveda (Especiales):**
- VWR (Vault Write)
- VINIT (Vault Initialize)  
- VSIGN (Vault Sign)

## Notas de Implementacion

- El pipeline implementa deteccion y manejo de riesgos de datos
- La boveda mantiene claves privadas que nunca se exponen fuera del modulo
- El algoritmo ToyMDMA utiliza operaciones no lineales para seguridad criptografica
- Todas las operaciones de 64 bits utilizan aritmetica modular para evitar overflow

## Dependencias

- Python 3.8+
- tkinter (GUI)
- struct (manipulacion de datos binarios)
- time (medicion de rendimiento)
