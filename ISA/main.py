# -------------------------
# main.py (solo pruebas del file_loader)
# -------------------------
from file_loader import FileLoader
import os

# Clase de memoria simulada para pruebas
class DummyMemory:
    def __init__(self, size=1024 * 64):
        self.mem = bytearray(size)

    def write_block(self, start_addr, data):
        """Simula escritura de un bloque de datos en memoria"""
        end = start_addr + len(data)
        if end > len(self.mem):
            raise ValueError("Bloque excede el tamaño de la memoria simulada")
        self.mem[start_addr:end] = data

    def __getitem__(self, addr):
        return self.mem[addr]

    def __setitem__(self, addr, val):
        self.mem[addr] = val


def main():
    print("=== Prueba del módulo FileLoader ===")

    # Crear memoria simulada y loader
    memory = DummyMemory()
    loader = FileLoader(memory)

    # Pedir archivo al usuario
    file_path = input("Ingrese la ruta del archivo a cargar: ").strip()

    if not os.path.exists(file_path):
        print("❌ Archivo no encontrado.")
        return

    try:
        # Cargar archivo en memoria
        result = loader.load_file(file_path)

        # Detectar tipo de retorno
        if isinstance(result, tuple):
            start_addr, num_blocks, file_size = result
        elif isinstance(result, dict):
            start_addr = result.get("start_addr")
            num_blocks = result.get("num_blocks")
            file_size = result.get("file_size")
        else:
            raise TypeError("El método load_file() devolvió un tipo inesperado.")

        # Mostrar resultados
        print("\n✅ Archivo cargado correctamente:")
        print(f"  Dirección inicial: 0x{start_addr:08X}")
        print(f"  Bloques cargados  : {num_blocks}")
        print(f"  Tamaño del archivo: {file_size} bytes")

        # Mostrar primeros bytes de la memoria
        print("\nPrimeros 64 bytes en memoria:")
        print(memory.mem[start_addr:start_addr + 64].hex())

    except Exception as e:
        print(f"⚠️ Error al cargar el archivo: {e}")


if __name__ == "__main__":
    main()
