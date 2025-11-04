import tkinter as tk
from tkinter import messagebox
import db
from inventario import InventarioWindow

COLOR_BG    = "#F7FFF7"
COLOR_PANEL = "#D9FFE1"
COLOR_CARD  = "#7CE5A3"
COLOR_TXT   = "#000000"

class SeleccionSede(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Selección de sede")
        self.geometry("950x560")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.sede_seleccionada_id = None

        db.crear_tabla_sedes()
        db.ensure_sedes_iniciales()

        tk.Label(self, text="Selección de sede", bg=COLOR_BG, fg=COLOR_TXT,
                 font=("Segoe UI", 26, "bold")).pack(pady=(12, 6))

        panel = tk.Frame(self, bg=COLOR_PANEL)
        panel.pack(expand=True, fill="both", padx=20, pady=20)

        self.cards_area = tk.Frame(panel, bg=COLOR_PANEL)
        self.cards_area.place(relx=0.5, rely=0.52, anchor="center", width=860, height=420)

        cont_btn = tk.Frame(panel, bg=COLOR_PANEL)
        cont_btn.place(x=20, y=370, width=820, height=44)

        tk.Button(cont_btn, text="Eliminar sede", bg=COLOR_CARD, fg=COLOR_TXT, bd=0,
                  cursor="hand2", command=self._eliminar).pack(side="left", padx=4)
        tk.Button(cont_btn, text="Nueva sede", bg=COLOR_CARD, fg=COLOR_TXT, bd=0,
                  cursor="hand2", command=self._nueva).pack(side="right", padx=4)

        self._render()

    def _render(self):
        for w in self.cards_area.winfo_children():
            w.destroy()
        sedes = db.listar_sedes()

        col, row, max_cols = 0, 0, 2
        for (sid, nombre, ubicacion) in sedes:
            card = tk.Frame(self.cards_area, bg=COLOR_CARD)
            card.grid(row=row, column=col, padx=60, pady=20, ipadx=80, ipady=80)
            card.bind("<Button-1>", lambda e, i=sid: self._abrir_inventario(i))

            tk.Label(card, text=nombre, bg=COLOR_CARD, fg=COLOR_TXT,
                     font=("Segoe UI", 18, "bold")).pack()
            tk.Label(card, text=ubicacion, bg=COLOR_CARD, fg=COLOR_TXT,
                     font=("Segoe UI", 12, "bold")).pack()

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def _abrir_inventario(self, sede_id: int):
        InventarioWindow(self, sede_id)

    def _nueva(self):
        from tkinter import simpledialog
        nombre = simpledialog.askstring("Nueva sede", "Nombre:", parent=self)
        if not nombre:
            return
        ubicacion = simpledialog.askstring("Nueva sede", "Ubicación:", parent=self) or "Ubicación"
        db.insertar_sede(nombre.strip(), ubicacion.strip())
        self._render()

    def _eliminar(self):
        from tkinter import simpledialog
        sid = simpledialog.askinteger("Eliminar sede", "ID de sede a eliminar:", parent=self, minvalue=1)
        if not sid:
            return
        if not db.obtener_sede(sid):
            messagebox.showerror("Eliminar", "No existe una sede con ese ID.")
            return
        if messagebox.askyesno("Eliminar", "¿Eliminar esta sede y su inventario?"):
            db.eliminar_sede(sid)
            self._render()