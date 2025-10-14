# reverse_hash.asm
# Programa que toma una firma (S0..S3) en memoria y recupera A,B,C,D
# usando XOR con una clave local (proceso inverso de firma simple: comp = S ^ K)

# Dirección base donde se esperan las 4 componentes de la firma
addi x20, x0, 0x400    # x20 = base addr (1024)

# Cargar firma S0..S3 desde memoria
lw x1, 0(x20)          # S0
lw x2, 8(x20)          # S1
lw x3, 16(x20)         # S2
lw x4, 24(x20)         # S3

# Cargar clave local en x6 desde memoria en base+64 (8 bytes little-endian)
# reverse_hash.asm espera que el orquestador ponga la key en memoria en base+64
lw x6, 64(x20)

# Recuperar componentes A..D: A = S0 ^ K, etc.
xor x10, x1, x6        # A
xor x11, x2, x6        # B
xor x12, x3, x6        # C
xor x13, x4, x6        # D

# Escribir componentes recuperadas de vuelta a memoria (offsets 32..56)
sw x10, 32(x20)
sw x11, 40(x20)
sw x12, 48(x20)
sw x13, 56(x20)

# Fin del programa
ebreak
