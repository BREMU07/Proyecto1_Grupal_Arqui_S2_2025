# Operacion original: D = D ^ C
# Operacion inversa: D_prev = D_final ^ C_final
xor x9, x5, x4              # x9 = D_prev = D_final ^ C_final

# Operacion original: C = C + B  
# Operacion inversa: C_prev = C_final - B_final
sub x8, x4, x3              # x8 = C_prev = C_final - B_final

# Operacion original: B = B ^ A
# Operacion inversa: B_prev = B_final ^ A_final  
xor x7, x3, x2              # x7 = B_prev = B_final ^ A_final

# Operacion original: A = A + GOLDEN
# Operacion inversa: A_prev = A_final - GOLDEN
addi x10, x0, 0x7C15        # x10 = GOLDEN_LOW (constante)
sub x6, x2, x10             # x6 = A_prev = A_final - GOLDEN

# Operacion original: if (D != 0) D = D % PRIME
# Nota: La operacion modulo no es facilmente reversible
# Para demostracion, mantenemos el valor calculado en x9

# Operacion original: C = C ^ data_block
# Operacion inversa: C_original = C_prev ^ data_block
xor x8, x8, x1              # x8 = C_original = C_prev ^ data_block

# Operacion original: A = A + data_block
# Operacion inversa: A_original = A_prev - data_block
sub x6, x6, x1              # x6 = A_original = A_prev - data_block

