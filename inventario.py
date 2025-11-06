import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import db
from side_bar import SideBar
from citas import CitasWindow
from reportes import ReportesWindow
from ventas import VentasWindow

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

class InventarioWindow(tk.Toplevel):
    def __init__(self, master, sede_id):
        super().__init__(master)
        self.sede_id = int(sede_id)
        self.title("Inventario")
        self.geometry("1366x768")
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)

        db.crear_tabla_inventario()
        db.asegurar_columna_precio()
        db.crear_tabla_ventas()
        db.crear_tabla_citas()

        self.sidebar = SideBar(
            self,
            on_exit=self.destroy,
            on_open_ventas=lambda: VentasWindow(self, self.sede_id),
            on_open_reportes=lambda: ReportesWindow(self),
            on_open_calendario=lambda: CitasWindow(self, self.sede_id)
        )
        self.sidebar.pack(side="left", fill="y")

        panel = tk.Frame(self, bg=BG_CARDS)
        panel.pack(side="left", expand=True, fill="both", padx=20, pady=20)

        sede = db.obtener_sede(self.sede_id)
        titulo = f"Inventario — {sede[1]}" if sede else "Inventario"
        tk.Label(panel, text=titulo, bg=BG_CARDS, fg=TEXT,
                 font=("Segoe UI", 20, "bold")).pack(pady=(6, 16))

        self.tree = ttk.Treeview(
            panel,
            columns=("Producto", "Existencias", "Precio (Q)"),
            show="headings",
            height=16
        )
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Existencias", text="Existencias")
        self.tree.heading("Precio (Q)", text="Precio (Q)")
        self.tree.column("Producto", width=380, anchor="center")
        self.tree.column("Existencias", width=120, anchor="center")
        self.tree.column("Precio (Q)", width=120, anchor="center")
        self.tree.pack(fill="x", pady=6)

        barra = tk.Frame(panel, bg=BG_CARDS)
        barra.pack(pady=12)

        tk.Button(
            barra, text="AGREGAR PRODUCTO", bg=BUTTONS, fg="white", bd=0,
            cursor="hand2", command=self._agregar
        ).pack(side="left", padx=6)

        tk.Button(
            barra, text="MODIFICAR PRODUCTO", bg=BUTTONS, fg="white", bd=0,
            cursor="hand2", command=self._modificar
        ).pack(side="left", padx=6)

        tk.Button(
            barra, text="ELIMINAR PRODUCTO", bg=BUTTONS, fg="white", bd=0,
            cursor="hand2", command=self._eliminar
        ).pack(side="left", padx=6)

        self._cargar()

    def _cerrar(self):
        try:
            self.destroy()
        except Exception:
            pass

    def _cargar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            productos = db.listar_inventario(self.sede_id)
        except Exception as e:
            messagebox.showerror("Inventario", f"Error cargando inventario:\n{e}")
            return
        for (pid, nombre, stock, precio) in productos:
            self.tree.insert("", "end", iid=str(pid), values=(nombre, int(stock), f"{float(precio):.2f}"))

    def _agregar(self):
        nombre = simpledialog.askstring("Nuevo producto", "Nombre:", parent=self)
        if not nombre:
            return
        try:
            stock = simpledialog.askinteger("Nuevo producto", "Existencias:", parent=self, minvalue=0)
            if stock is None:
                return
            precio = simpledialog.askfloat("Nuevo producto", "Precio (Q):", parent=self, minvalue=0.0)
            if precio is None:
                return
            db.insertar_producto(self.sede_id, nombre.strip(), int(stock), float(precio))
        except Exception as e:
            messagebox.showerror("Inventario", f"No se pudo agregar el producto:\n{e}")
            return
        self._cargar()

    def _modificar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Editar", "Selecciona un producto primero.")
            return
        pid = int(sel[0])
        nombre_act, stock_act, precio_act = self.tree.item(sel[0], "values")

        nuevo_nombre = simpledialog.askstring("Modificar", "Nuevo nombre:", initialvalue=nombre_act, parent=self)
        if nuevo_nombre is None:
            return
        try:
            nuevo_stock = simpledialog.askinteger(
                "Modificar", "Nueva cantidad:", initialvalue=int(stock_act), parent=self, minvalue=0
            )
            if nuevo_stock is None:
                return
            nuevo_precio = simpledialog.askfloat(
                "Modificar", "Nuevo precio (Q):", initialvalue=float(precio_act), parent=self, minvalue=0.0
            )
            if nuevo_precio is None:
                return
            db.actualizar_producto(pid, nuevo_nombre.strip(), int(nuevo_stock), float(nuevo_precio))
        except Exception as e:
            messagebox.showerror("Inventario", f"No se pudo modificar el producto:\n{e}")
            return
        self._cargar()

    def _eliminar(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Eliminar", "Selecciona un producto primero.")
            return
        pid = int(sel[0])
        if not messagebox.askyesno("Eliminar", "¿Eliminar este producto?"):
            return
        try:
            db.eliminar_producto(pid)
        except Exception as e:
            messagebox.showerror("Inventario", f"No se pudo eliminar el producto:\n{e}")
            return
        self._cargar()