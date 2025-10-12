import tkinter as tk
from tkinter import filedialog, messagebox
import time
from simple_pipeline import Simple_Pipeline
from assembler import Assembler
from isa_pipeline_hash import ISAPipelineHashProcessor
from execution_statistics import ExecutionStatistics
import os

class Simple_Pipeline_Window:
    def __init__(self, master):
        self.master = master
        self.master.title("Segmentado sin riesgos")
        self.create_widgets()
        self.segmentado = Simple_Pipeline()
        self.assembler = Assembler()
        self.execution_stats = ExecutionStatistics()
        # Pipeline ToyMDMA para hash
        self.toymdma_instructions = self.assembler.assemble(ISAPipelineHashProcessor().create_toymdata_program())
        self.start_time = None
        self.execution_time = 0
        self.cycle_time_ns = 10  # Suponiendo 10 ns por ciclo
        self.num_instructions = 0

    def create_widgets(self):
        self.main_frame = tk.Frame(self.master, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.controls_frame = tk.Frame(self.main_frame)
        self.controls_frame.pack(fill=tk.X, pady=5)

        self.load_button = tk.Button(self.controls_frame, text="Load Program", command=self.load_program)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.run_button = tk.Button(self.controls_frame, text="Run Program", command=self.run_program)
        self.run_button.pack(side=tk.LEFT, padx=5)

        self.step_button = tk.Button(self.controls_frame, text="Step", command=self.step_program)
        self.step_button.pack(side=tk.LEFT, padx=5)

        self.run_timed_button = tk.Button(self.controls_frame, text="Run Timed", command=self.run_timed_program)
        self.run_timed_button.pack(side=tk.LEFT, padx=5)

        # Botón para procesar archivo ToyMDMA
        self.hash_file_button = tk.Button(self.controls_frame, text="Load & Hash File", command=self.load_sign_and_verify_file)
        self.hash_file_button.pack(side=tk.LEFT, padx=5)
        

        self.status_frame = tk.Frame(self.main_frame)
        self.status_frame.pack(fill=tk.X, pady=5)

        self.cycle_label = tk.Label(self.status_frame, text="Cycle: 0")
        self.cycle_label.pack(side=tk.LEFT, padx=5)

        self.time_label = tk.Label(self.status_frame, text="Execution Time: 0.0s")
        self.time_label.pack(side=tk.LEFT, padx=5)

        self.pc_label = tk.Label(self.status_frame, text="PC: 0x00000000")
        self.pc_label.pack(side=tk.LEFT, padx=5)

         # --- Mostrar las 5 etapas del pipeline ---
        self.pipeline_frame = tk.Frame(self.main_frame)
        self.pipeline_frame.pack(fill=tk.X, pady=10)

        stages = ["IF", "ID", "EX", "MEM", "WB"]
        self.stage_labels = []
        for stage in stages:
            lbl = tk.Label(self.pipeline_frame, text=f"{stage}\n----", width=12, height=3, relief="ridge", bg="lightgray")
            lbl.pack(side=tk.LEFT, padx=5)
            self.stage_labels.append(lbl)

        separator = tk.Frame(self.main_frame, height=2, bd=1, relief=tk.SUNKEN)
        separator.pack(fill=tk.X, pady=10)

        self.data_frame = tk.Frame(self.main_frame)
        self.data_frame.pack(fill=tk.BOTH, expand=True)

        self.registers_label = tk.Label(self.data_frame, text="Registers", font=("Helvetica", 14))
        self.registers_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        self.registers_text = tk.Text(self.data_frame, height=10, width=30)
        self.registers_text.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        self.memory_label = tk.Label(self.data_frame, text="Memory", font=("Helvetica", 14))
        self.memory_label.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.memory_text = tk.Text(self.data_frame, height=10, width=30)
        self.memory_text.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        self.assembly_label = tk.Label(self.data_frame, text="Assembly Code", font=("Helvetica", 14))
        self.assembly_label.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        self.assembly_text = tk.Text(self.data_frame, height=10, width=80)
        self.assembly_text.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        self.output_label = tk.Label(self.data_frame, text="Output", font=("Helvetica", 14))
        self.output_label.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        self.output_text = tk.Text(self.data_frame, height=10, width=80)
        self.output_text.grid(row=4, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)

        self.stats_label = tk.Label(self.data_frame, text="Statistics", font=("Helvetica", 14))
        self.stats_label.grid(row=0, column=2, columnspan=2, padx=8, pady=5)

        self.stats_text = tk.Text(self.data_frame, height=10, width=80)
        self.stats_text.grid(row=1, column=2, columnspan=2, padx=8, pady=5)


    
    def update_pipeline_stages(self):
        stages_instructions = [
            ("IF", self.segmentado.IF_ID),
            ("ID", self.segmentado.ID_EX),
            ("EX", self.segmentado.EX_MEM),
            ("MEM", self.segmentado.MEM_WB),
            ("WB", self.segmentado.MEM_WB),
        ]

        for i, (stage, reg) in enumerate(stages_instructions):
            if reg.valid:
                instr_hex = f"{reg.instruction:016X}"
                self.stage_labels[i].config(text=f"{stage}\n{instr_hex}", bg="lightgreen")
            else:
                self.stage_labels[i].config(text=f"{stage}\n----", bg="lightgray")
                        

    def load_program(self):
        # Abrir diálogo para seleccionar archivo
        file_path = filedialog.askopenfilename(
            title="Select Assembly File",
            filetypes=[("Assembly Files", "*.asm"), ("All Files", "*.*")]
        )
        if not file_path:
            return 

        try:
            # Leer el contenido del archivo
            with open(file_path, 'r') as f:
                assembly_code = f.read()

            # Pegar el contenido en el Text widget
            self.assembly_text.delete("1.0", tk.END)
            self.assembly_text.insert(tk.END, assembly_code)

            # Ensamblar y cargar programa en pipeline
            machine_code = self.assembler.assemble(assembly_code)
            self.segmentado.load_program(machine_code)
            self.num_instructions = len(machine_code)
            self.output_text.insert(tk.END, f"Loaded {file_path} ({self.num_instructions} instructions).\n")

        except Exception as e:
            self.output_text.insert(tk.END, f"Error loading program: {e}\n")

    def run_program(self):
        if not self.segmentado:
            messagebox.showwarning("Warning", "Load a program first.")
            return

        try:
            while self.segmentado.is_pipeline_active():
                output = self.segmentado.step()
                if output is None:
                    output = ""
                else:
                    output = str(output)
                self.output_text.insert(tk.END, output + "\n")
                self.output_text.see(tk.END)
                self.update_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Error during run: {e}")

    def run_timed_program(self):
        if self.start_time is None:
            self.start_time = time.time()
        self.master.after(1000, self.step_timed)

    def step_timed(self):
        if self.segmentado.pc < len(self.segmentado.memory):
            output = self.segmentado.step()
            self.execution_time = time.time() - self.start_time
            self.update_ui()
            self.output_text.insert(tk.END, output)
            self.master.after(1000, self.step_timed)
        else:
            self.record_statistics()
            self.output_text.insert(tk.END, "Program execution finished.\n")

    def step_program(self):
        if not self.segmentado:
            messagebox.showwarning("Warning", "Load a program first.")
            return

        try:
            output = self.segmentado.step()
            if output is None:
                output = ""
            else:
                output = str(output)
            self.output_text.insert(tk.END, output + "\n")
            self.output_text.see(tk.END)
            self.update_ui()
        except Exception as e:
            messagebox.showerror("Error", f"Error during step: {e}")

    def record_statistics(self):
        num_cycles = self.segmentado.cycle
        num_instructions = self.num_instructions  
        cpi = num_cycles / num_instructions
        self.execution_stats.add_execution(num_cycles, num_instructions, self.cycle_time_ns,0)
        self.display_statistics()

    def display_statistics(self):
        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert(tk.END, f"{'Execution':<10}{'Cycles':<10}{'Instructions':<15}{'CPI':<10}{'Time (ns)':<15}\n")
        for i, stat in enumerate(self.execution_stats.get_statistics()):
            num_cycles = f"{stat['num_cycles']:}"
            num_instructions = f"{stat['num_instructions']:}"
            cpi = f"{stat['cpi']:.2f}"
            execution_time_ns = f"{stat['execution_time_ns']:.2f}"
            stage = f"{stat['stage']:}"
            self.stats_text.insert(
                tk.END, 
                f"{i+1:<10}{num_cycles:<10}{num_instructions:<15}{cpi:<10}{execution_time_ns:<10}\n"
            )

    # ---------------- HASH Y FIRMA ----------------
    def hash_block_with_pipeline(self, A, B, C, D, data_block):
        """
        Procesa un bloque de datos usando el pipeline existente
        y devuelve valores finales junto con los pasos.
        """
        try:
            self.segmentado.load_program(self.toymdma_instructions)
            self.segmentado.registers[1] = data_block
            self.segmentado.registers[2] = A
            self.segmentado.registers[3] = B
            self.segmentado.registers[4] = C
            self.segmentado.registers[5] = D

            steps = 0
            max_steps = 50
            while self.segmentado.is_pipeline_active() and steps < max_steps:
                self.segmentado.step()
                steps += 1

            if steps >= max_steps:
                self.output_text.insert(tk.END, f"Warning: Pipeline excedió {max_steps} pasos\n")

            new_A = self.segmentado.registers[2] & 0xFFFFFFFFFFFFFFFF
            new_B = self.segmentado.registers[3] & 0xFFFFFFFFFFFFFFFF
            new_C = self.segmentado.registers[4] & 0xFFFFFFFFFFFFFFFF
            new_D = self.segmentado.registers[5] & 0xFFFFFFFFFFFFFFFF

            return new_A, new_B, new_C, new_D, steps
        except Exception as e:
            raise RuntimeError(f"Error usando pipeline: {e}")

    def load_sign_and_verify_file(self):
        """Cargar archivo, calcular hash, firmar, guardar y verificar"""
        file_path = filedialog.askopenfilename(
            title="Select File to Hash & Sign",
            filetypes=[("All Files", "*.*")]
        )
        if not file_path:
            return

        signed_file = f"{file_path}_signed.bin"
        try:
            self.output_text.insert(tk.END, f"\n=== PROCESANDO: {file_path} ===\n")
            processor = ISAPipelineHashProcessor()
            data = processor.load_file(file_path)

            # Inicializar hash
            A, B, C, D = 0x0123456789ABCDEF, 0xFEDCBA9876543210, 0x1111111111111111, 0x2222222222222222
            total_steps = 0

            # Bloques de 8 bytes
            blocks = [data[i:i+8] for i in range(0, len(data), 8)]
            if len(blocks[-1]) < 8:
                blocks[-1] = blocks[-1].ljust(8, b'\x00')

            # Procesar cada bloque
            for i, block in enumerate(blocks):
                data_block = int.from_bytes(block, 'little')
                A, B, C, D, steps = self.hash_block_with_pipeline(A, B, C, D, data_block)
                total_steps += steps
                self.output_text.insert(
                    tk.END,
                    f"Bloque {i+1}/{len(blocks)}: A=0x{A:016X}, B=0x{B:016X}, "
                    f"C=0x{C:016X}, D=0x{D:016X}, Steps={steps}\n"
                )
                self.output_text.see(tk.END)

            final_hash = (A ^ B ^ C ^ D) & 0xFFFFFFFFFFFFFFFF
            self.output_text.insert(tk.END, f"\nHash final: 0x{final_hash:016X}\n")

            # Crear archivo firmado
            signature_info = processor.create_signed_file(file_path, signed_file)
            signature = signature_info['signature']
            private_key = signature_info.get('private_key', processor.private_key)

            self.output_text.insert(
                tk.END,
                f"Archivo firmado: {signed_file}\n"
                f"Firma: S1=0x{signature[0]:016X}, S2=0x{signature[1]:016X}, "
                f"S3=0x{signature[2]:016X}, S4=0x{signature[3]:016X}\n"
            )

            
            result = processor.verify_signed_file(signed_file)
            is_valid = result["valid"]
            self.output_text.insert(
                tk.END,
                f"Verificación de firma: {'VÁLIDA' if is_valid else 'INVÁLIDA'}\n"
            )
            self.output_text.insert(
                tk.END,
                f"Detalles de firma: {result['signature']}\n"
            )
            self.output_text.insert(
                tk.END,
                f"Hash componentes: {result['hash_components']}\n"
            )




            # Estadísticas de tamaño
            original_size = os.path.getsize(file_path)
            signed_size = os.path.getsize(signed_file)
            overhead = signed_size - original_size
            self.output_text.insert(
                tk.END,
                f"\nTamaño original: {original_size} bytes\n"
                f"Tamaño archivo firmado: {signed_size} bytes\n"
                f"Overhead de firma: {overhead} bytes\n"
                f"Clave usada: 0x{private_key:016X}\n"
            )
            self.output_text.see(tk.END)

        except Exception as e:
            self.output_text.insert(tk.END, f"Error procesando archivo: {e}\n")
            self.output_text.see(tk.END)

    def update_ui(self):
        self.update_pipeline_stages()
        self.cycle_label.config(text=f"Cycle: {self.segmentado.cycle}")
        self.time_label.config(text=f"Execution Time: {self.execution_time:.2f}s")
        self.pc_label.config(text=f"PC: 0x{self.segmentado.pc:08X}")
        self.update_registers()
        self.update_memory()
        



    def update_registers(self):
        self.registers_text.delete('1.0', tk.END)
        for i in range(len(self.segmentado.registers)):
            self.registers_text.insert(tk.END, f"x{i}: 0x{self.segmentado.registers[i]:08X}\n")


    def update_memory(self):
        self.memory_text.delete('1.0', tk.END)
        for addr in range(0, len(self.segmentado.memory), 4):
            value = int.from_bytes(self.segmentado.memory[addr:addr+4], 'little')
            self.memory_text.insert(tk.END, f"0x{addr:08X}: 0x{value:08X}\n")

    def update_pipeline(self):
        self.pipeline_text.delete('1.0', tk.END)
        stages = ["IF", "ID", "EX", "MEM", "WB"]
        for stage_name, stage_content in zip(stages, self.segmentado.pipeline):
            self.pipeline_text.insert(tk.END, f"{stage_name}: {stage_content}\n")
        

if __name__ == "__main__":
    root = tk.Tk()
    app = Simple_Pipeline_Window(root)
    root.mainloop()
