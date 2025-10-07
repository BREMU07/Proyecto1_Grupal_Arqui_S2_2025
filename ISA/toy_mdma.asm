# ToyMDMA assembly implementation using project assembler instruction set
# Registers mapping (chosen for the assembler's x0..x31):
# x1 = A
# x2 = B
# x3 = C
# x4 = D
# x5 = block (input 64-bit block)
# x6..x12 = temporaries as needed
# Constants used:
# GOLDEN = 0x9e3779b97f4a7c15
# PRIME = 0xFFFFFFFB

# Implementation notes:
# - rol rd, rs1, imm     -> rotate-left immediate
# - muli rd, rs1, imm    -> rd = rs1 * imm
# - modi rd, rs1, imm    -> rd = rs1 % imm
# - add/sub/mul/and/or/xor/not are available as R-type ops
# - lw/sw are available for memory
# - This assembly follows the C reference step-by-step.

# PSEUDOCODE (C reference)
# A = *a; B = *b; C = *c; D = *d
# f = (A & B) | (~A & C)
# g = (B & C) | (~B & D)
# h = A ^ B ^ C ^ D
# mul = (block * GOLDEN) & 0xFFFFFFFFFFFFFFFF
# A = rol64(A + f + mul, 7) + B
# B = rol64(B + g + block, 11) + (C * 3)
# C = rol64(C + h + mul, 17) + (D % PRIME)
# D = rol64(D + A + block, 19) ^ (f * 5)

# Assembly sequence (uses temporaries x6..x12)

# compute f = (A & B) | (~A & C)
and x6, x1, x2        # x6 = A & B
not x7, x1            # x7 = ~A
and x8, x7, x3        # x8 = ~A & C
or x9, x6, x8         # x9 = f

# compute g = (B & C) | (~B & D)
and x6, x2, x3        # x6 = B & C
not x7, x2            # x7 = ~B
and x8, x7, x4        # x8 = ~B & D
or x10, x6, x8        # x10 = g

# compute h = A ^ B ^ C ^ D
xor x11, x1, x2       # x11 = A ^ B
xor x11, x11, x3      # x11 = A ^ B ^ C
xor x11, x11, x4      # x11 = h

# mul = block * GOLDEN
# Load 64-bit GOLDEN constant from memory address 512 into x13, then multiply
lw x13, 512(x0)        # x13 = GOLDEN (from memory)
mul x12, x5, x13       # x12 = block * GOLDEN
# (ensure x12 is treated as 64-bit in simulator/emulation)

# A = rol64(A + f + mul, 7) + B
add x6, x1, x9        # x6 = A + f
add x6, x6, x12       # x6 = A + f + mul
rol x6, x6, 7         # x6 = rol(x6, 7)
add x1, x6, x2        # A = x6 + B

# B = rol64(B + g + block, 11) + (C * 3)
add x6, x2, x10       # x6 = B + g
add x6, x6, x5        # x6 = B + g + block
rol x6, x6, 11        # x6 = rol(...,11)
# compute C*3
muli x7, x3, 3        # x7 = C * 3
add x2, x6, x7        # B = x6 + (C*3)

# C = rol64(C + h + mul, 17) + (D % PRIME)
add x6, x3, x11       # x6 = C + h
add x6, x6, x12       # x6 = C + h + mul
rol x6, x6, 17        # x6 = rol(...,17)
modi x7, x4, 0xFFFFFFFB # x7 = D % PRIME
add x3, x6, x7        # C = x6 + (D % PRIME)

# D = rol64(D + A + block, 19) ^ (f * 5)
add x6, x4, x1        # x6 = D + A
add x6, x6, x5        # x6 = D + A + block
rol x6, x6, 19        # x6 = rol(...,19)
# compute f * 5
muli x7, x9, 5        # x7 = f * 5
xor x4, x6, x7        # D = x6 ^ (f*5)

# final state: x1(A), x2(B), x3(C), x4(D)
# done
