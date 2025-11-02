import tkinter as tk
from tkinter import messagebox

COLOR_LATERAL = "#9BB1FF"
COLOR_BTN     = "#7A93E5"
COLOR_TXT     = "#000000"

class SideBar(tk.Frame):
    def __init__(self, master, on_exit=None):
        super().__init__(master, bg=COLOR_LATERAL, width=200)
        self.on_exit = on_exit
        self.pack_propagate(False)

        logo = tk.Canvas(self, width=120, height=120, bg=COLOR_LATERAL, highlightthickness=0)
        logo.create_oval(10, 10, 110, 110, fill=COLOR_BTN, outline="")
        logo.create_text(60, 60, text="LOGO", fill="white", font=("Segoe UI", 12, "bold"))
        logo.pack(pady=16)

        for texto in ("GESTIÓN DE CITAS", "CALENDARIO", "REPORTE COBROS"):
            tk.Button(self, text=texto, bg=COLOR_BTN, fg=COLOR_TXT, bd=0,
                      height=2, cursor="hand2",
                      command=self._en_construccion).pack(fill="x", padx=16, pady=6)

        btn_salir = tk.Button(master, text="x", bg=COLOR_BTN, fg="black", bd=0,
                              cursor="hand2", command=self._cerrar)
        btn_salir.place(x=900, y=18, width=28, height=28)

    def _en_construccion(self):
        messagebox.showinfo("Próximamente", "Esta sección estará disponible pronto.")

    def _cerrar(self):
        if self.on_exit:
            self.on_exit()