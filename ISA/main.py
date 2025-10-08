# main.py -- pruebas del FileLoader 
import os
from file_loader import FileLoader

def main():
    print("=== Prueba del módulo FileLoader ===\n")

    # Crear memoria simulada como bytearray (2 MB por defecto)
    MEMORY_SIZE = 2 * 1024 * 1024  # 2 MiB
    memory = bytearray(MEMORY_SIZE)

    # Crear FileLoader pasando la referencia de memoria
    # Ajustamos base_address a 0x1000 (4096) para no pisar el posible código en 0
    loader = FileLoader(memory, base_address=0x1000)

    # Pedir archivo al usuario
    file_path = input("Ingrese la ruta del archivo a cargar: ").strip()

    if not file_path:
        print("No se ingresó ruta. Saliendo.")
        return

    if not os.path.exists(file_path):
        print("❌ Archivo no encontrado:", file_path)
        return

    try:
        # Lógica adaptable: llamamos al método que exista en FileLoader
        if hasattr(loader, 'load_file_in_blocks'):
            # preferimos bloques (útil para hashing), usamos block_size=8 (64 bits)
            result = loader.load_file_in_blocks(file_path, block_size=8)
            # load_file_in_blocks -> (start_addr, num_blocks, file_size)
            if isinstance(result, tuple) and len(result) == 3:
                start_addr, num_blocks, file_size = result
            else:
                raise RuntimeError("Formato de retorno inesperado desde load_file_in_blocks()")
        elif hasattr(loader, 'load_file_to_memory'):
            # carga completa (sin bloques)
            result = loader.load_file_to_memory(file_path)
            # load_file_to_memory -> (start_addr, size_bytes)
            if isinstance(result, tuple) and len(result) == 2:
                start_addr, file_size = result
                num_blocks = (file_size + 7) // 8  # contar bloques de 8 bytes como referencia
            else:
                raise RuntimeError("Formato de retorno inesperado desde load_file_to_memory()")
        else:
            raise AttributeError("FileLoader no provee métodos de carga conocidos (load_file_in_blocks / load_file_to_memory)")

        # Mostrar resultados
        print("\n✅ Archivo cargado correctamente:")
        print(f"  Ruta               : {file_path}")
        print(f"  Dirección inicial  : 0x{start_addr:08X}")
        print(f"  Tamaño (bytes)     : {file_size}")
        print(f"  Bloques (8 bytes)  : {num_blocks}")

        # Mostrar primeros 64 bytes en memoria (si están dentro del rango)
        end_preview = start_addr + 64
        if end_preview <= len(memory):
            preview = memory[start_addr:end_preview]
            print("\nPrimeros 64 bytes en memoria (hex):")
            print(preview.hex())
        else:
            print("\nNo hay suficiente memoria para mostrar 64 bytes de preview.")

    except Exception as e:
        print(f"\n⚠️ Error al cargar el archivo: {e}")


if __name__ == "__main__":
    main()

