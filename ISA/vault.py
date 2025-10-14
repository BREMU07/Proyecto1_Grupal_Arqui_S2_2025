# vault.py
# ----------------------------------------------------------
# Simulacion de la boveda segura para la ISA personalizada
# ----------------------------------------------------------

def rol64(x, r):
    """Rotación a la izquierda de 64 bits."""
    x &= 0xFFFFFFFFFFFFFFFF
    return ((x << r) | (x >> (64 - r))) & 0xFFFFFFFFFFFFFFFF


def toy_mdma_hash_block(block, a, b, c, d):
    """Función de mezcla ToyMDMA basada en operaciones no lineales."""
    A = a & 0xFFFFFFFFFFFFFFFF
    B = b & 0xFFFFFFFFFFFFFFFF
    C = c & 0xFFFFFFFFFFFFFFFF
    D = d & 0xFFFFFFFFFFFFFFFF

    # Operaciones lógicas no lineales
    f = (A & B) | (~A & C)
    g = (B & C) | (~B & D)
    h = (A ^ B ^ C ^ D)

    # Mezcla multiplicativa (constante de oro de 64 bits)
    mul = (block * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF

    # Rotaciones y combinaciones
    A = (rol64((A + f + mul) & 0xFFFFFFFFFFFFFFFF, 7) + B) & 0xFFFFFFFFFFFFFFFF
    B = (rol64((B + g + block) & 0xFFFFFFFFFFFFFFFF, 11) + (C * 3)) & 0xFFFFFFFFFFFFFFFF
    C = (rol64((C + h + mul) & 0xFFFFFFFFFFFFFFFF, 17) + (D % 0xFFFFFFFB)) & 0xFFFFFFFFFFFFFFFF
    D = (rol64((D + A + block) & 0xFFFFFFFFFFFFFFFF, 19) ^ (f * 5)) & 0xFFFFFFFFFFFFFFFF

    return A, B, C, D


class Vault:
    """
    Boveda segura para almacenamiento de llaves e inicializacion de hash.
    - Las llaves privadas NUNCA se exponen fuera de este modulo.
    - Solo las instrucciones autorizadas (vwr, vinit, vsign) pueden operar con ellas.
    """
    def __init__(self, num_keys=4):
        # Cuatro llaves privadas (K0–K3)
        self.keys = [0] * num_keys
        # Cuatro valores iniciales para el hash (A,B,C,D)
        self.inits = [0] * num_keys

    # ----------------------------------------------------------
    # Métodos de escritura segura
    # ----------------------------------------------------------
    def write_key(self, index, value):
        """Guarda una llave privada en la boveda."""
        if 0 <= index < len(self.keys):
            self.keys[index] = value & 0xFFFFFFFFFFFFFFFF

    def write_init(self, index, value):
        """Guarda un valor inicial (A/B/C/D) para el hash."""
        if 0 <= index < len(self.inits):
            self.inits[index] = value & 0xFFFFFFFFFFFFFFFF

    # ----------------------------------------------------------
    # Función principal de firmado seguro
    # ----------------------------------------------------------
    def sign_block(self, key_idx, data_blocks):
        """
        Aplica el algoritmo ToyMDMA sobre los datos y genera una firma segura.

        Entradas:
          - key_idx: indice de la llave privada (0-3)
          - data_blocks: lista de 4 bloques de 64 bits
        Salida:
          - Lista de 4 palabras (S0..S3) firmadas con la llave privada
        """
        if not (0 <= key_idx < len(self.keys)):
            return [0, 0, 0, 0]

        K = self.keys[key_idx]

        # Inicializacion: si no hay valores definidos, usar constantes base
        A = self.inits[0] if self.inits[0] else 0x0123456789ABCDEF
        B = self.inits[1] if self.inits[1] else 0x0F0E0D0C0B0A0908
        C = self.inits[2] if self.inits[2] else 0x0011223344556677
        D = self.inits[3] if self.inits[3] else 0x8899AABBCCDDEEFF

        # Procesar los 4 bloques secuencialmente
        for blk in data_blocks:
            A, B, C, D = toy_mdma_hash_block(blk, A, B, C, D)

        # Generar firma: XOR con la llave privada
        S = [
            (A ^ K) & 0xFFFFFFFFFFFFFFFF,
            (B ^ K) & 0xFFFFFFFFFFFFFFFF,
            (C ^ K) & 0xFFFFFFFFFFFFFFFF,
            (D ^ K) & 0xFFFFFFFFFFFFFFFF,
        ]

        return S

    def recover_components_from_signature(self, key_idx, signature):
        """
        Recupera internamente A,B,C,D desde una firma aplicando XOR con la llave almacenada.
        Esto mantiene la llave dentro de la boveda y no la expone.
        """
        if not (0 <= key_idx < len(self.keys)):
            return None
        K = self.keys[key_idx]
        return tuple((s ^ K) & 0xFFFFFFFFFFFFFFFF for s in signature)

    def sign_components(self, key_idx, components):
        """
        Dado A,B,C,D, produce los componentes de la firma S0..S3 aplicando XOR con la llave almacenada.
        """
        if not (0 <= key_idx < len(self.keys)):
            return [0, 0, 0, 0]
        K = self.keys[key_idx]
        return [ (c ^ K) & 0xFFFFFFFFFFFFFFFF for c in components ]
