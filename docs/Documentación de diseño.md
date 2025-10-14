# Arquitectura del set de instrucciones

## Tipos y tamaños de datos
**Datos soportados:** El procesador opera principalmente con enteros de 64 bits, tanto en registros como en memoria. El uso de 64 bits permite operaciones eficientes sobre grandes cantidades de datos y es adecuado para aplicaciones modernas, como criptografía y procesamiento de archivos.

## Registros disponibles 
**Banco de registros:** 32 registros generales(`x0-x31`), cada uno de 64 bits.
- (`x0`): Registro constante con valor cero (no modificable).
- (`x1`) a (`x31`): Registros de propósito general para operaciones aritméticas, lógicas, direcciones y almacenamiento temporal.

Un banco amplio de registros reduce la necesidad de acceso a memoria, mejora el rendimiento y simplifica la gestión de variables temporales.

## Modos de direccionamiento
- **Inmediato:** Permite usar valores constantes directamente en las instrucciones.
- **Registro:** Operaciones entre valores almacenados en registros.
- **Memoria directa:** Acceso a posiciones de memoria especificadas por registros.
- **Justificación:** Estos modos cubren los casos más comunes en programación y hardware, manteniendo la ISA simple y eficiente.
  
## Sintaxis
Las instrucciones siguen el formato

# Modelado del software 

Este proyecto implementa una arquitectura **RISC segmentada (pipeline)** con extensiones **criptográficas seguras**, simulada completamente en **Python**.

El sistema incluye un módulo de **bóveda (Vault)** que almacena llaves privadas y realiza el **firmado digital** de bloques de datos mediante una función hash personalizada denominada **ToyMDMA**.

## Componentes principales

El modelo integra:

- Un **simulador de pipeline** de 5 etapas (IF, ID, EX, MEM, WB)  
- Un **conjunto de instrucciones extendido** (ISA personalizada)  
- Una **bóveda segura (Vault)** para operaciones de clave y firma  
- Una **interfaz gráfica (Tkinter)** para simular la ejecución paso a paso  
- Un **script de pruebas automáticas** (`vault_test_runner.py`) para validación de la firma

---

## Banco de registros y memoria

| Recurso | Descripción |
|---------|-------------|
| **32 registros (x0–x31)** | Registros de propósito general (`x0` es siempre cero) |
| **Memoria principal** | 1024 bytes direccionados por bytes |
| **Codificación de instrucción** | 64 bits: `[63-56] opcode`, `[55-51] rd`, `[50-46] rs1`, `[45-41] rs2`, `[40-38] funct3`, `[37-31] funct7`, `[30-0] imm` |
| **Endianness** | *Little-endian* para almacenamiento en memoria |

---

## Flujo de pipeline (5 etapas)

| Etapa | Función | Estructura usada |
|-------|---------|------------------|
| **IF (Instruction Fetch)** | Obtiene la instrucción desde memoria | `IF_ID` |
| **ID (Instruction Decode)** | Decodifica `opcode`, registros e inmediato | `ID_EX` |
| **EX (Execute)** | Realiza operación aritmética o controla flujo | `EX_MEM` |
| **MEM (Memory Access)** | Accede a memoria o bóveda | `MEM_WB` |
| **WB (Write Back)** | Escribe el resultado en el registro destino | `MEM_WB` |

> La función `step()` ejecuta una iteración completa del pipeline, propagando los valores entre registros segmentados.

---

## Conjunto de instrucciones (ISA extendida)

### Instrucciones aritméticas

| Instrucción | Descripción | Opcode |
|-------------|-------------|--------|
| `add rd, rs1, rs2` | Suma de registros | `0xC3` |
| `sub rd, rs1, rs2` | Resta de registros | `0xC3` |
| `mul rd, rs1, rs2` | Multiplicación | `0xC3` |
| `addi rd, rs1, imm` | Suma inmediata | `0xA9` |
| `muli rd, rs1, imm` | Multiplicación inmediata | `0xAB` |
| `modi rd, rs1, imm` | Módulo inmediato | `0xAC` |
| `rol rd, rs1, imm` | Rotación izquierda 64 bits | `0xAA` |

