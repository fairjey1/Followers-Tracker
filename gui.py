import customtkinter as ctk
import threading
import time
import json
import os
from cryptography.fernet import Fernet 
import main 
from main import ruta_config

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class GestorSeguridad:
    """Clase auxiliar para manejar el cifrado/descifrado"""
    def __init__(self):
        self.key_file = "secret.key"
        self.key_dir = "keys"
        if not os.path.exists(self.key_dir):
            os.makedirs(self.key_dir)
        self.key_file = os.path.join(self.key_dir, "secret.key")
        self.key = self.cargar_o_crear_key()
        self.cipher = Fernet(self.key)

    def cargar_o_crear_key(self):
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as file:
                return file.read()
        else:
            key = Fernet.generate_key()
            with open(self.key_file, "wb") as file:
                file.write(key)
            return key

    def encriptar(self, texto_plano):
        if not texto_plano: return ""
        token_bytes = self.cipher.encrypt(texto_plano.encode())
        return token_bytes.decode()

    def desencriptar(self, texto_encriptado):
        if not texto_encriptado: return ""
        try:
            token_bytes = texto_encriptado.encode()
            decrypted_bytes = self.cipher.decrypt(token_bytes)
            return decrypted_bytes.decode()
        except Exception:
            return ""

class InstagramTrackerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.security = GestorSeguridad()

        self.title("Instagram Tracker")
        self.geometry("600x700")
        self.resizable(False, False)
        self.config_file = "config.json"

        self.label_title = ctk.CTkLabel(self, text="Instagram Tracker", font=("Roboto", 24, "bold"))
        self.label_title.pack(pady=10)

        # pestañas
        self.tabview = ctk.CTkTabview(self, width=550, height=400)
        self.tabview.pack(pady=10)

        # Crear las dos pestañas
        self.tab_insta = self.tabview.add("Instagram")
        self.tab_email = self.tabview.add("Notificaciones (Email)")

        # Pestaña de instagram
        self.label_insta = ctk.CTkLabel(self.tab_insta, text="Credenciales de cuenta", font=("Roboto", 16))
        self.label_insta.pack(pady=10)

        self.entry_user = ctk.CTkEntry(self.tab_insta, placeholder_text="Tu Usuario Instagram", width=350)
        self.entry_user.pack(pady=5)

        self.entry_pass = ctk.CTkEntry(self.tab_insta, placeholder_text="Cookie de sesión", show="*", width=350)
        self.entry_pass.pack(pady=5)

        self.label_targets = ctk.CTkLabel(self.tab_insta, text="Cuentas a analizar (una por línea):")
        self.label_targets.pack(pady=(10, 0))
        
        self.textbox_targets = ctk.CTkTextbox(self.tab_insta, width=350, height=100)
        self.textbox_targets.pack(pady=5)

        # Pestaña de email
        self.label_email = ctk.CTkLabel(self.tab_email, text="Configuración GMAIL", font=("Roboto", 16))
        self.label_email.pack(pady=10)

        # agregamos los campos de email
        self.entry_email_sender = ctk.CTkEntry(self.tab_email, 
                                               placeholder_text="Email Remitente (ej: bot@gmail.com)", 
                                               placeholder_text_color="gray",
                                               width=350)
        self.entry_email_sender.pack(pady=5)

        self.entry_email_pass = ctk.CTkEntry(self.tab_email, 
                                             placeholder_text="Contraseña de Aplicación (16 dígitos)", 
                                             show="*", 
                                             placeholder_text_color="gray",
                                             width=350)
        self.entry_email_pass.pack(pady=5)

        self.entry_email_receiver = ctk.CTkEntry(self.tab_email, 
                                                 placeholder_text="Email Destino (¿A quién aviso?)", 
                                                 placeholder_text_color="gray",
                                                 width=350)
        self.entry_email_receiver.pack(pady=5)

        self.label_info = ctk.CTkLabel(self.tab_email, text="Nota: Usa una 'Contraseña de Aplicación' de Google,\nno tu contraseña normal.", text_color="gray", font=("Roboto", 10))
        self.label_info.pack(pady=10)

        # Elementos comunes (Botón y Logs)
        # [FIX 1] Agregamos width=400 (o un valor fijo grande) para que el botón no cambie de tamaño
        self.btn_start = ctk.CTkButton(self, 
                                       text="Guardar Configuración y Comenzar", 
                                       command=self.iniciar_proceso_thread,
                                       width=400,
                                       height=40) 
        self.btn_start.pack(pady=10)

        self.textbox_log = ctk.CTkTextbox(self, width=550, height=150)
        self.textbox_log.pack(pady=5)
        self.textbox_log.configure(state="disabled")

        self.cargar_configuracion()

    def log_message(self, message):
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")
        self.textbox_log.configure(state="disabled")

    # Métodos de persistencia
    def guardar_configuracion(self):
        pass_insta_enc = self.security.encriptar(self.entry_pass.get())
        pass_email_enc = self.security.encriptar(self.entry_email_pass.get())

        datos = {
            "usuario": self.entry_user.get(),
            "password_encrypted": pass_insta_enc,
            "targets": self.textbox_targets.get("1.0", "end-1c"),
            "email_sender": self.entry_email_sender.get(),
            "email_pass_encrypted": pass_email_enc,
            "email_receiver": self.entry_email_receiver.get()
        }
        try:
            with open(ruta_config, "w") as f: # Usamos ruta_config desde main.py para guardar en la carpeta correcta
                json.dump(datos, f)
        except Exception as e:
            self.log_message(f"Error guardando config: {e}")

    def cargar_configuracion(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    datos = json.load(f)
                    
                    # Instagram Data
                    self.entry_user.insert(0, datos.get("usuario", ""))
                    self.entry_pass.insert(0, self.security.desencriptar(datos.get("password_encrypted", "")))
                    self.textbox_targets.insert("1.0", datos.get("targets", ""))
                    
                    # Email Data
                    self.entry_email_sender.insert(0, datos.get("email_sender", ""))
                    self.entry_email_pass.insert(0, self.security.desencriptar(datos.get("email_pass_encrypted", "")))
                    self.entry_email_receiver.insert(0, datos.get("email_receiver", ""))

                    self.log_message("Configuración cargada exitosamente.")
            except Exception as e:
                self.log_message(f"Error cargando config: {e}")

    def iniciar_proceso_thread(self):
        self.guardar_configuracion()
        
        # Validación simple
        if not self.entry_user.get() or not self.entry_email_sender.get():
            self.log_message("ERROR: Faltan datos obligatorios.")
            return

        self.btn_start.configure(state="disabled", text="Procesando...")
        hilo = threading.Thread(target=self.ejecutar_logica)
        hilo.start()

    def ejecutar_logica(self):
        # 1. Recuperar datos limpios de la GUI
        insta_user = self.entry_user.get()
        insta_pass = self.entry_pass.get()
        
        # Empaquetamos la config de email en un diccionario para ser ordenados
        config_email = {
            "sender": self.entry_email_sender.get(),
            "password": self.entry_email_pass.get(),
            "receiver": self.entry_email_receiver.get()
        }
        
        # Procesamos la lista de objetivos
        raw_targets = self.textbox_targets.get("1.0", "end-1c")
        targets = [line.strip() for line in raw_targets.split('\n') if line.strip()]

        # 2. Validaciones finales (Opcional pero recomendado)
        if not targets:
            self.log_message("Error: No hay cuentas para analizar.")
            self.btn_start.configure(state="normal", text="Guardar Configuración y Comenzar")
            return

        # 3. LLAMADA AL BACKEND (main.py)
        # Pasamos 'self.log_message' como argumento.
        # Esto permite que main.py escriba directamente en tu caja de texto.
        try:
            main.iniciar_analisis(
                usuario=insta_user,
                session_id=insta_pass,
                targets=targets,
                email_config=config_email,
                log_callback=self.log_message 
            )
        except Exception as e:
            self.log_message(f"Error al ejecutar main: {e}")
        
        # 4. Restaurar botón al finalizar
        self.btn_start.configure(state="normal", text="Guardar Configuración y Comenzar")

if __name__ == "__main__":
    app = InstagramTrackerApp()
    app.mainloop()