import os
import re
import random
import hashlib
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from sedes_selector import SeleccionSede

import db

CONTACTO_RECUPERACION = "Comunícate al WhatsApp: +502 5555-5555 o al correo: soporte@salon.com"

def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")
def correo_valido(s: str) -> bool:
    return bool(EMAIL_RE.match((s or "").strip()))

def _base_username(first_name: str, last_name: str) -> str:
    fi = (first_name.strip()[:1] or "x").lower()
    li = (last_name.strip()[:1] or "x").lower()
    return f"{fi}{li}"

def generar_username(first_name: str, last_name: str, intentos: int = 0) -> str:
    base = _base_username(first_name, last_name)
    tail = f"{random.randint(0, 999):03d}"
    candidate = f"{base}{tail}"
    if not db.usuario_existe(candidate):
        return candidate
    if intentos >= 5:
        for _ in range(1000):
            tail = f"{random.randint(0, 999):03d}"
            candidate = f"{base}{tail}"
            if not db.usuario_existe(candidate):
                return candidate
        return f"{base}{random.getrandbits(16)}"
    return generar_username(first_name, last_name, intentos + 1)

class VentanaRegistro(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Crear cuenta")
        self.resizable(False, False)

        cont = ttk.Frame(self, padding=10)
        cont.pack(fill="both", expand=True)

        ttk.Label(cont, text="Nombre:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(cont, text="Apellido:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(cont, text="Correo:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(cont, text="Contraseña:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(cont, text="Confirmar:").grid(row=4, column=0, sticky="e", padx=5, pady=5)

        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_correo = tk.StringVar()
        self.var_pass = tk.StringVar()
        self.var_pass2 = tk.StringVar()

        ttk.Entry(cont, textvariable=self.var_nombre).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(cont, textvariable=self.var_apellido).grid(row=1, column=1, padx=5, pady=5)
        ttk.Entry(cont, textvariable=self.var_correo).grid(row=2, column=1, padx=5, pady=5)
        ttk.Entry(cont, textvariable=self.var_pass, show="*").grid(row=3, column=1, padx=5, pady=5)
        ttk.Entry(cont, textvariable=self.var_pass2, show="*").grid(row=4, column=1, padx=5, pady=5)

        botones = ttk.Frame(cont)
        botones.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(botones, text="Crear cuenta", command=self.crear_cuenta).pack(side="left", padx=5)
        ttk.Button(botones, text="Cancelar", command=self.destroy).pack(side="left", padx=5)

        self.update_idletasks()
        self.geometry(self._centrar(360, 260))

    def _centrar(self, w, h):
        x = self.master.winfo_rootx()
        y = self.master.winfo_rooty()
        mw = self.master.winfo_width()
        mh = self.master.winfo_height()
        return f"+{x + (mw - w)//2}+{y + (mh - h)//2}"

    def crear_cuenta(self):
        nombre = self.var_nombre.get().strip()
        apellido = self.var_apellido.get().strip()
        correo = self.var_correo.get().strip()
        p1 = self.var_pass.get()
        p2 = self.var_pass2.get()

        if not nombre or not apellido or not correo or not p1 or not p2:
            messagebox.showwarning("Validación", "Por favor completa todos los campos.")
            return
        if not correo_valido(correo):
            messagebox.showwarning("Correo inválido", "Ingresa un correo válido.")
            return
        if p1 != p2:
            messagebox.showwarning("Contraseña", "Las contraseñas no coinciden.")
            return

        username = generar_username(nombre, apellido)
        try:
            db.insertar_usuario(username, nombre, apellido, correo, hash_password(p1))
        except Exception:
            messagebox.showerror("Error", "No se pudo crear el usuario. Intenta de nuevo.")
            return

        messagebox.showinfo(
            "Cuenta creada",
            f"Listo, tu usuario es: {username}\nGuárdalo para iniciar sesión."
        )
        self.destroy()

class AppLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("420x500")
        self.resizable(False, False)

        marco = ttk.Frame(self, padding=10)
        marco.pack(fill="both", expand=True)

        self.logo_img = None
        if os.path.exists("logo.png"):
            try:
                self.logo_img = tk.PhotoImage(file="logo.png")
                ttk.Label(marco, image=self.logo_img).pack(pady=10)
            except Exception:
                pass

        ttk.Label(marco, text="Inicio de sesión", font=("Segoe UI", 14, "bold")).pack(pady=(5, 15))

        form = ttk.Frame(marco)
        form.pack()

        ttk.Label(form, text="Usuario:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        ttk.Label(form, text="Contraseña:").grid(row=1, column=0, sticky="e", padx=5, pady=5)

        self.var_user = tk.StringVar()
        self.var_pass = tk.StringVar()

        ttk.Entry(form, textvariable=self.var_user).grid(row=0, column=1, padx=5, pady=5)
        ttk.Entry(form, textvariable=self.var_pass, show="*").grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(marco, text="Iniciar sesión", command=self.iniciar_sesion).pack(pady=(10, 5))
        ttk.Button(marco, text="Crear cuenta", command=self.abrir_registro).pack(pady=5)
        ttk.Button(marco, text="Olvidé mi contraseña", command=self.recuperar).pack(pady=5)

    def iniciar_sesion(self):
        username = self.var_user.get().strip()
        passwd = self.var_pass.get()

        if not username or not passwd:
            messagebox.showwarning("Validación", "Ingresa usuario y contraseña.")
            return

        user = db.obtener_usuario(username)
        if not user:
            messagebox.showerror("Error", "Usuario no encontrado.")
            return

        _id, _u, p_hash, fallos, locked = user
        if locked:
            messagebox.showerror("Bloqueado", "Usuario bloqueado por demasiados intentos fallidos.")
            return

        if hash_password(passwd) == p_hash:
            db.reset_intentos(username)
            self.withdraw()
            SeleccionSede(self)
            messagebox.showinfo("Bienvenido", f"Inicio de sesión correcto.\nUsuario: {username}")
        else:
            restantes = max(0, 3 - (fallos + 1))
            nuevos_fallos = db.registrar_fallo(username)
            if restantes == 0 or nuevos_fallos >= 3:
                messagebox.showerror("Bloqueado", "Contraseña incorrecta. Usuario BLOQUEADO.")
            else:
                messagebox.showerror("Error", f"Contraseña incorrecta. Intentos restantes: {restantes}")

    def abrir_registro(self):
        VentanaRegistro(self)

    def recuperar(self):
        messagebox.showinfo("Recuperar contraseña", CONTACTO_RECUPERACION)

if __name__ == "__main__":
    db.crear_bd_y_tabla()
    app = AppLogin()
    app.mainloop()