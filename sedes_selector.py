import tkinter as tk
import tkinter.ttk as ttk
from tkinter import simpledialog, messagebox
import db

COLOR_BG = "#FFF7E9"
COLOR_PANEL = "#EDCDBF"
COLOR_CARD = "#CC6B5A"
COLOR_TXT = "#000000"

class SeleccionSede(tk.Toplevel):
    def __init__(self, master=None, on_open_sede=None):
        super().__init__(master)
        self.title("Selección de sede")
        self.geometry("900x550")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)
        self.on_open_sede = on_open_sede
        self.sede_seleccionada_id = None

        panel = tk.Frame(self, bg=COLOR_PANEL, bd=0, highlightthickness=0)
        panel.place(relx=0.5, rely=0.52, anchor="center", width=840, height=440)


        lbl = tk.Label(self, text="Selección de sede",
                       bg=COLOR_BG, fg=COLOR_TXT,
                       font=("Segoe UI", 28, "bold"))
        lbl.pack(pady=(15, 10))

        self.cards_area = tk.Frame(panel, bg=COLOR_PANEL)
        self.cards_area.place(x=20, y=20, width=800, height=350)

        cont_botones = tk.Frame(panel, bg=COLOR_PANEL)
        cont_botones.place(x=20, y=380, width=800, height=40)

        btn_eliminar = tk.Button(cont_botones, text="Eliminar sede",
                                 command=self.eliminar_sede,
                                 bg=COLOR_CARD, fg=COLOR_TXT, bd=0, padx=12, pady=6, cursor="hand2")
        btn_eliminar.pack(side="left")

        btn_nueva = tk.Button(cont_botones, text="Nueva sede",
                              command=self.nueva_sede,
                              bg=COLOR_CARD, fg=COLOR_TXT, bd=0, padx=12, pady=6, cursor="hand2")
        btn_nueva.pack(side="right")

        db.crear_tabla_sedes()
        db.ensure_sedes_iniciales()

        self.render_cards()

    def render_cards(self):
        for w in self.cards_area.winfo_children():
            w.destroy()

        sedes = db.listar_sedes()
        col = 0
        row = 0
        max_cols = 2

        for (sid, nombre, ubicacion) in sedes:
            card = tk.Frame(self.cards_area, bg=COLOR_CARD, bd=0, highlightthickness=0)
            card.bind("<Button-1>", lambda e, i=sid: self.seleccionar_sede(i))
            card.grid(row=row, column=col, padx=60, pady=20, ipadx=80, ipady=80)

            lbl_nombre = tk.Label(card, text=nombre, bg=COLOR_CARD, fg=COLOR_TXT,
                                  font=("Segoe UI", 18, "bold"))
            lbl_nombre.pack()
            lbl_ubi = tk.Label(card, text=ubicacion, bg=COLOR_CARD, fg=COLOR_TXT,
                               font=("Segoe UI", 12, "bold"))
            lbl_ubi.pack()

            if self.sede_seleccionada_id == sid:
                card.config(highlightbackground="#000000", highlightcolor="#000000", highlightthickness=3)
            else:
                card.config(highlightthickness=0)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def seleccionar_sede(self, sede_id):
        self.sede_seleccionada_id = sede_id
        self.render_cards()
        # Placeholder (aquí luego abrimos el menú propio de la sede)
        info = db.obtener_sede(sede_id)
        if info:
            _, nombre, ubicacion = info
            messagebox.showinfo("Sede seleccionada",
                                f"Abriremos el menú de:\n\n{nombre}\n{ubicacion}\n\n(Pronto: más pantallas)")

            if self.on_open_sede:
                self.on_open_sede(sede_id)

    def nueva_sede(self):
        nombre = simpledialog.askstring("Nueva sede", "Nombre de la sede:", parent=self)
        if not nombre:
            return
        ubicacion = simpledialog.askstring("Nueva sede", "Ubicación:", parent=self)
        if not ubicacion:
            ubicacion = "Ubicación"

        db.insertar_sede(nombre.strip(), ubicacion.strip())
        self.render_cards()

    def eliminar_sede(self):
        if not self.sede_seleccionada_id:
            messagebox.showwarning("Eliminar sede", "Primero selecciona una sede haciendo clic en una tarjeta.")
            return
        if messagebox.askyesno("Eliminar sede", "¿Seguro que quieres eliminar la sede seleccionada?"):
            db.eliminar_sede(self.sede_seleccionada_id)
            self.sede_seleccionada_id = None
            self.render_cards()