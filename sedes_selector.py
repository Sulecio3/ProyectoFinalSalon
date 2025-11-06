import tkinter as tk
from tkinter import messagebox
import db
from inventario import InventarioWindow

COLOR_BG    = "#F3D6DD"
COLOR_PANEL = "#EEC1CD"
COLOR_CARD  = "#E4A6B5"
COLOR_TXT   = "#0B1011"
BUTTONS     = "#01A6B2"

class SeleccionSede(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Selección de sede")
        self.geometry("1366x788")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.sede_seleccionada_id = None

        db.crear_tabla_sedes()
        db.ensure_sedes_iniciales()

        tk.Label(
            self, text="Selección de sede", bg=COLOR_BG, fg=COLOR_TXT,
            font=("Segoe UI", 36, "bold")
        ).pack(pady=(18, 8))

        panel = tk.Frame(self, bg=COLOR_PANEL)
        panel.pack(expand=True, fill="both", padx=28, pady=22)

        self.cards_area = tk.Frame(panel, bg=COLOR_PANEL)
        self.cards_area.place(relx=0.5, rely=0.50, anchor="center", width=1180, height=540)

        btn_eliminar = tk.Button(
            panel, text="Eliminar sede", bg=BUTTONS, fg=COLOR_TXT, bd=0,
            activebackground=BUTTONS, cursor="hand2", command=self._eliminar
        )
        btn_eliminar.place(relx=0.02, rely=0.97, anchor="sw", width=140, height=36)

        btn_nueva = tk.Button(
            panel, text="Nueva sede", bg=BUTTONS, fg=COLOR_TXT, bd=0,
            activebackground=BUTTONS, cursor="hand2", command=self._nueva
        )
        btn_nueva.place(relx=0.98, rely=0.97, anchor="se", width=140, height=36)

        self._render()

    def _render(self):
        for w in self.cards_area.winfo_children():
            w.destroy()
        sedes = db.listar_sedes()

        col, row, max_cols = 0, 0, 2
        for (sid, nombre, ubicacion) in sedes:
            card = tk.Frame(self.cards_area, bg=COLOR_CARD)
            card.grid(row=row, column=col, padx=70, pady=28, ipadx=110, ipady=110)
            card.bind("<Button-1>", lambda e, i=sid: self._abrir_inventario(i))

            tk.Label(
                card, text=nombre, bg=COLOR_CARD, fg=COLOR_TXT,
                font=("Segoe UI", 22, "bold")
            ).pack(pady=(0, 6))

            tk.Label(
                card, text=ubicacion, bg=COLOR_CARD, fg=COLOR_TXT,
                font=("Segoe UI", 12, "bold")
            ).pack()

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