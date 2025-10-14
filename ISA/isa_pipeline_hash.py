#!/usr/bin/env python3

from assembler import Assembler
from simple_pipeline import Simple_Pipeline
import time

class ISAPipelineHashProcessor:
    def __init__(self, vault=None):
        self.assembler = Assembler()
<<<<<<< Updated upstream
        # Clave privada para firma (por ahora hardcodeada)
        self.private_key = 0x123456789ABCDEF0
    
=======
        
        # Usar la bóveda existente o crear una nueva
        if vault is None:
            self.vault = Vault()
            # Configurar clave por defecto en la bóveda (índice 0)
            self.vault.write_key(0, 0x123456789ABCDEF0)
        else:
            self.vault = vault
        
        self.key_index = 0  # Índice de la clave a usar por defecto
        self.pipeline = Simple_Pipeline(trace=False)
        self.program_loaded = False
    
    def set_key_index(self, index):
        """
        Cambiar el índice de la clave de bóveda a usar
        """
        if 0 <= index < len(self.vault.keys):
            self.key_index = index
            return True
        return False

    # --- ARCHIVOS ---
>>>>>>> Stashed changes
    def load_file(self, file_path):
        """Cargar archivo como bytes"""
        with open(file_path, 'rb') as f:
            return f.read()
    
    def sign_hash(self, A, B, C, D, key=None):
        """
        Firmar el hash usando XOR con la clave privada
        S = (A XOR K, B XOR K, C XOR K, D XOR K)
        """
        if key is None:
<<<<<<< Updated upstream
            key = self.private_key
        
        signature = (
            A ^ key,
            B ^ key,
            C ^ key,
            D ^ key
        )
        
        return signature
    
=======
            key = self.vault.keys[self.key_index]
        return (A ^ key, B ^ key, C ^ key, D ^ key)

>>>>>>> Stashed changes
    def verify_signature(self, signature, A, B, C, D, key=None):
        """
        Verificar la firma aplicando XOR nuevamente para recuperar el hash original
        """
        if key is None:
<<<<<<< Updated upstream
            key = self.private_key
        
        # Recuperar hash original: Hash = Signature XOR K
        recovered_A = signature[0] ^ key
        recovered_B = signature[1] ^ key  
        recovered_C = signature[2] ^ key
        recovered_D = signature[3] ^ key
        
        # Verificar que coincida con el hash calculado
        return (recovered_A == A and recovered_B == B and 
                recovered_C == C and recovered_D == D)
    
=======
            key = self.vault.keys[self.key_index]
        return (signature[0] ^ key == A and
                signature[1] ^ key == B and
                signature[2] ^ key == C and
                signature[3] ^ key == D)

    # --- CREAR ARCHIVO FIRMADO ---
