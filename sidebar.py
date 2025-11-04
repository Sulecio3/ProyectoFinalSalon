import tkinter as tk
from tkinter import messagebox

COLOR_LATERAL = "#9BB1FF"
COLOR_BTN     = "#7A93E5"
COLOR_TXT     = "#000000"

class SideBar(tk.Frame):
    def __init__(self, master, on_exit=None, on_open_ventas=None, on_open_calendario=None):
        super().__init__(master, bg=COLOR_LATERAL, width=200)
        self.on_exit = on_exit
        self.on_open_ventas = on_open_ventas
        self.on_open_calendario = on_open_calendario

        self.pack_propagate(False)

        header = tk.Frame(self, bg=COLOR_LATERAL)
        header.pack(fill="x", pady=(10, 6))

        logo = tk.Canvas(header, width=120, height=120, bg=COLOR_LATERAL, highlightthickness=0)
        logo.create_oval(10, 10, 110, 110, fill=COLOR_BTN, outline="")
        logo.create_text(60, 60, text="LOGO", fill="white", font=("Segoe UI", 12, "bold"))
        logo.pack()

        def mk_btn(text, cmd):
            tk.Button(self, text=text, bg=COLOR_BTN, fg=COLOR_TXT, bd=0,
                      height=2, cursor="hand2", command=cmd).pack(fill="x", padx=16, pady=6)

        mk_btn("GESTIÓN DE CITAS", self._en_construccion)
        mk_btn("CALENDARIO", self._abrir_calendario)
        mk_btn("REPORTE COBROS", self._en_construccion)
        mk_btn("VENTAS", self._abrir_ventas)
        mk_btn("SALIR", self._cerrar)

    def _en_construccion(self):
        messagebox.showinfo("Próximamente", "Esta sección estará disponible pronto.")

    def _abrir_ventas(self):
        if self.on_open_ventas: self.on_open_ventas()
        else: messagebox.showinfo("Ventas", "No hay acción definida para VENTAS.")

    def _abrir_calendario(self):
        if self.on_open_calendario: self.on_open_calendario()
        else: messagebox.showinfo("Calendario", "No hay acción definida para CALENDARIO.")

    def _cerrar(self):
        if self.on_exit: self.on_exit()
