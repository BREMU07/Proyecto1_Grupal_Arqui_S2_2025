#!/usr/bin/env python3
# verificador_boveda.py - Verificacion simple de firma de boveda

import struct
import os

class VerificadorBoveda:
    def __init__(self, vault=None):
        # Si no se proporciona una bóveda, crear una por defecto
        if vault is None:
            from vault import Vault
            self.vault = Vault()
            # Configurar clave por defecto en la bóveda (índice 0)
            self.vault.write_key(0, 0x123456789ABCDEF0)
        else:
            self.vault = vault
        
        # Usar la clave de la bóveda (índice 0 por defecto)
        self.key_index = 0
    
    def set_key_index(self, index):
        """
        Cambiar el índice de la clave de bóveda a usar para verificación
        """
        if 0 <= index < len(self.vault.keys):
            self.key_index = index
            return True
        return False
    
    def verificar_firma(self, archivo_firmado_path):
        """
        Verifica si la firma de un archivo es válida para la bóveda.
        Imprime solo si es válida o no, sin detalles.
        """
        if not os.path.exists(archivo_firmado_path):
            print("Archivo no encontrado.")
            return False
        
        try:
            with open(archivo_firmado_path, 'rb') as f:
                contenido = f.read()
            
            if len(contenido) < 32:
                print("Archivo demasiado pequeño para contener firma.")
                return False
            
            # Separar contenido y firma
            contenido_original = contenido[:-32]
            firma_bytes = contenido[-32:]
            
            # Extraer componentes de la firma
            s1, s2, s3, s4 = struct.unpack('<QQQQ', firma_bytes)
            
            # Obtener clave de la bóveda
            boveda_key = self.vault.keys[self.key_index]
            
            # Descifrar firma
            A_esperado = s1 ^ boveda_key
            B_esperado = s2 ^ boveda_key
            C_esperado = s3 ^ boveda_key
            D_esperado = s4 ^ boveda_key
            
            # Recalcular hash del documento
            hash_recalculado = self.calcular_hash_documento(contenido_original)
            A_calc, B_calc, C_calc, D_calc = hash_recalculado
            
            # Comparar
            if (A_esperado == A_calc and B_esperado == B_calc and 
                C_esperado == C_calc and D_esperado == D_calc):
                print("FIRMA VALIDA")
                return True
            else:
                print("FIRMA INVALIDA")
                return False
                
        except Exception:
            print("Error al verificar la firma.")
            return False
    
    def calcular_hash_documento(self, contenido):
        """
        Calcular hash ToyMDMA del documento usando ISA
        """
        try:
            from isa_pipeline_hash import ISAPipelineHashProcessor
            processor = ISAPipelineHashProcessor()
            
            # Procesar en bloques de 8 bytes
            bloques = [contenido[i:i+8] for i in range(0, len(contenido), 8)]
            
            # Padding del ultimo bloque si es necesario
            if len(bloques[-1]) < 8:
                bloques[-1] = bloques[-1].ljust(8, b'\x00')
            
            # Valores iniciales del hash ToyMDMA
            A = 0x0123456789ABCDEF
            B = 0xFEDCBA9876543210
            C = 0x1111111111111111
            D = 0x2222222222222222
            
            # Procesar cada bloque
            for bloque in bloques:
                data_block = int.from_bytes(bloque, 'little')
                A, B, C, D, _ = processor.hash_block_with_isa(A, B, C, D, data_block)
            
            return A, B, C, D
            
        except Exception:
            # Fallback simple si no hay ISA disponible
            return 0, 0, 0, 0

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Verificar archivo especifico
        archivo = sys.argv[1]
        verificador = VerificadorBoveda()
        verificador.verificar_firma(archivo)
    else:
        print("Uso: python verificador_boveda.py <archivo.bin>")
    
    def verificar_archivo_firmado(self, archivo_firmado_path):
        """
        Verificar si un archivo contiene una firma valida de la boveda
        
        Args:
            archivo_firmado_path: Ruta al archivo .bin firmado
            
        Returns:
            dict: Resultado de la verificacion
        """
        if not os.path.exists(archivo_firmado_path):
            return {
                'valido': False,
                'error': f'Archivo no encontrado: {archivo_firmado_path}',
                'detalles': {}
            }
        
        try:
            print(f"=== VERIFICACION DE FIRMA DE BOVEDA ===")
            print(f"Archivo: {archivo_firmado_path}")
            
            # 1. Leer y separar archivo firmado
            with open(archivo_firmado_path, 'rb') as f:
                contenido_completo = f.read()
            
            if len(contenido_completo) < 32:
                return {
                    'valido': False,
                    'error': 'Archivo demasiado pequeño para contener firma',
                    'detalles': {}
                }
            
            # Separar contenido original y firma
            contenido_original = contenido_completo[:-32]
            firma_bytes = contenido_completo[-32:]
            
            print(f"Tamano documento: {len(contenido_original)} bytes")
            print(f"Tamano firma: {len(firma_bytes)} bytes")
            
            # 2. Extraer componentes de la firma
            s1, s2, s3, s4 = struct.unpack('<QQQQ', firma_bytes)
            print(f"Firma leida: S1=0x{s1:016X}, S2=0x{s2:016X}, S3=0x{s3:016X}, S4=0x{s4:016X}")
            
            # 3. Aplicar operacion inversa de la firma (descifrado)
            A_esperado = s1 ^ self.boveda_key
            B_esperado = s2 ^ self.boveda_key
            C_esperado = s3 ^ self.boveda_key
            D_esperado = s4 ^ self.boveda_key
            
            print(f"Hash esperado (descifrado): A=0x{A_esperado:016X}, B=0x{B_esperado:016X}, C=0x{C_esperado:016X}, D=0x{D_esperado:016X}")
            
            # 4. Recalcular hash del documento usando proceso directo
            hash_recalculado = self.calcular_hash_documento(contenido_original)
            A_calc, B_calc, C_calc, D_calc = hash_recalculado
            
            print(f"Hash recalculado: A=0x{A_calc:016X}, B=0x{B_calc:016X}, C=0x{C_calc:016X}, D=0x{D_calc:016X}")
            
            # 5. Comparar hashes
            hash_coincide = (A_esperado == A_calc and B_esperado == B_calc and 
                           C_esperado == C_calc and D_esperado == D_calc)
            
            # 6. Verificacion adicional usando proceso inverso (demostracion ISA)
            print(f"\n--- Verificacion usando proceso inverso ISA ---")
            self.demostrar_proceso_inverso(A_calc, B_calc, C_calc, D_calc, contenido_original)
            
            resultado = {
                'valido': hash_coincide,
                'archivo': archivo_firmado_path,
                'tamano_documento': len(contenido_original),
                'detalles': {
                    'hash_esperado': (A_esperado, B_esperado, C_esperado, D_esperado),
                    'hash_calculado': (A_calc, B_calc, C_calc, D_calc),
                    'firma_original': (s1, s2, s3, s4),
                    'clave_boveda': self.boveda_key
                }
            }
            
            if hash_coincide:
                print(f"\nFIRMA VALIDA - El archivo pertenece a la boveda")
            else:
                print(f"\nFIRMA INVALIDA - El archivo NO pertenece a la boveda")
            
            return resultado
            
        except Exception as e:
            return {
                'valido': False,
                'error': f'Error durante verificacion: {str(e)}',
                'detalles': {}
            }
    
    def calcular_hash_documento_con_isa(self, contenido):
        """
        Calcular hash ToyMDMA del documento usando ISA (proceso directo)
        """
        # Procesar en bloques de 8 bytes
        bloques = [contenido[i:i+8] for i in range(0, len(contenido), 8)]
        
        # Padding del ultimo bloque
        if len(bloques[-1]) < 8:
            bloques[-1] = bloques[-1].ljust(8, b'\x00')
        
        # Valores iniciales
        A = 0x0123456789ABCDEF
        B = 0xFEDCBA9876543210
        C = 0x1111111111111111
        D = 0x2222222222222222
        
        # Usar el ISA para procesar cada bloque (proceso directo)
        from isa_pipeline_hash import ISAPipelineHashProcessor
        processor_hash = ISAPipelineHashProcessor()
        
        for bloque in bloques:
            data_block = int.from_bytes(bloque, 'little')
            A, B, C, D, _ = processor_hash.hash_block_with_isa(A, B, C, D, data_block)
        
        return A, B, C, D

    def calcular_hash_documento(self, contenido):
        """
        Calcular hash ToyMDMA del documento (proceso directo simplificado)
        """
        return self.calcular_hash_documento_con_isa(contenido)
    
    def extraer_componentes_archivo_firmado(self, archivo_firmado_path):
        """
        Extraer los componentes de un archivo firmado para su uso en el pipeline
        
        Args:
            archivo_firmado_path: Ruta al archivo .bin firmado
            
        Returns:
            dict: Componentes extraidos o None si hay error
        """
        if not os.path.exists(archivo_firmado_path):
            return None
        
        try:
            with open(archivo_firmado_path, 'rb') as f:
                contenido_completo = f.read()
            
            if len(contenido_completo) < 32:
                return None
            
            # Separar contenido original y firma
            contenido_original = contenido_completo[:-32]
            firma_bytes = contenido_completo[-32:]
            
            # Extraer componentes de la firma
            s1, s2, s3, s4 = struct.unpack('<QQQQ', firma_bytes)
            
            # Calcular hash del documento
            hash_documento = self.calcular_hash_documento_con_isa(contenido_original)
            
            # Descifrar firma (aplicar XOR con clave de boveda)
            A_esperado = s1 ^ self.boveda_key
            B_esperado = s2 ^ self.boveda_key
            C_esperado = s3 ^ self.boveda_key
            D_esperado = s4 ^ self.boveda_key
            
            return {
                'archivo': archivo_firmado_path,
                'tamano_documento': len(contenido_original),
                'firma_cifrada': (s1, s2, s3, s4),
                'hash_esperado': (A_esperado, B_esperado, C_esperado, D_esperado),
                'hash_calculado': hash_documento,
                'clave_boveda': self.boveda_key,
                'contenido_original': contenido_original
            }
            
        except Exception as e:
            print(f"Error extrayendo componentes: {e}")
            return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Verificar archivo especifico
        archivo = sys.argv[1]
        verificador = VerificadorBoveda()
        resultado = verificador.verificar_archivo_firmado(archivo)
        
        if resultado['valido']:
            print("FIRMA VALIDA")
            sys.exit(0)
        else:
            print("FIRMA INVALIDA")
            if 'error' in resultado:
                print(f"Error: {resultado['error']}")
            sys.exit(1)
    else:
        # Modo interactivo
        pass 