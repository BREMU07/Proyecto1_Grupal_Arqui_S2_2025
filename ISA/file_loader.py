
import os
from simple_pipeline import Simple_Pipeline, PipelinedRegister

class FileLoader:
    def __init__(self, memory, base_address=0):
        """
        Inicializa el cargador de archivos
        
        Args:
            memory: Referencia a la memoria del pipeline (bytearray)
            base_address: Dirección base donde comenzar a cargar archivos
        """
        self.memory = memory
        self.base_address = base_address
        self.current_address = base_address
        
    def load_file_to_memory(self, file_path, target_address=None):
        """
        Carga un archivo completo a memoria
        
        Args:
            file_path: Ruta al archivo a cargar
            target_address: Dirección específica donde cargar (opcional)
            
        Returns:
            tuple: (dirección_inicio, tamaño_bytes)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        # Leer contenido del archivo
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        # Determinar dirección de carga
        if target_address is not None:
            load_address = target_address
        else:
            load_address = self.current_address
            
        # Verificar que hay espacio suficiente
        if load_address + len(file_content) > len(self.memory):
            raise MemoryError("Memoria insuficiente para cargar el archivo")
            
        # Cargar contenido a memoria
        self.memory[load_address:load_address + len(file_content)] = file_content
        
        # Actualizar dirección actual si no se especificó una dirección fija
        if target_address is None:
            self.current_address += len(file_content)
            
        return load_address, len(file_content)
    
    def load_file_in_blocks(self, file_path, block_size=64, target_address=None):
        """
        Carga un archivo en bloques de tamaño específico (para procesamiento por bloques)
        
        Args:
            file_path: Ruta al archivo a cargar
            block_size: Tamaño de cada bloque en bytes (default 64 bits = 8 bytes)
            target_address: Dirección específica donde cargar (opcional)
            
        Returns:
            tuple: (dirección_inicio, número_bloques, tamaño_bytes)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        # Leer contenido del archivo
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        # Determinar dirección de carga
        if target_address is not None:
            load_address = target_address
        else:
            load_address = self.current_address
            
        # Calcular número de bloques completos
        file_size = len(file_content)
        num_blocks = (file_size + block_size - 1) // block_size  # División hacia arriba
        
        # Verificar que hay espacio suficiente
        total_size = num_blocks * block_size
        if load_address + total_size > len(self.memory):
            raise MemoryError("Memoria insuficiente para cargar el archivo")
            
        # Cargar contenido a memoria, rellenando el último bloque si es necesario
        for i in range(num_blocks):
            start_idx = i * block_size
            end_idx = min((i + 1) * block_size, file_size)
            
            # Obtener bloque
            block_data = file_content[start_idx:end_idx]
            
            # Rellenar con ceros si el bloque está incompleto
            if len(block_data) < block_size:
                block_data += b'\x00' * (block_size - len(block_data))
                
            # Calcular dirección de destino para este bloque
            block_address = load_address + (i * block_size)
            
            # Escribir bloque en memoria
            self.memory[block_address:block_address + block_size] = block_data
            
        # Actualizar dirección actual si no se especificó una dirección fija
        if target_address is None:
            self.current_address += total_size
            
        return load_address, num_blocks, file_size
    
    def save_memory_to_file(self, start_address, size, output_path):
        """
        Guarda contenido de memoria a un archivo
        
        Args:
            start_address: Dirección inicial en memoria
            size: Cantidad de bytes a guardar
            output_path: Ruta del archivo de salida
        """
        if start_address + size > len(self.memory):
            raise ValueError("Rango de memoria inválido")
            
        content = bytes(self.memory[start_address:start_address + size])
        
        with open(output_path, 'wb') as f:
            f.write(content)
            
    def get_file_info(self, file_path):
        """
        Obtiene información sobre un archivo sin cargarlo
        
        Returns:
            dict: Información del archivo (tamaño, bloques necesarios, etc.)
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
            
        file_size = os.path.getsize(file_path)
        num_blocks_64bit = (file_size + 7) // 8  # Bloques de 64 bits (8 bytes)
        
        return {
            'file_size': file_size,
            'blocks_64bit': num_blocks_64bit,
            'blocks_64bit_padded': (file_size + 7) // 8,
            'file_path': file_path
        }
    
    def reset_memory_pointer(self):
        """Reinicia el puntero de memoria a la dirección base"""
        self.current_address = self.base_address
        
    def clear_memory_range(self, start_address, size):
        """
        Limpia un rango de memoria (establece a 0)
        
        Args:
            start_address: Dirección inicial
            size: Número de bytes a limpiar
        """
        if start_address + size > len(self.memory):
            raise ValueError("Rango de memoria inválido")
            
        self.memory[start_address:start_address + size] = b'\x00' * size


# Integración con el pipeline existente
class EnhancedPipeline(Simple_Pipeline):
    def __init__(self, memory_size=1024 * 1024, trace=False):  # 1MB por defecto
        # Extender memoria para archivos más grandes
        self.memory = bytearray(memory_size)
        self.registers = [0] * 32
        self.pc = 0
        self.cycle = 0
        self.trace = trace
        
        # Pipeline registers
        self.IF_ID = PipelinedRegister()
        self.ID_EX = PipelinedRegister()
        self.EX_MEM = PipelinedRegister()
        self.MEM_WB = PipelinedRegister()
        
        # File loader integrado
        self.file_loader = FileLoader(self.memory, base_address=1024)  # Comenzar después del código
    
    def load_file_for_hashing(self, file_path, target_address=None):
        """
        Carga un archivo para procesamiento de hash (en bloques de 64 bits)
        
        Returns:
            tuple: (start_address, num_blocks, file_size)
        """
        return self.file_loader.load_file_in_blocks(file_path, block_size=8, target_address=target_address)
    
    def save_signed_file(self, original_start, original_size, signature_start, output_path):
        """
        Guarda un archivo firmado (archivo original + firma de 256 bits al final)
        """
        # Leer archivo original de memoria
        original_content = bytes(self.memory[original_start:original_start + original_size])
        
        # Leer firma (256 bits = 32 bytes)
        signature = bytes(self.memory[signature_start:signature_start + 32])
        
        # Combinar archivo original con firma
        signed_content = original_content + signature
        
        # Guardar archivo firmado
        with open(output_path, 'wb') as f:
            f.write(signed_content)
            
    def extract_from_signed_file(self, signed_file_path, content_start=0):
        """
        Extrae contenido y firma de un archivo firmado
        """
        file_info = self.file_loader.get_file_info(signed_file_path)
        file_size = file_info['file_size']
        
        if file_size < 32:
            raise ValueError("Archivo firmado demasiado pequeño")
            
        # El archivo firmado tiene los últimos 32 bytes como firma
        content_size = file_size - 32
        
        # Cargar todo el archivo
        load_addr, actual_size = self.file_loader.load_file_to_memory(signed_file_path, content_start)
        
        # Retornar direcciones y tamaños
        return {
            'content_start': load_addr,
            'content_size': content_size,
            'signature_start': load_addr + content_size,
            'signature_size': 32,
            'total_size': actual_size
        }


# Ejemplo de uso integrado
def demo_file_loading():
    """Demostración del uso del cargador de archivos"""
    
    # Crear pipeline mejorado
    pipeline = EnhancedPipeline(memory_size=2 * 1024 * 1024)  # 2MB
    
    # Crear archivo de prueba
    test_content = b"Este es un documento de prueba para firma digital. " * 10
    with open('test_document.bin', 'wb') as f:
        f.write(test_content)
    
    try:
        # Cargar archivo para procesamiento de hash
        print("Cargando archivo para hash...")
        start_addr, num_blocks, file_size = pipeline.load_file_for_hashing('test_document.bin')
        
        print(f"Archivo cargado en memoria:")
        print(f"  Dirección inicial: 0x{start_addr:08X}")
        print(f"  Tamaño archivo: {file_size} bytes")
        print(f"  Bloques de 64 bits: {num_blocks}")
        
        # Mostrar primeros bytes en memoria como verificación
        first_bytes = pipeline.memory[start_addr:start_addr + 16]
        print(f"  Primeros bytes: {first_bytes.hex()}")
        
        # Simular procesamiento (aquí iría el código de hash real)
        print("\nArchivo listo para procesamiento con ToyMDMA...")
        
        # Guardar archivo firmado de ejemplo
        signature_data = b'\x01' * 32  # Firma de ejemplo
        pipeline.memory[0x1000:0x1020] = signature_data
        pipeline.save_signed_file(start_addr, file_size, 0x1000, 'documento_firmado.bin')
        print("Archivo firmado guardado como 'documento_firmado.bin'")
        
    finally:
        # Limpiar archivos de prueba
        if os.path.exists('test_document.bin'):
            os.remove('test_document.bin')
        if os.path.exists('documento_firmado.bin'):
            os.remove('documento_firmado.bin')


if __name__ == "__main__":
    demo_file_loading()