>>>>>>> Stashed changes
    def create_signed_file(self, original_file, signed_file, key=None):
        """
        Crear archivo firmado que contiene el documento original + firma
        """
        # Calcular hash del documento original
        A, B, C, D = self.calculate_hash_components(original_file)
        
        # Firmar el hash
        signature = self.sign_hash(A, B, C, D, key)
        
        # Leer contenido original
        original_data = self.load_file(original_file)
        
        # Crear archivo firmado: [contenido original][firma de 32 bytes]
        with open(signed_file, 'wb') as f:
            f.write(original_data)  # Escribir documento original
            
            # Escribir firma (4 valores de 64 bits = 32 bytes)
            for sig_component in signature:
                f.write(sig_component.to_bytes(8, 'little'))
        
        print(f"Archivo firmado creado: {signed_file}")
        print(f"   Hash original: A=0x{A:016X}, B=0x{B:016X}, C=0x{C:016X}, D=0x{D:016X}")
        print(f"   Firma: S1=0x{signature[0]:016X}, S2=0x{signature[1]:016X}, S3=0x{signature[2]:016X}, S4=0x{signature[3]:016X}")
        
        return signature
    
    def verify_signed_file(self, signed_file, key=None):
        """
        Verificar un archivo firmado
        """
        with open(signed_file, 'rb') as f:
            data = f.read()
        
        # Los ultimos 32 bytes son la firma (4 x 8 bytes)
        if len(data) < 32:
            raise ValueError("Archivo demasiado pequeno para contener firma")
        
        document_data = data[:-32]  # Documento sin firma
        signature_data = data[-32:]  # Ultimos 32 bytes son la firma
        
        # Extraer componentes de la firma
        signature = []
        for i in range(4):
            sig_bytes = signature_data[i*8:(i+1)*8]
            sig_component = int.from_bytes(sig_bytes, 'little')
            signature.append(sig_component)
        signature = tuple(signature)
        
        # Recalcular hash del documento
        A, B, C, D = self.calculate_hash_from_data(document_data)
        
        # Verificar firma
        is_valid = self.verify_signature(signature, A, B, C, D, key)
        
        print(f"   Verificacion de archivo firmado:")
        print(f"   Documento: {len(document_data)} bytes")
        print(f"   Hash recalculado: A=0x{A:016X}, B=0x{B:016X}, C=0x{C:016X}, D=0x{D:016X}")
        print(f"   Firma leida: S1=0x{signature[0]:016X}, S2=0x{signature[1]:016X}, S3=0x{signature[2]:016X}, S4=0x{signature[3]:016X}")
        print(f"   Verificacion: {'VALIDA' if is_valid else 'INVALIDA'}")
        
        return is_valid
    
    def create_toymdata_program(self):
        """
        Crear programa ToyMDMA completo usando instrucciones del ISA
        con condicionales reales implementados con JAL y BEQ
        """
        program = """
        # ToyMDMA Hash Algorithm - Implementacion completa con ISA
        # Procesa un bloque de 8 bytes usando condicionales reales
        # 
        # Registros usados:
        # x1 = data_block (entrada de 8 bytes)
        # x2 = A, x3 = B, x4 = C, x5 = D (variables de hash)
        # x6 = GOLDEN_LOW, x7 = GOLDEN_HIGH  
        # x8 = PRIME, x9 = temp, x10 = temp2
        
        # === INICIALIZACION DE CONSTANTES ===
        # Cargar constantes ToyMDMA (valores completos de 64 bits usando addi)
        addi x6, x0, 0x7C15         # GOLDEN_LOW (parte baja de 0x9e3779b97f4a7c15)
        addi x7, x0, 0x7F4A         # GOLDEN_MID (para construir GOLDEN)
        addi x8, x0, 0xFFFB         # PRIME = 0xFFFFFFFB (truncado a 32 bits)
        
        # === ALGORITMO TOYMDATA - 8 PASOS ===
        
        # PASO 1: A = A + data_block (siempre se ejecuta)
        add x2, x2, x1
        
        # PASO 2: if (data_block != 0) B = B * data_block
        beq x1, x0, 16              # Si data_block == 0, saltar multiplicacion
        mul x3, x3, x1              # B = B * data_block
        
        # PASO 3: C = C ^ data_block (siempre se ejecuta)  
        xor x4, x4, x1
        
        # PASO 4: if (D != 0) D = D % PRIME
        beq x5, x0, 16              # Si D == 0, saltar modulo
        modi x5, x5, 0xFFFFFFFB     # D = D % PRIME
        
        # PASO 5: A = A + GOLDEN (construccion de 64-bit GOLDEN)
        add x2, x2, x6              # A = A + GOLDEN_LOW
        
        # PASO 6: B = B ^ A (mezcla)
        xor x3, x3, x2
        
        # PASO 7: C = C + B (acumulacion)
        add x4, x4, x3
        
        # PASO 8: D = D ^ C (mezcla final)
        xor x5, x5, x4
        
        # Los registros x2, x3, x4, x5 contienen A, B, C, D finales
        """
        return program
    
    def hash_block_with_isa(self, A, B, C, D, data_block):
        """
        Hashear un bloque usando el pipeline ISA con condicionales
        """
        try:
            # Compilar programa ToyMDMA
            instructions = self.assembler.assemble(self.create_toymdata_program())
            
            # Crear pipeline y cargar programa
            pipeline = Simple_Pipeline(trace=False)
            pipeline.load_program(instructions)
            
            # Inicializar registros con valores de entrada
            pipeline.registers[1] = data_block  # x1 = data_block
            pipeline.registers[2] = A           # x2 = A
            pipeline.registers[3] = B           # x3 = B  
            pipeline.registers[4] = C           # x4 = C
            pipeline.registers[5] = D           # x5 = D
            
            # Ejecutar pipeline
            steps = 0
            max_steps = 50
            
            while pipeline.is_pipeline_active() and steps < max_steps:
                pipeline.step()
                steps += 1
            
            if steps >= max_steps:
                raise RuntimeError(f"Pipeline excedio {max_steps} pasos")
            
            # Extraer resultados
            new_A = pipeline.registers[2] & 0xFFFFFFFFFFFFFFFF
            new_B = pipeline.registers[3] & 0xFFFFFFFFFFFFFFFF
            new_C = pipeline.registers[4] & 0xFFFFFFFFFFFFFFFF
            new_D = pipeline.registers[5] & 0xFFFFFFFFFFFFFFFF
            
            return new_A, new_B, new_C, new_D, steps
            
        except Exception as e:
            raise RuntimeError(f"Error en pipeline ISA: {e}")
    
    def toy_mdma_hash_isa(self, file_path):
        """
        Calcular hash ToyMDMA completo usando pipeline ISA
        """
        print(f"Hash ToyMDMA con Pipeline ISA")
        print("-" * 50)
        
        # Cargar archivo
        print(f"Cargando archivo: {file_path}")
        data = self.load_file(file_path)
        
        if not data:
            raise ValueError("No se pudo cargar el archivo")
        
        print(f"Tamano del archivo: {len(data)} bytes")
        
        # Procesar en bloques de 8 bytes
        blocks = [data[i:i+8] for i in range(0, len(data), 8)]
        
        # Padding del ultimo bloque si es necesario
        if len(blocks[-1]) < 8:
            blocks[-1] = blocks[-1].ljust(8, b'\x00')
        
        print(f"Total de bloques a procesar: {len(blocks)}")
        
        # Inicializar variables de hash
        A = 0x0123456789ABCDEF
        B = 0xFEDCBA9876543210  
        C = 0x1111111111111111
        D = 0x2222222222222222
        
        total_steps = 0
        start_time = time.time()
        
        # Procesar cada bloque
        for i, block in enumerate(blocks):
            # Convertir bloque a entero de 64 bits
            data_block = int.from_bytes(block, 'little')
            
            # Mostrar progreso cada 100 bloques
            if i % 100 == 0:
                print(f"Procesando bloque {i+1}/{len(blocks)}")
                print(f"   Datos: 0x{data_block:016X}")
                print(f"   Hash actual: A=0x{A:016X}, B=0x{B:016X}, C=0x{C:016X}, D=0x{D:016X}")
            
            # Procesar bloque con pipeline ISA
            A, B, C, D, steps = self.hash_block_with_isa(A, B, C, D, data_block)
            total_steps += steps
        
        end_time = time.time()
        
        # Mostrar resultados finales
        print(f"\nHash final del archivo:")
        print(f"   A = 0x{A:016X}")
        print(f"   B = 0x{B:016X}")
        print(f"   C = 0x{C:016X}")
        print(f"   D = 0x{D:016X}")
        
        # Combinar hash final (ejemplo simple)
        final_hash = (A ^ B ^ C ^ D) & 0xFFFFFFFFFFFFFFFF
        print(f"   Hash combinado = 0x{final_hash:016X}")
        
        print(f"Tiempo: {end_time - start_time:.4f} segundos")
        print(f"Total de pasos de pipeline: {total_steps}")
        print(f"Promedio de pasos por bloque: {total_steps/len(blocks):.1f}")
        print(f"Hash: 0x{final_hash:016X}")
        
        return final_hash
    
    def calculate_hash_components(self, file_path):
        """
        Calcular componentes individuales del hash (A, B, C, D) sin combinar
        """
        print(f"Calculando componentes de hash para: {file_path}")
        
        # Cargar archivo
        data = self.load_file(file_path)
        
        return self.calculate_hash_from_data(data)
    
    def calculate_hash_from_data(self, data):
        """
        Calcular hash ToyMDMA de datos en memoria, devolviendo componentes separados
        """
        # Procesar en bloques de 8 bytes
        blocks = [data[i:i+8] for i in range(0, len(data), 8)]
        
        # Padding del ultimo bloque si es necesario
        if len(blocks[-1]) < 8:
            blocks[-1] = blocks[-1].ljust(8, b'\x00')
        
        # Inicializar variables de hash
        A = 0x0123456789ABCDEF
        B = 0xFEDCBA9876543210  
        C = 0x1111111111111111
        D = 0x2222222222222222
        
        # Procesar cada bloque
        for block in blocks:
            # Convertir bloque a entero de 64 bits
            data_block = int.from_bytes(block, 'little')
            
            # Procesar bloque con pipeline ISA
            A, B, C, D, _ = self.hash_block_with_isa(A, B, C, D, data_block)
        
        return A, B, C, D

