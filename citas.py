import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox, simpledialog
from datetime import date, datetime

try:
    from tkcalendar import Calendar
except Exception as e:
    Calendar = None
    _TKCAL_ERROR = e
else:
    _TKCAL_ERROR = None

import db

BG      = "#F7F2FF"
PANEL   = "#E6DAFF"
TXT     = "#000000"
BTN     = "#CDB7FF"

class CitasWindow(tk.Toplevel):
    """
    Agenda sencilla por sede:
    - Calendario a la izquierda
    - Citas del día a la derecha (Cliente, Servicio, Hora)
    - CRUD de citas con validación simple
    - LIFO: pila de acciones recientes (agregar/modificar/eliminar) para posible 'deshacer' simple (1 paso)
      (Aquí solo guardamos el último registro afectado y su estado para mantener LIFO).
    - Recursividad mínima: validación de hora intenta revalidar limpiando espacios una vez.
    """
    def __init__(self, master, sede_id: int):
        super().__init__(master)
        self.title("Calendario y Citas")
        self.geometry("980x620")
        self.configure(bg=BG)
        self.resizable(False, False)

        if _TKCAL_ERROR is not None:
            tk.Label(self, text="Falta instalar tkcalendar (pip install tkcalendar)",
                     bg=BG, fg="red", font=("Segoe UI", 12, "bold")).pack(pady=20)
            return

        self.sede_id = sede_id

        db.crear_tabla_citas()

        self._stack_acciones = []  # LIFO

        cont = tk.Frame(self, bg=PANEL)
        cont.pack(expand=True, fill="both", padx=16, pady=16)

        # Título
        sede = db.obtener_sede(self.sede_id)
        titulo = f"Calendario — {sede[1]}" if sede else "Calendario"
        tk.Label(cont, text=titulo, bg=PANEL, fg=TXT, font=("Segoe UI", 18, "bold")).pack(pady=(0, 8))

        cuerpo = tk.Frame(cont, bg=PANEL)
        cuerpo.pack(expand=True, fill="both")

        izq = tk.Frame(cuerpo, bg=PANEL)
        izq.pack(side="left", fill="y", padx=(0, 12))

        hoy = date.today()
        self.cal = Calendar(
            izq,
            selectmode="day",
            date_pattern="yyyy-mm-dd",
            showweeknumbers=False
        )
        self.cal.selection_set(datetime(hoy.year, hoy.month, hoy.day))
        self.cal.pack(padx=4, pady=4)
        self.cal.bind("<<CalendarSelected>>", lambda e: self._cargar())

        der = tk.Frame(cuerpo, bg=PANEL)
        der.pack(side="left", expand=True, fill="both")

        self.badge = tk.Label(der, text=self.cal.get_date(), bg=PANEL, fg=TXT, font=("Segoe UI", 11, "bold"))
        self.badge.pack(anchor="w", pady=(0, 6))

        self.tree = ttk.Treeview(der, columns=("Cliente", "Servicio", "Hora"), show="headings", height=16)
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Servicio", text="Servicio")
        self.tree.heading("Hora", text="Hora")
        self.tree.column("Cliente", width=260, anchor="center")
        self.tree.column("Servicio", width=220, anchor="center")
        self.tree.column("Hora", width=120, anchor="center")
        self.tree.pack(fill="x", pady=4)

        barra = tk.Frame(der, bg=PANEL)
        barra.pack(pady=8)
        tk.Button(barra, text="+ NUEVA", bg=BTN, bd=0, command=self._nueva).pack(side="left", padx=4)
        tk.Button(barra, text="MODIFICAR", bg=BTN, bd=0, command=self._modificar).pack(side="left", padx=4)
        tk.Button(barra, text="ELIMINAR", bg=BTN, bd=0, command=self._eliminar).pack(side="left", padx=4)
        tk.Button(barra, text="DESHACER (LIFO)", bg="#FFB7B7", bd=0, command=self._deshacer).pack(side="left", padx=12)
        tk.Button(barra, text="CERRAR", bg="#FFD6A5", bd=0, command=self.destroy).pack(side="left", padx=12)

        self._cargar()

    def _cargar(self):
        fecha = self.cal.get_date()
        self.badge.config(text=f"Fecha: {fecha}")
        for i in self.tree.get_children():
            self.tree.delete(i)
        for (cid, cliente, servicio, inicio, fin) in db.listar_citas(self.sede_id, fecha):
            self.tree.insert("", "end", iid=str(cid), values=(cliente, servicio, f"{inicio} - {fin}"))

    def _hora_valida(self, texto: str, intento: int = 0) -> bool:
        """
        Acepta "HH:MM". Si falla, en el primer intento recorta espacios y reintenta (recursividad 1 nivel).
        """
        try:
            if len(texto) != 5 or texto[2] != ":":
                raise ValueError()
            h = int(texto[:2])
            m = int(texto[3:])
            ok = (0 <= h <= 23 and 0 <= m <= 59)
            if not ok:
                raise ValueError()
            return True
        except Exception:
            if intento < 1:
                return self._hora_valida(texto.strip(), intento + 1)
            return False

    def _sel_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    # --- Acciones ---
    def _nueva(self):
        fecha = self.cal.get_date()
        cliente = simpledialog.askstring("Nueva cita", "Cliente:", parent=self)
        if not cliente:
            return
        servicio = simpledialog.askstring("Nueva cita", "Servicio:", parent=self) or ""
        inicio = simpledialog.askstring("Nueva cita", "Hora de inicio (HH:MM):", parent=self) or ""
        fin = simpledialog.askstring("Nueva cita", "Hora de fin (HH:MM):", parent=self) or ""

        if not all([cliente.strip(), servicio.strip(), inicio.strip(), fin.strip()]):
            messagebox.showwarning("Validación", "Completa todos los campos.")
            return
        if not self._hora_valida(inicio) or not self._hora_valida(fin):
            messagebox.showwarning("Hora", "Formato 24h (ej. 09:30).")
            return
        if inicio >= fin:
            messagebox.showwarning("Horario", "La hora de inicio debe ser menor que la de fin.")
            return

        cid = db.insertar_cita(self.sede_id, fecha, cliente.strip(), servicio.strip(), inicio.strip(), fin.strip())
        # LIFO push
        self._stack_acciones.append(("add", {"id": cid}))
        self._cargar()
        messagebox.showinfo("Citas", "Cita creada.")

    def _modificar(self):
        cid = self._sel_id()
        if not cid:
            messagebox.showwarning("Modificar", "Selecciona una cita.")
            return
        actual = db.obtener_cita(cid)  # (id, sede_id, fecha, cliente, servicio, inicio, fin)

        cliente = simpledialog.askstring("Modificar", "Cliente:", parent=self, initialvalue=actual[3]) or ""
        servicio = simpledialog.askstring("Modificar", "Servicio:", parent=self, initialvalue=actual[4]) or ""
        inicio = simpledialog.askstring("Modificar", "Hora inicio (HH:MM):", parent=self, initialvalue=actual[5]) or ""
        fin = simpledialog.askstring("Modificar", "Hora fin (HH:MM):", parent=self, initialvalue=actual[6]) or ""

        if not all([cliente.strip(), servicio.strip(), inicio.strip(), fin.strip()]):
            messagebox.showwarning("Validación", "Completa todos los campos.")
            return
        if not self._hora_valida(inicio) or not self._hora_valida(fin):
            messagebox.showwarning("Hora", "Formato 24h (ej. 09:30).")
            return
        if inicio >= fin:
            messagebox.showwarning("Horario", "La hora de inicio debe ser menor que la de fin.")
            return

        db.actualizar_cita(cid, cliente.strip(), servicio.strip(), inicio.strip(), fin.strip())
        self._stack_acciones.append(("edit", {
            "id": cid,
            "prev": {
                "cliente": actual[3], "servicio": actual[4],
                "inicio": actual[5], "fin": actual[6]
            }
        }))
        self._cargar()
        messagebox.showinfo("Citas", "Cita modificada.")

    def _eliminar(self):
        cid = self._sel_id()
        if not cid:
            messagebox.showwarning("Eliminar", "Selecciona una cita.")
            return
        row = db.obtener_cita(cid)
        if not row:
            messagebox.showerror("Eliminar", "No se encontró la cita.")
            return
        if not messagebox.askyesno("Eliminar", "¿Eliminar esta cita?"):
            return
        db.eliminar_cita(cid)
        # LIFO push con estado para poder restaurar
        self._stack_acciones.append(("del", {
            "id": row[0], "sede_id": row[1], "fecha": row[2],
            "cliente": row[3], "servicio": row[4],
            "inicio": row[5], "fin": row[6]
        }))
        self._cargar()
        messagebox.showinfo("Citas", "Cita eliminada.")

    def _deshacer(self):
        if not self._stack_acciones:
            messagebox.showinfo("Deshacer", "Nada para deshacer.")
            return
        accion, datos = self._stack_acciones.pop()  # LIFO
        try:
            if accion == "add":
                db.eliminar_cita(int(datos["id"]))
            elif accion == "edit":
                prev = datos["prev"]
                db.actualizar_cita(int(datos["id"]),
                                   prev["cliente"], prev["servicio"],
                                   prev["inicio"], prev["fin"])
            elif accion == "del":
                db.insertar_cita(datos["sede_id"], datos["fecha"],
                                 datos["cliente"], datos["servicio"],
                                 datos["inicio"], datos["fin"])
            else:
                pass
            self._cargar()
            messagebox.showinfo("Deshacer", "Acción deshecha.")
        except Exception as e:
            messagebox.showerror("Deshacer", f"No se pudo deshacer: {e}")
