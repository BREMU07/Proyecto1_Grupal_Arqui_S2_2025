# vault_test.asm
# Prueba de la bóveda Vault ISA: vwr, vinit, vsign
# Objetivo: Escribir llave privada en la bóveda, inicializar A/B/C/D,
# preparar 4 bloques de datos en memoria y ejecutar vsign.
#
# Notas:
# - Semántica usada en el proyecto: 
#   vwr rd, imm      -> rd (número de registro) indica índice de key (0..3)
#                      imm es la llave (inmediato) o se acepta vwr rd, rs1
#   vinit rd, imm    -> rd indica índice init (0..3), imm es valor inicial
#   vsign rd, rs1, rs2 -> firma usando key index en rs1 (valor en registro),
#                         datos a firmar empiezan en dirección contenida en rs2.
#

# --- Carga llave privada K0 directamente (vwr admite inmediato) ---
vwr x0, 0x123456789ABCDEF0   # escribe llave privada K0 en slot 0

# --- Inicializa valores A,B,C,D en la bóveda ---
vinit x0, 0x0123456789ABCDEF  # init A  -> index 0 (rd = x0 -> 0)
vinit x1, 0x0F0E0D0C0B0A0908  # init B  -> index 1 (rd = x1 -> 1)
vinit x2, 0x0011223344556677  # init C  -> index 2 (rd = x2 -> 2)
vinit x3, 0x8899AABBCCDDEEFF  # init D  -> index 3 (rd = x3 -> 3)

# --- Prepara dirección base donde estarán los 4 bloques (en memoria) ---
# Usamos un registro para contener la dirección base de los 4 bloques a firmar.
addi x5, x0, 0x0100   # x5 = 0x100  (direccion base para bloques de 8 bytes)
addi x0, x0, 0         # NOP (stall para el  pipeline)

# --- Ejecuta firmado usando llave K0, con datos en dirección x5 ---
# Semántica asumida: vsign rd, rs1, rs2
# - rs1 contiene el índice de llave (0 en x0)
# - rs2 contiene la dirección base de los 4 bloques (x5)
# - rd recibirá el resultado de la operación (en la microarquitectura puede escribirse a rd o a rd..rd+3 según implementación)
vsign x6, x0, x5   # firmar con key index = x0 (0), datos en addr = x5, resultado en x6

# --- FIN del programa: una instrucción NOP implícita (0x0) marcará el final ---
