import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import db
from sidebar import SideBar

COLOR_BG     = "#FFF8E6"
COLOR_PANEL  = "#FFE0A3"
COLOR_BTN    = "#FFB86B"
COLOR_TXT    = "#000000"

class InventarioWindow(tk.Toplevel):
    def __init__(self, master, sede_id):
        super().__init__(master)
        self.sede_id = sede_id
        self.title("Inventario")
        self.geometry("950x560")
        self.configure(bg=COLOR_BG)

        db.crear_tabla_inventario()

        self.sidebar = SideBar(self, on_exit=self.destroy)
        self.sidebar.pack(side="left", fill="y")

        panel = tk.Frame(self, bg=COLOR_PANEL)
        panel.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        tk.Label(panel, text="Inventario", bg=COLOR_PANEL, fg=COLOR_TXT,
                 font=("Segoe UI", 22, "bold")).pack(pady=(6, 16))

        self.tree = ttk.Treeview(panel, columns=("Producto", "Existencias"),
                                 show="headings", height=10)
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Existencias", text="Existencias")
        self.tree.column("Producto", width=300, anchor="center")
        self.tree.column("Existencias", width=120, anchor="center")
        self.tree.pack(pady=6)

        self._cargar()

        barra = tk.Frame(panel, bg=COLOR_PANEL)
        barra.pack(pady=12)
        tk.Button(barra, text="AGREGAR PRODUCTO", bg=COLOR_BTN, fg="black", bd=0,
                  cursor="hand2", command=self._agregar).pack(side="left", padx=6)
        tk.Button(barra, text="MODIFICAR PRODUCTO", bg=COLOR_BTN, fg="black", bd=0,
                  cursor="hand2", command=self._modificar).pack(side="left", padx=6)
        tk.Button(barra, text="ELIMINAR PRODUCTO", bg=COLOR_BTN, fg="black", bd=0,
                  cursor="hand2", command=self._eliminar).pack(side="left", padx=6)

    def _cargar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for (pid, nombre, stock) in db.listar_inventario(self.sede_id):
            self.tree.insert("", "end", iid=str(pid), values=(nombre, stock))

    def _agregar(self):
        nombre = simpledialog.askstring("Nuevo producto", "Nombre:", parent=self)
        if not nombre:
            return
        stock = simpledialog.askinteger("Nuevo producto", "Existencias:", parent=self, minvalue=0)
        db.insertar_producto(self.sede_id, nombre.strip(), int(stock or 0))
        self._cargar()

    def _modificar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Editar", "Selecciona un producto primero.")
            return
        pid = int(sel[0])
        nombre_act, stock_act = self.tree.item(sel[0], "values")
        nuevo_nombre = simpledialog.askstring("Modificar", "Nuevo nombre:",
                                              initialvalue=nombre_act, parent=self)
        if nuevo_nombre is None:
            return
        nuevo_stock = simpledialog.askinteger("Modificar", "Nueva cantidad:",
                                              initialvalue=int(stock_act), parent=self, minvalue=0)
        if nuevo_stock is None:
            return
        db.actualizar_producto(pid, nuevo_nombre.strip(), int(nuevo_stock))
        self._cargar()

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Eliminar", "Selecciona un producto primero.")
            return
        pid = int(sel[0])
        if messagebox.askyesno("Eliminar", "¿Eliminar este producto?"):
            db.eliminar_producto(pid)
            self._cargar()