import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import db

COLOR_BG     = "#F3FFF5"
COLOR_PANEL  = "#CFF5D2"
COLOR_TXT    = "#000000"
COLOR_BTN    = "#8BE28F"

class VentasWindow(tk.Toplevel):
    def __init__(self, master, sede_id):
        super().__init__(master)
        self.sede_id = sede_id
        self.title("Ventas")
        self.geometry("720x480")
        self.configure(bg=COLOR_BG)

        panel = tk.Frame(self, bg=COLOR_PANEL)
        panel.pack(expand=True, fill="both", padx=20, pady=20)

        sede = db.obtener_sede(self.sede_id)
        titulo = f"Ventas — {sede[1]}" if sede else "Ventas"
        tk.Label(panel, text=titulo, bg=COLOR_PANEL, fg=COLOR_TXT,
                 font=("Segoe UI", 18, "bold")).pack(pady=(6, 12))

        self.tree = ttk.Treeview(panel, columns=("Producto", "Stock", "Precio (Q)"),
                                 show="headings", height=10)
        self.tree.heading("Producto", text="Producto")
        self.tree.heading("Stock", text="Stock")
        self.tree.heading("Precio (Q)", text="Precio (Q)")
        self.tree.column("Producto", width=280, anchor="center")
        self.tree.column("Stock", width=80, anchor="center")
        self.tree.column("Precio (Q)", width=100, anchor="center")
        self.tree.pack(pady=6)

        self._cargar()

        tk.Button(panel, text="VENDER", bg=COLOR_BTN, fg="black", bd=0,
                  cursor="hand2", command=self._vender).pack(pady=8)

    def _cargar(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for (pid, nombre, stock, precio) in db.listar_inventario(self.sede_id):
            self.tree.insert("", "end", iid=str(pid), values=(nombre, stock, f"{precio:.2f}"))

    def _vender(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Vender", "Selecciona un producto primero.")
            return
        pid = int(sel[0])
        nombre, stock, precio_str = self.tree.item(sel[0], "values")
        stock = int(stock)
        precio = float(precio_str)

        cant = simpledialog.askinteger("Vender", f"¿Cuántas unidades de '{nombre}' deseas vender?",
                                       parent=self, minvalue=1, maxvalue=stock if stock > 0 else 1)
        if not cant:
            return
        if cant > stock:
            messagebox.showerror("Vender", "No hay suficientes existencias.")
            return

        db.registrar_venta(self.sede_id, pid, cant, precio)
        messagebox.showinfo("Venta", f"Venta registrada.\nTotal: Q {precio * cant:.2f}")
        self._cargar()