import tkinter as tk
from tkinter import ttk, Menu, filedialog, messagebox
from interfaz.pipeline_simple_window import Simple_Pipeline_Window
import sys
import os

# Agregar el directorio padre al path para importar verificador_boveda
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from verificador_boveda import VerificadorBoveda

class MainWindow:
    def __init__(self, master):
        self.master = master
        self.master.title("Simulator ISA and Signing")
        self.master.geometry("800x600")
        self.superuser_logged_in = False
        self.create_widgets()
        self.create_menu()

    def create_widgets(self):
        self.label = tk.Label(self.master, text="Arquitectura del Set de Instrucciones (ISA)", font=("Helvetica", 24))
        self.label.pack(pady=20)

        self.frame = tk.Frame(self.master)
        self.frame.pack(pady=10)

        # Crea un Frame interno para alinear los botones verticalmente
        self.button_frame = tk.Frame(self.frame)
        self.button_frame.pack(pady=10)

        self.pipeline_button = tk.Button(self.button_frame, text="Cargar archivo", command=self.open_pipeline_simple, font=("Helvetica", 16))
        self.pipeline_button.pack(pady=5, padx=10)

        # Boton de login
        self.login_button = tk.Button(self.button_frame, text="Login", command=self.login_prompt, font=("Helvetica", 16))
        self.login_button.pack(pady=5, padx=10)

        # Botón para salir
        self.exit_button = tk.Button(self.button_frame, text="Exit", command=self.master.quit, font=("Helvetica", 16))
        self.exit_button.pack(pady=5, padx=10)

    def login_prompt(self):
        import tkinter.simpledialog
        password = tkinter.simpledialog.askstring("Login", "Contraseña:", show='*', parent=self.master)
        if password is None:
            return
        # Contraseña fija para demostración
        if password == "superuser":
            self.superuser_logged_in = True
            print("Logeado como superusuario")
        else:
            print("Contraseña incorrecta: vuelva a intentarlo")

    def create_menu(self):
        self.menubar = Menu(self.master)
        self.master.config(menu=self.menubar)

        self.file_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open", command=self.open_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.master.quit)

        self.help_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.help_menu.add_command(label="About", command=self.show_about)

    def open_pipeline_simple(self):
        pipeline_simple_window = tk.Toplevel(self.master)
        pipeline_simple_window.main_window = self
        Simple_Pipeline_Window(pipeline_simple_window)
    
    def open_file(self):
        pass

    def show_about(self):
        about_window = tk.Toplevel(self.master)
        about_window.title("About Original ISA and Signing")
        about_window.geometry("400x300")
        label = tk.Label(about_window, text="Original ISA and Signing\nVersion 1.0\n\n🔒 Con Verificador de Bóveda", font=("Helvetica", 14), justify=tk.CENTER)
        label.pack(expand=True, pady=20)
