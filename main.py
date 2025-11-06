import os
import re
import random
import hashlib
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
import db
from sedes_selector import SeleccionSede

# Paleta de colores
BG_PRIMARY = '#fccfd4'
BG_SECONDARY = '#fccfd4'
BG_CARDS = '#fccfd4'
ACCENT = '#da5d86'
TEXT = '#0b1011'
BUTTONS = '#01a6b2'
BUTTONS_SECONDARY = '#01a6b2'
SUCCESS = '#7CE5A3'
WARNING = '#FFD6A5'
ERROR = '#FFB7B7'

CONTACTO_RECUPERACION = "Comunícate al WhatsApp: +502 55152328 o al correo: soporte@salon.com"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE_DIR, "logo.png")

def _load_logo_scaled(path: str, max_w: int, max_h: int):
    try:
        if os.path.exists(path):
            img = tk.PhotoImage(file=path)
            w, h = img.width(), img.height()
            factor = max((w + max_w - 1) // max_w, (h + max_h - 1) // max_h, 1)
            if factor > 1:
                img = img.subsample(factor, factor)
            return img
    except Exception as e:
        print("Error cargando logo (main):", e)
    return None

# Verificación base de datos y seguridad
def correo_valido(s: str) -> bool:
    return bool(EMAIL_RE.match((s or "").strip()))

def hash_password(plain: str) -> str:
    return hashlib.sha256(plain.encode()).hexdigest()

def _base_username(first_name: str, last_name: str) -> str:
    fi = (first_name.strip()[:1] or "x").lower()
    li = (last_name.strip()[:1] or "x").lower()
    return f"{fi}{li}"

def generar_username(first_name: str, last_name: str) -> str:
    base = _base_username(first_name, last_name)
    stack = [f"{random.randint(0, 999):03d}" for _ in range(10)]
    while True:
        if not stack:
            stack = [f"{random.randint(0, 999):03d}" for _ in range(10)]
        tail = stack.pop()
        candidate = f"{base}{tail}"
        if not db.usuario_existe(candidate):
            return candidate

def _load_icon(path: str, target_px: int = 22):
    try:
        if os.path.exists(path):
            img = tk.PhotoImage(file=path)
            w, h = img.width(), img.height()
            factor = max(w // target_px, h // target_px, 1)
            if factor > 1:
                img = img.subsample(factor, factor)
            return img
    except Exception:
        pass
    return None

# Estilo
def aplicar_estilos_ttk(root: tk.Tk):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except:
        pass

    root.configure(bg=BG_PRIMARY)
    style.configure(".", foreground=TEXT)

    # Frames
    style.configure("Card.TFrame", background=BG_CARDS)
    style.configure("Main.TFrame", background=BG_PRIMARY)

    # Labels
    style.configure("Title.TLabel", background=BG_PRIMARY, foreground=TEXT, font=("Segoe UI", 22, "bold"))
    style.configure("Label.TLabel", background=BG_PRIMARY, foreground=TEXT, font=("Segoe UI", 11))
    style.configure("CardLabel.TLabel", background=BG_CARDS, foreground=TEXT, font=("Segoe UI", 11))

    style.configure("Big.TEntry", fieldbackground="white", bordercolor=BG_SECONDARY, borderwidth=1, relief="flat")
    style.map("Big.TEntry",
              lightcolor=[("focus", ACCENT)],
              bordercolor=[("focus", ACCENT)])

    # Botones principales (rosa)
    style.configure("Primary.TButton",
                    background=BUTTONS,
                    foreground=TEXT,
                    font=("Segoe UI", 11, "bold"),
                    padding=8,
                    borderwidth=0)
    style.map("Primary.TButton",
              background=[("active", BUTTONS_SECONDARY)],
              relief=[("pressed", "sunken")])

    # Botones secundarios (rosa)
    style.configure("Secondary.TButton",
                    background=BUTTONS_SECONDARY,
                    foreground=TEXT,
                    font=("Segoe UI", 11, "bold"),
                    padding=8,
                    borderwidth=0)
    style.map("Secondary.TButton",
              background=[("active", BUTTONS)],
              relief=[("pressed", "sunken")])

    # Links de recuperar contraseña
    style.configure("Link.TLabel", background=BG_PRIMARY, foreground=ACCENT, font=("Segoe UI", 10, "bold"))


class VentanaRegistro(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Crear cuenta")
        self.resizable(False, False)
        self.configure(bg=BG_PRIMARY)

        cont_out = ttk.Frame(self, style="Main.TFrame", padding=20)
        cont_out.pack(fill="both", expand=True)

        card = ttk.Frame(cont_out, style="Card.TFrame", padding=20)
        card.pack(fill="both", expand=True)

        titulo = ttk.Label(card, text="Crear cuenta", style="CardLabel.TLabel", font=("Segoe UI", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        ttk.Label(card, text="Nombre:", style="CardLabel.TLabel").grid(row=1, column=0, sticky="e", padx=8, pady=6)
        ttk.Label(card, text="Apellido:", style="CardLabel.TLabel").grid(row=2, column=0, sticky="e", padx=8, pady=6)
        ttk.Label(card, text="Correo:", style="CardLabel.TLabel").grid(row=3, column=0, sticky="e", padx=8, pady=6)
        ttk.Label(card, text="Contraseña:", style="CardLabel.TLabel").grid(row=4, column=0, sticky="e", padx=8, pady=6)
        ttk.Label(card, text="Confirmar:", style="CardLabel.TLabel").grid(row=5, column=0, sticky="e", padx=8, pady=6)

        self.var_nombre = tk.StringVar()
        self.var_apellido = tk.StringVar()
        self.var_correo = tk.StringVar()
        self.var_pass = tk.StringVar()
        self.var_pass2 = tk.StringVar()

        e1 = ttk.Entry(card, textvariable=self.var_nombre, style="Big.TEntry", width=36)
        e2 = ttk.Entry(card, textvariable=self.var_apellido, style="Big.TEntry", width=36)
        e3 = ttk.Entry(card, textvariable=self.var_correo, style="Big.TEntry", width=36)
        e4 = ttk.Entry(card, textvariable=self.var_pass, style="Big.TEntry", show="*", width=36)
        e5 = ttk.Entry(card, textvariable=self.var_pass2, style="Big.TEntry", show="*", width=36)

        e1.grid(row=1, column=1, padx=8, pady=6, sticky="we")
        e2.grid(row=2, column=1, padx=8, pady=6, sticky="we")
        e3.grid(row=3, column=1, padx=8, pady=6, sticky="we")
        e4.grid(row=4, column=1, padx=8, pady=6, sticky="we")
        e5.grid(row=5, column=1, padx=8, pady=6, sticky="we")

        botones = ttk.Frame(card, style="Card.TFrame")
        botones.grid(row=6, column=0, columnspan=2, pady=(14, 0))
        ttk.Button(botones, text="Crear cuenta", style="Primary.TButton", command=self.crear_cuenta)\
            .pack(side="left", padx=6)
        ttk.Button(botones, text="Cancelar", style="Secondary.TButton", command=self.destroy)\
            .pack(side="left", padx=6)

        self.update_idletasks()
        self.geometry(self._centrar(520, 360))

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
        messagebox.showinfo("Cuenta creada", f"Listo, tu usuario es: {username}\nGuárdalo para iniciar sesión.")
        self.destroy()


class AppLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Login")
        self.geometry("1366x788")
        self.resizable(False, False)

        aplicar_estilos_ttk(self)

        main = ttk.Frame(self, style="Main.TFrame", padding=24)
        main.pack(fill="both", expand=True)

        card = ttk.Frame(main, style="Main.TFrame")
        card.place(relx=0.5, rely=0.5, anchor="center")

        self.logo_img = _load_logo_scaled(LOGO_PATH, max_w=700, max_h=220)
        if self.logo_img:
            tk.Label(card, image=self.logo_img, bg=BG_PRIMARY, borderwidth=0, highlightthickness=0)\
                .grid(row=0, column=0, columnspan=2, pady=(10, 18))
        else:
            ttk.Label(card, text="LOGO", style="Title.TLabel")\
                .grid(row=0, column=0, columnspan=2, pady=(10, 18))

        # Título
        ttk.Label(card, text="Inicio de sesión", style="Title.TLabel").grid(row=1, column=0, columnspan=2, pady=(0, 8))

        form = ttk.Frame(card, style="Main.TFrame")
        form.grid(row=2, column=0, columnspan=2, pady=(6, 0))

        ttk.Label(form, text="Usuario:", style="Label.TLabel").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        ttk.Label(form, text="Contraseña:", style="Label.TLabel").grid(row=2, column=0, sticky="w", padx=6, pady=6)

        self.var_user = tk.StringVar()
        self.var_pass = tk.StringVar()

        entry_width = 64
        ttk.Entry(form, textvariable=self.var_user, style="Big.TEntry", width=entry_width)\
            .grid(row=1, column=0, columnspan=2, padx=6, pady=4, sticky="we")

        self._pwd_shown = False
        self.ent_pass = ttk.Entry(form, textvariable=self.var_pass, show="*", style="Big.TEntry", width=entry_width-6)
        self.ent_pass.grid(row=3, column=0, padx=6, pady=4, sticky="we")

        self._img_eye_open  = _load_icon("eye.png", target_px=22)
        self._img_eye_closed = _load_icon("eye_off.png", target_px=22)

        btn_kwargs = {
            "style": "Secondary.TButton",
            "command": self._toggle_password,
            "width": 2,
        }
        if self._img_eye_closed:
            self.btn_toggle_pwd = ttk.Button(form, image=self._img_eye_closed, **btn_kwargs)
        else:
            self.btn_toggle_pwd = ttk.Button(form, text="👁", **btn_kwargs)
        self.btn_toggle_pwd.grid(row=3, column=1, padx=(4, 6), pady=4, sticky="w")

        link_rec = ttk.Label(form, text="Recuperar contraseña", style="Link.TLabel", cursor="hand2")
        link_rec.grid(row=4, column=0, sticky="w", padx=6, pady=(6, 0))
        link_rec.bind("<Button-1>", lambda e: self.recuperar())


        buttons = ttk.Frame(card, style="Main.TFrame")
        buttons.grid(row=5, column=0, columnspan=2, pady=(26, 0), sticky="w")

        ttk.Button(buttons, text="Iniciar sesión", style="Primary.TButton", command=self.iniciar_sesion)\
            .pack(side="left", padx=(6, 6))
        ttk.Button(buttons, text="Crear cuenta", style="Secondary.TButton", command=self.abrir_registro)\
            .pack(side="left", padx=(6, 6))

        card.grid_columnconfigure(0, minsize=320)

        self.logo_img = getattr(self, "logo_img", None)

    def _toggle_password(self):
        self._pwd_shown = not self._pwd_shown
        self.ent_pass.configure(show="" if self._pwd_shown else "*")
        if self._pwd_shown:
            if self._img_eye_open:
                self.btn_toggle_pwd.configure(image=self._img_eye_open, text="")
            else:
                self.btn_toggle_pwd.configure(text="👁")
        else:
            if self._img_eye_closed:
                self.btn_toggle_pwd.configure(image=self._img_eye_closed, text="")
            else:
                self.btn_toggle_pwd.configure(text="👁")

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

print("CWD:", os.getcwd())
print("LOGO_PATH:", LOGO_PATH, "exists?", os.path.exists(LOGO_PATH))


db.crear_bd_y_tabla()
app = AppLogin()
app.mainloop()