def main():
    """
    Demostracion completa: Hash ToyMDMA + Firma Digital
    """
    print("SISTEMA COMPLETO: ToyMDMA + Firma Digital")
    print("=" * 60)
    
    processor = ISAPipelineHashProcessor()
    target_file = "file_loader.py"
    signed_file = f"{target_file}_signed.bin"
    
    try:
        print("=== FASE 1: CALCULO DE HASH ===")
        # Calcular hash completo (para demostracion) 
        hash_result = processor.toy_mdma_hash_isa(target_file)
        print(f"Hash combinado: 0x{hash_result:016X}")
        
        print(f"\n=== FASE 2: FIRMA DIGITAL ===")
        # Crear archivo firmado
        signature = processor.create_signed_file(target_file, signed_file)
        
        print(f"\n=== FASE 3: VERIFICACION ===")
        # Verificar archivo firmado
        is_valid = processor.verify_signed_file(signed_file)
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"Archivo original: {target_file}")
        print(f"Archivo firmado: {signed_file}")
        print(f"Firma valida: {'SI' if is_valid else 'NO'}")
        print(f"Sistema funcionando: COMPLETO")
        
        # Mostrar tamanos
        import os
        original_size = os.path.getsize(target_file)
        signed_size = os.path.getsize(signed_file)
        signature_overhead = signed_size - original_size
        
        print(f"\nEstadisticas:")
        print(f"   Archivo original: {original_size} bytes")
        print(f"   Archivo firmado: {signed_size} bytes")
        print(f"   Overhead de firma: {signature_overhead} bytes")
        print(f"   Clave usada: 0x{processor.private_key:016X}")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()