---

### Instrucciones lógicas y de control

| Instrucción | Descripción | Opcode |
|-------------|-------------|--------|
| `and rd, rs1, rs2` | AND bit a bit | `0xF6` |
| `or rd, rs1, rs2` | OR bit a bit | `0xF6` |
| `xor rd, rs1, rs2` | XOR bit a bit | `0xF7` |
| `not rd, rs1` | Negación (unaria) | `0xF7` |

---

### Control de flujo

| Instrucción | Descripción | Opcode |
|-------------|-------------|--------|
| `jal rd, imm` | Salto con enlace | `0xD4` |
| `beq rs1, rs2, imm` | Branch si iguales | `0xE5` |

---

### Extensión criptográfica (Vault)

| Instrucción | Función | Opcode |
|-------------|---------|--------|
| `vwr rd, imm` | Escribe llave privada | `0x90` |
| `vinit rd, imm` | Inicializa valor de hash (A–D) | `0x91` |
| `vsign rs1, rs2` | Firma bloque de memoria | `0x92` |

---

## Bóveda segura (Vault)

### Descripción general

La clase `Vault` encapsula todas las operaciones de seguridad:

- **`write_key()`**: almacena llaves privadas internas.  
- **`write_init()`**: define valores iniciales del hash.  
- **`sign_block()`**: genera la firma *ToyMDMA* sobre cuatro bloques de datos.

---

## Algoritmo ToyMDMA

El algoritmo de hash **ToyMDMA** combina operaciones no lineales, multiplicativas y rotacionales de 64 bits:

```python
f = (A & B) | (~A & C)
g = (B & C) | (~B & D)
h = (A ^ B ^ C ^ D)
mul = (block * 0x9E3779B97F4A7C15)

A = rol64((A + f + mul), 7) + B
B = rol64((B + g + block), 11) + (C * 3)
C = rol64((C + h + mul), 17) + (D % 0xFFFFFFFB)
D = rol64((D + A + block), 19) ^ (f * 5)
```

El resultado final se firma con una llave privada:

```python
S = [A ^ K, B ^ K, C ^ K, D ^ K]
```

---

## Interfaz gráfica

### Ventana principal (`main_window.py`)

- Sistema de **login de superusuario** para habilitar operaciones seguras.  
- Acceso a la ventana de simulación del pipeline.

### Simulador de pipeline (`pipeline_simple_window.py`)

- Muestra las **cinco etapas** del pipeline en tiempo real.  
- Permite ejecutar **paso a paso** o de forma **automática**.  
- Visualiza **registros**, **memoria** y **firma generada**.

**Botones principales:**

- **Cargar programa**  
- **Ejecutar paso**  
- **Firmar datos (Vault)**  
- **Mostrar estadísticas**

---

## Estadísticas de ejecución

El módulo `execution_statistics.py` calcula métricas como:

- Número total de ciclos  
- **CPI** (Cycles Per Instruction)  
- Tiempo total de ejecución  
- Porcentaje de ocupación del pipeline  

Los resultados se muestran en la interfaz gráfica al finalizar la simulación.

---

## Consideraciones de diseño

| Aspecto | Decisión |
|---------|----------|
| **Separación de responsabilidades** | Lógica de ejecución (pipeline) separada de la interfaz |
| **Seguridad** | La bóveda no expone llaves privadas fuera de `vault.py` |
| **Extensibilidad** | El formato unificado de 64 bits permite agregar nuevas instrucciones |
| **Visibilidad** | La interfaz visualiza las etapas, registros y ciclos en tiempo real |
| **Compatibilidad** | El sistema es portable (Python 3.10+ sin dependencias externas) |

---
