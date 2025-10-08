# -------------------------
# test.py
# -------------------------
from vault import Vault

def print_block(label, blocks):
    for i, b in enumerate(blocks):
        print(f"{label}[{i}] = 0x{b:016X}")
    print()

def main():
    print("=== Prueba unitaria de la bóveda segura (Vault) ===\n")

    # Inicializar bóveda
    vault = Vault()

    # -------------------------
    # Cargar llave privada y valores iniciales
    # -------------------------
    key = 0xDEADBEEFCAFEBABE
    inits = [
        0x0123456789ABCDEF,
        0x0F0E0D0C0B0A0908,
        0x0011223344556677,
        0x8899AABBCCDDEEFF
    ]

    vault.write_key(0, key)
    for i, val in enumerate(inits):
        vault.write_init(i, val)

    print("Llave y valores iniciales cargados en la bóveda:")
    print(f"Key[0] = 0x{vault.keys[0]:016X}")
    print_block("Init", vault.inits)

    # -------------------------
    # Mensaje de prueba (4 bloques de 64 bits)
    # -------------------------
    msg_blocks = [
        0x1111111111111111,
        0x2222222222222222,
        0x3333333333333333,
        0x4444444444444444
    ]
    print("Bloques de mensaje de entrada:")
    print_block("M", msg_blocks)

    # -------------------------
    # Firmar con la bóveda usando ToyMDMA
    # -------------------------
    signature = vault.sign_block(0, msg_blocks)

    # -------------------------
    # Mostrar firma resultante
    # -------------------------
    print("Firma generada (ToyMDMA, 4 bloques de 64 bits):")
    print_block("S", signature)

    # -------------------------
    # Validación simple
    # -------------------------
    all_64bit = all(0 <= s <= 0xFFFFFFFFFFFFFFFF for s in signature)
    if all_64bit:
        print("Todas las salidas están correctamente limitadas a 64 bits.\n")
    else:
        print("Error: algún valor excede los 64 bits.\n")

if __name__ == "__main__":
    main()
