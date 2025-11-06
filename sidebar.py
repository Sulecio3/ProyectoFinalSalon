import tkinter as tk
from tkinter import messagebox
import os

COLOR_LATERAL = "#26b6c0"
COLOR_BTN     = "#1ea7b1e4"
COLOR_TXT     = "#000000"

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
    except Exception:
        pass
    return None

class SideBar(tk.Frame):
    def __init__(self, master, on_exit=None, on_open_ventas=None, on_open_reportes=None, on_open_calendario=None):
        super().__init__(master, bg=COLOR_LATERAL, width=200)
        self.on_exit = on_exit
        self.on_open_ventas = on_open_ventas
        self.on_open_reportes = on_open_reportes
        self.on_open_calendario = on_open_calendario
        self.pack_propagate(False)

        top = tk.Frame(self, bg=COLOR_LATERAL)
        top.pack(fill="x", pady=16)

        C_SIZE = 140
        C_RAD = 60
        self._canvas_logo = tk.Canvas(top, width=C_SIZE, height=C_SIZE, bg=COLOR_LATERAL, highlightthickness=0)
        self._canvas_logo.pack()

        cx, cy = C_SIZE // 2, C_SIZE // 2
        self._canvas_logo.create_oval(cx - C_RAD, cy - C_RAD, cx + C_RAD, cy + C_RAD, fill='white', outline="")

        self.logo_img = _load_logo_scaled(LOGO_PATH, max_w=int(C_RAD * 1.6), max_h=int(C_RAD * 1.6))
        if self.logo_img:
            self._canvas_logo.create_image(cx, cy, image=self.logo_img)
        else:
            self._canvas_logo.create_text(cx, cy, text="LOGO", fill="white", font=("Segoe UI", 12, "bold"))

        def mk_btn(text, cmd):
            tk.Button(self, text=text, bg=BUTTONS, fg=TEXT, bd=0, height=2, cursor="hand2", command=cmd)\
                .pack(fill="x", padx=16, pady=6)

        mk_btn("CALENDARIO", self._abrir_calendario)
        mk_btn("REPORTES", self._abrir_reportes)
        mk_btn("VENTAS", self._abrir_ventas)

        btn_salir = tk.Button(master, text="x", bg=BUTTONS, fg=TEXT, bd=0, cursor="hand2", command=self._cerrar)
        btn_salir.place(x=1340, y=18, width=28, height=28)

    def _abrir_ventas(self):
        if self.on_open_ventas:
            self.on_open_ventas()
        else:
            messagebox.showinfo("Ventas", "No hay acción definida para VENTAS.")

    def _abrir_reportes(self):
        if self.on_open_reportes:
            self.on_open_reportes()
        else:
            messagebox.showinfo("Reportes", "No hay acción definida para REPORTES.")

    def _abrir_calendario(self):
        if self.on_open_calendario:
            self.on_open_calendario()
        else:
            messagebox.showinfo("Calendario", "No hay acción definida para CALENDARIO.")

    def _cerrar(self):
        if self.on_exit:
            self.on_exit()
