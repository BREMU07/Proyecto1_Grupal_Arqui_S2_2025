# program.asm - Programa de prueba completo para todas las instrucciones del ISA
# Este programa prueba sistematicamente cada instruccion implementada

# === INICIALIZACION ===
# Configurar valores iniciales en registros
addi x1, x0, 10          # x1 = 10 (valor base para pruebas)
addi x2, x0, 5           # x2 = 5 (segundo operando)
addi x3, x0, 42          # x3 = 42 (valor de prueba)
addi x4, x0, 100         # x4 = 100 (valor grande)
addi x5, x0, 1           # x5 = 1 (incremento)

# === INSTRUCCIONES ARITMETICAS BASICAS ===
# Prueba ADD - Suma de registros
add x6, x1, x2           # x6 = x1 + x2 = 10 + 5 = 15

# Prueba SUB - Resta de registros  
sub x7, x4, x1           # x7 = x4 - x1 = 100 - 10 = 90

# Prueba MUL - Multiplicacion de registros
mul x8, x1, x2           # x8 = x1 * x2 = 10 * 5 = 50

# === INSTRUCCIONES INMEDIATAS ===
# Prueba ADDI - Suma con inmediato
addi x9, x3, 8           # x9 = x3 + 8 = 42 + 8 = 50

# Prueba MULI - Multiplicacion con inmediato
muli x10, x2, 3          # x10 = x2 * 3 = 5 * 3 = 15

# Prueba MODI - Modulo con inmediato
modi x11, x4, 7          # x11 = x4 % 7 = 100 % 7 = 2

# === INSTRUCCIONES LOGICAS ===
# Configurar valores para operaciones logicas
addi x12, x0, 0xFF       # x12 = 255 (0xFF)
addi x13, x0, 0x0F       # x13 = 15 (0x0F)

# Prueba AND - Y logico
and x14, x12, x13        # x14 = x12 & x13 = 0xFF & 0x0F = 0x0F

# Prueba OR - O logico  
or x15, x12, x13         # x15 = x12 | x13 = 0xFF | 0x0F = 0xFF

# Prueba XOR - O exclusivo
xor x16, x12, x13        # x16 = x12 ^ x13 = 0xFF ^ 0x0F = 0xF0

# Prueba NOT - Negacion logica
not x17, x13, x0         # x17 = ~x13 (NOT de x13)

# === INSTRUCCIONES DE ROTACION ===
# Prueba ROL - Rotacion a la izquierda
addi x18, x0, 0x80       # x18 = 128 (10000000 en binario)
rol x19, x18, 1          # x19 = rotar x18 una posicion a la izquierda

# === INSTRUCCIONES DE MEMORIA ===
# Preparar datos para memoria
addi x20, x0, 0x200      # x20 = direccion base de memoria (512)
addi x21, x0, 0xDEAD     # x21 = datos a almacenar (0xDEAD)

# Prueba SW - Store Word (guardar en memoria)
sw x21, 0(x20)           # Memoria[x20 + 0] = x21 (guardar 0xDEAD en direccion 512)

# Prueba LW - Load Word (cargar de memoria)
lw x22, 0(x20)           # x22 = Memoria[x20 + 0] (cargar desde direccion 512)

# Almacenar otro valor con offset
sw x3, 8(x20)            # Memoria[x20 + 8] = x3 (guardar 42 en direccion 520)
lw x23, 8(x20)           # x23 = Memoria[x20 + 8] (cargar desde direccion 520)

# === INSTRUCCIONES DE BOVEDA ===
# Configurar boveda con claves y valores iniciales

# VWR - Vault Write Register (escribir clave en boveda)
# Sintaxis: vwr indice, valor_inmediato
vwr x0, 0x1234           # Escribir valor 0x1234 en indice 0 de claves de boveda
vwr x1, 0x5678           # Escribir valor 0x5678 en indice 1 de claves de boveda

# VINIT - Vault Initialize (inicializar valores de hash)
# Sintaxis: vinit indice, valor_inmediato
vinit x0, 0xABCD         # Inicializar valor A=0xABCD en boveda (indice 0)
vinit x1, 0xEF01         # Inicializar valor B=0xEF01 en boveda (indice 1)

# VSIGN - Vault Sign Block (firmar bloque con boveda)
# Preparar direccion donde almacenar los datos a firmar
addi x28, x0, 0x400      # x28 = direccion base para datos (1024)

# Almacenar 4 bloques de datos en memoria para firmar
sw x1, 0(x28)            # Almacenar bloque 1 en memoria
sw x2, 8(x28)            # Almacenar bloque 2 en memoria
sw x3, 16(x28)           # Almacenar bloque 3 en memoria
sw x4, 24(x28)           # Almacenar bloque 4 en memoria

# Preparar registros para vsign: rd=x0, rs1=indice_clave, rs2=direccion_datos
addi x29, x0, 0          # x29 = indice de clave 0
# Firmar con clave del indice 0
vsign x0, x29, x28       # Firmar bloques usando clave 0 de boveda

# === INSTRUCCIONES DE CONTROL DE FLUJO ===
# Preparar registros para pruebas de control

# Prueba BEQ - Branch if Equal (salto condicional si igual)
addi x1, x0, 5           # Restablecer x1 = 5
addi x2, x0, 5           # x2 = 5 (igual a x1)
beq x1, x2, 4            # Si x1 == x2, saltar 4 instrucciones adelante

# Estas instrucciones se saltaran si la condicion es verdadera
addi x1, x0, 999         # Esta no se ejecutara (se salta)
addi x2, x0, 999         # Esta no se ejecutara (se salta) 
addi x3, x0, 999         # Esta no se ejecutara (se salta)
addi x4, x0, 999         # Esta no se ejecutara (se salta)

# Destino del salto - continua aqui
addi x5, x0, 200         # x5 = 200 (confirma que el salto funciono)

# === PRUEBA DE JAL - Jump and Link ===
# JAL guarda PC+4 en registro destino y salta
jal x6, 8               # Saltar 8 bytes adelante, guardar direccion de retorno en x6

# Estas instrucciones se saltaran
addi x7, x0, 777         # No se ejecutara
addi x8, x0, 888         # No se ejecutara

# Destino del salto JAL
addi x9, x0, 300         # x9 = 300 (confirma que JAL funciono)

# === PRUEBAS ADICIONALES DE COHERENCIA ===
# Verificar que los resultados son correctos
add x10, x6, x7          # Sumar resultados de operaciones anteriores
sub x11, x8, x9          # Restar para verificar coherencia
mul x12, x5, x2          # Multiplicar valores calculados

# === OPERACIONES FINALES DE VERIFICACION ===
# Cargar valores finales para verificacion
lw x13, 0(x20)           # Verificar que el valor guardado sigue en memoria
add x14, x13, x22        # Sumar valor cargado con valor leido anteriormente

# Operacion final con todos los tipos de instrucciones usadas
and x15, x14, x12        # Operacion logica final
or x16, x15, x11         # Combinar resultados
xor x17, x16, x10        # Resultado final en x17

# === FINALIZACION DEL PROGRAMA ===  
# EBREAK - Environment Break (finalizar programa)
ebreak                   # Señal de fin del programa