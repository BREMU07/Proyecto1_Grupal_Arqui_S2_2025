# -------------------------
# main.py - Sistema ToyMDMA con Pipeline ISA y Condicionales
# -------------------------
from isa_pipeline_hash import ISAPipelineHashProcessor
import os

<<<<<<< Updated upstream
def main():
    """Funcion principal que demuestra el sistema completo ToyMDMA con ISA"""
    
    print("=== SISTEMA TOYMDMA CON PIPELINE ISA ===\n")
    
    # Archivo objetivo: file_loader.py
    target_file = "c:/Users/menei/Documents/GitHub/Proyecto1_Grupal_Arqui_S2_2025/ISA/prueba.txt"
    
    if not os.path.exists(target_file):
        print(f"Error: No se encuentra el archivo {target_file}")
        return
    
    print(f"Archivo objetivo: {target_file}")
    print(f"Tamano: {os.path.getsize(target_file)} bytes")
    
    try:
        # Crear procesador ISA
        processor = ISAPipelineHashProcessor()
        signed_file = f"{target_file}_signed.bin"
        
        print(f"\n=== FASE 1: HASH CON PIPELINE ISA ===")
        
        # Procesar archivo con pipeline ISA y condicionales
        hash_result = processor.toy_mdma_hash_isa(target_file)
        
        print(f"\n=== FASE 2: FIRMA DIGITAL ===")
        
        # Crear archivo firmado
        signature = processor.create_signed_file(target_file, signed_file)
        
        print(f"\n=== FASE 3: VERIFICACION DE FIRMA ===")
        
        # Verificar integridad del archivo firmado
        is_valid = processor.verify_signed_file(signed_file)
        
        print(f"\n=== RESULTADO FINAL ===")
        print(f"   Archivo procesado: {target_file}")
        print(f"   Archivo firmado: {signed_file}")
        print(f"   Hash ToyMDMA: 0x{hash_result:016X}")
        print(f"   Firma valida: {'SI' if is_valid else 'NO'}")
        
        # Mostrar estadisticas del archivo procesado
        original_size = os.path.getsize(target_file)
        signed_size = os.path.getsize(signed_file)
        
        print(f"\nEstadisticas del Sistema:")
        print(f"   Archivo original: {original_size} bytes")
        print(f"   Archivo firmado: {signed_size} bytes")
        print(f"   Overhead firma: {signed_size - original_size} bytes")
        print(f"   Bloques procesados: {(original_size + 7) // 8}")
        
    except Exception as e:
        print(f"Error durante el procesamiento: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()


=======
if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
>>>>>>> Stashed changes
