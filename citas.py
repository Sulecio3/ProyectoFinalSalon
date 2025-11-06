import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from datetime import date, datetime

try:
    from tkcalendar import Calendar
except Exception as e:
    Calendar = None
    _TKCAL_ERROR = e
else:
    _TKCAL_ERROR = None

import db

BG_PRIMARY = '#fccfd4'
BG_SECONDARY = '#fccfd4'
BG_CARDS = '#fccfd4'
ACCENT = '#da5d86'
TEXT = '#0b1011'
BUTTONS = "#1d7c83"
BUTTONS_SECONDARY = "#1b9199"
SUCCESS = "#7CB2E5"
WARNING = "#FFA5DC"
ERROR = "#FFB7CF"

OPEN_TIME_MIN = 9 * 60
FIRST_START_MIN = 9 * 60 + 15
CLOSE_TIME_MIN = 19 * 60
LAST_END_MIN = 18 * 60 + 45

EMP_UNIAS = ["Angelica", "Yoli"]


class CitasWindow(tk.Toplevel):
    def __init__(self, master, sede_id: int):
        super().__init__(master)
        self.title("Calendario y Citas")
        self.geometry("1366x768")
        self.configure(bg=BG_PRIMARY)
        self.resizable(False, False)

        if _TKCAL_ERROR is not None:
            tk.Label(self, text="Falta instalar tkcalendar (pip install tkcalendar)",
                     bg=BG_PRIMARY, fg="red", font=("Segoe UI", 12, "bold")).pack(pady=20)
            return

        self.sede_id = int(sede_id)
        self.es_unias = db.sede_es_unas(self.sede_id)

        db.crear_tabla_citas()
        db.crear_tabla_servicios()
        db.seed_servicios()
        db.asegurar_columnas_citas()

        self._stack_acciones = []

        cont = tk.Frame(self, bg=BG_CARDS)
        cont.pack(expand=True, fill="both", padx=16, pady=16)

        sede = db.obtener_sede(self.sede_id)
        titulo = f"Calendario — {sede[1]}" if sede else "Calendario"
        tk.Label(cont, text=titulo, bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(pady=(0, 8))

        cuerpo = tk.Frame(cont, bg=BG_CARDS)
        cuerpo.pack(expand=True, fill="both")

        izq = tk.Frame(cuerpo, bg=BG_CARDS)
        izq.pack(side="left", fill="y", padx=(0, 12))

        hoy = date.today()
        self.cal = Calendar(izq, selectmode="day", date_pattern="yyyy-mm-dd", showweeknumbers=False)
        self.cal.selection_set(datetime(hoy.year, hoy.month, hoy.day))
        self.cal.pack(padx=4, pady=4)
        self.cal.bind("<<CalendarSelected>>", lambda e: self._cargar())

        der = tk.Frame(cuerpo, bg=BG_CARDS)
        der.pack(side="left", expand=True, fill="both")

        self.badge = tk.Label(der, text=self.cal.get_date(), bg=BG_CARDS, fg=TEXT, font=("Segoe UI", 11, "bold"))
        self.badge.pack(anchor="w", pady=(0, 6))

        self.tree = ttk.Treeview(
            der,
            columns=("Cliente", "Servicio", "Precio (Q)", "Hora", "Empleada"),
            show="headings",
            height=16
        )
        self.tree.heading("Cliente", text="Cliente")
        self.tree.heading("Servicio", text="Servicio")
        self.tree.heading("Precio (Q)", text="Precio (Q)")
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Empleada", text="Empleada")
        self.tree.column("Cliente", width=220, anchor="center")
        self.tree.column("Servicio", width=320, anchor="center")
        self.tree.column("Precio (Q)", width=100, anchor="center")
        self.tree.column("Hora", width=120, anchor="center")
        self.tree.column("Empleada", width=120, anchor="center")
        self.tree.pack(fill="x", pady=4)

        barra = tk.Frame(der, bg=BG_CARDS)
        barra.pack(pady=8)
        tk.Button(barra, text="+ NUEVA", bg=BUTTONS, bd=0, command=self._nueva).pack(side="left", padx=4)
        tk.Button(barra, text="MODIFICAR", bg=BUTTONS, bd=0, command=self._modificar).pack(side="left", padx=4)
        tk.Button(barra, text="ELIMINAR", bg=BUTTONS, bd=0, command=self._eliminar).pack(side="left", padx=4)
        tk.Button(barra, text="DESHACER", bg=ERROR, bd=0, command=self._deshacer).pack(side="left", padx=12)
        tk.Button(barra, text="CERRAR", bg=WARNING, bd=0, command=self.destroy).pack(side="left", padx=12)

        self._cargar()

    def _cargar(self):
        fecha = self.cal.get_date()
        self.badge.config(text=f"Fecha: {fecha}")
        for i in self.tree.get_children():
            self.tree.delete(i)
        for (cid, cliente, servicio, inicio, fin, precio, empleada) in db.listar_citas(self.sede_id, fecha):
            self.tree.insert(
                "", "end", iid=str(cid),
                values=(cliente, servicio, f"{float(precio):.2f}", f"{inicio} - {fin}",
                        empleada or ("Única" if not self.es_unias else "—"))
            )

    def _to_min(self, hhmm: str) -> int:
        return int(hhmm[:2]) * 60 + int(hhmm[3:])

    def _hora_valida(self, inicio: str, fin: str) -> tuple[bool, str]:
        for t in (inicio, fin):
            if len(t) != 5 or t[2] != ":":
                return False, "Formato de hora inválido. Usa HH:MM (ej. 09:30)."
            try:
                h = int(t[:2]);
                m = int(t[3:])
                if not (0 <= h <= 23 and 0 <= m <= 59):
                    return False, "Hora fuera de rango."
            except Exception:
                return False, "Hora inválida."

        ini = self._to_min(inicio)
        finm = self._to_min(fin)
        if ini >= finm:
            return False, "La hora de inicio debe ser menor que la de finalización."
        if ini < FIRST_START_MIN:
            return False, "La primera cita debe iniciar a las 09:15 o después."
        if finm > LAST_END_MIN:
            return False, "La última cita debe finalizar a las 18:45 o antes."
        if ini < OPEN_TIME_MIN or finm > CLOSE_TIME_MIN:
            return False, "Fuera del horario (09:00 a 19:00)."
        return True, ""

    def _traslapa(self, i1: str, f1: str, i2: str, f2: str) -> bool:
        a, b = self._to_min(i1), self._to_min(f1)
        c, d = self._to_min(i2), self._to_min(f2)
        return a < d and c < b

    def _hay_conflicto(self, fecha: str, inicio: str, fin: str, empleada: str | None) -> bool:
        rows = db.listar_citas(self.sede_id, fecha)
        if self.es_unias:
            for (_cid, _cli, _srv, _ini, _fin, _precio, _emp) in rows:
                if (empleada or "").strip().lower() == ((_emp or "").strip().lower()):
                    if self._traslapa(inicio, fin, _ini, _fin):
                        return True
            return False
        else:
            for (_cid, _cli, _srv, _ini, _fin, _precio, _emp) in rows:
                if self._traslapa(inicio, fin, _ini, _fin):
                    return True
            return False

    def _sel_id(self):
        sel = self.tree.selection()
        return int(sel[0]) if sel else None

    def _nueva(self):
        self._form_guardar()

    def _modificar(self):
        cid = self._sel_id()
        if not cid:
            messagebox.showwarning("Modificar", "Selecciona una cita.")
            return
        actual = db.obtener_cita(cid)
        if not actual:
            messagebox.showerror("Modificar", "No se encontró la cita.")
            return
        self._form_guardar(cid, actual)

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
        self._stack_acciones.append(("del", {
            "id": row[0], "sede_id": row[1], "fecha": row[2],
            "cliente": row[3], "servicio": row[4],
            "inicio": row[5], "fin": row[6],
            "servicio_id": row[7], "servicio_nombre": row[8], "precio": row[9] or 0.0,
            "empleada": row[10]
        }))
        self._cargar()
        messagebox.showinfo("Citas", "Cita eliminada.")

    def _deshacer(self):
        if not self._stack_acciones:
            messagebox.showinfo("Deshacer", "Nada para deshacer.")
            return
        accion, datos = self._stack_acciones.pop()
        try:
            if accion == "add":
                db.eliminar_cita(int(datos["id"]))
            elif accion == "edit":
                prev = datos["prev"]
                db.actualizar_cita(
                    int(datos["id"]),
                    prev["cliente"], prev["servicio"], prev["inicio"], prev["fin"],
                    prev.get("servicio_id"), prev.get("servicio_nombre"), prev.get("precio"), prev.get("empleada")
                )
            elif accion == "del":
                db.insertar_cita(
                    datos["sede_id"], datos["fecha"], datos["cliente"], datos["servicio"],
                    datos["inicio"], datos["fin"], datos.get("servicio_id"),
                    datos.get("servicio_nombre"), datos.get("precio") or 0.0, datos.get("empleada")
                )
            self._cargar()
            messagebox.showinfo("Deshacer", "Acción deshecha.")
        except Exception as e:
            messagebox.showerror("Deshacer", f"No se pudo deshacer: {e}")

    def _time_choices(self):
        mins = []
        t = FIRST_START_MIN
        while t <= LAST_END_MIN:
            h = t // 60
            m = t % 60
            mins.append(f"{h:02d}:{m:02d}")
            t += 30
        return mins

    def _form_guardar(self, cid: int = None, actual=None):
        fecha = self.cal.get_date()
        form = tk.Toplevel(self)
        form.title("Cita")
        form.geometry("1366x768")
        form.resizable(False, False)
        form.grab_set()
        form.transient(self)

        panel = tk.Frame(form, padx=12, pady=12)
        panel.pack(fill="both", expand=True)

        tk.Label(panel, text=f"Fecha: {fecha}", font=("Segoe UI", 10, "bold")).grid(row=0, column=0, columnspan=2,
                                                                                    sticky="w", pady=(0, 10))

        prev = {"cliente": "", "servicio": "", "inicio": "", "fin": "", "servicio_id": None, "servicio_nombre": "",
                "precio": 0.0, "empleada": None}
        if actual:
            prev["cliente"] = actual[3] or ""
            prev["servicio"] = actual[4] or ""
            prev["inicio"] = actual[5] or ""
            prev["fin"] = actual[6] or ""
            prev["servicio_id"] = actual[7]
            prev["servicio_nombre"] = actual[8] or actual[4] or ""
            prev["precio"] = float(actual[9] or 0.0)
            prev["empleada"] = actual[10]

        tk.Label(panel, text="Cliente:").grid(row=1, column=0, sticky="e", padx=6, pady=6)
        var_cliente = tk.StringVar(value=prev["cliente"])
        tk.Entry(panel, textvariable=var_cliente, width=34).grid(row=1, column=1, sticky="w")

        tk.Label(panel, text="Servicio:").grid(row=2, column=0, sticky="e", padx=6, pady=6)
        servicios = db.listar_servicios(self.sede_id)
        opciones = [f"{nom} (Q {float(pre):.2f})" for (_id, nom, pre) in servicios]
        combo = ttk.Combobox(panel, values=opciones, state="readonly", width=44)
        combo.grid(row=2, column=1, sticky="w")

        if prev["servicio_nombre"]:
            texto_buscar = f"{prev['servicio_nombre']} (Q {prev['precio']:.2f})"
            try:
                combo.current(opciones.index(texto_buscar))
            except Exception:
                for i, (_id, nom, pre) in enumerate(servicios):
                    if nom.strip().lower() == prev["servicio"].strip().lower():
                        combo.current(i)
                        break

        var_emp = tk.StringVar()
        emp_combo = None
        base_row = 4
        if self.es_unias:
            tk.Label(panel, text="Empleada:").grid(row=3, column=0, sticky="e", padx=6, pady=6)
            emp_combo = ttk.Combobox(panel, values=EMP_UNIAS, state="readonly", width=20)
            emp_combo.grid(row=3, column=1, sticky="w")
            if prev["empleada"] in EMP_UNIAS:
                emp_combo.set(prev["empleada"])
        else:
            base_row = 3

        tk.Label(panel, text="Inicio:").grid(row=base_row, column=0, sticky="e", padx=6, pady=6)
        tk.Label(panel, text="Fin:").grid(row=base_row + 1, column=0, sticky="e", padx=6, pady=6)

        horas = self._time_choices()
        var_inicio = tk.StringVar(value=prev["inicio"] if prev["inicio"] in horas else "")
        var_fin = tk.StringVar(value=prev["fin"] if prev["fin"] in horas else "")

        cb_inicio = ttk.Combobox(panel, values=horas, state="readonly", width=10, textvariable=var_inicio)
        cb_fin = ttk.Combobox(panel, values=horas, state="readonly", width=10, textvariable=var_fin)
        cb_inicio.grid(row=base_row, column=1, sticky="w")
        cb_fin.grid(row=base_row + 1, column=1, sticky="w")

        barra = tk.Frame(panel)
        barra.grid(row=base_row + 2, column=0, columnspan=2, pady=(12, 0))

        def _guardar():
            cliente = (var_cliente.get() or "").strip()
            if not cliente:
                messagebox.showwarning("Validación", "Escribe el nombre del cliente.")
                return
            if not combo.get():
                messagebox.showwarning("Validación", "Selecciona un servicio.")
                return

            idx = opciones.index(combo.get())
            servicio_id, servicio_nombre, precio = servicios[idx][0], servicios[idx][1], float(servicios[idx][2])

            empleada = None
            if self.es_unias:
                if not emp_combo or not emp_combo.get():
                    messagebox.showwarning("Validación", "Selecciona la empleada (Angelica o Yoli).")
                    return
                empleada = emp_combo.get().strip()
            else:
                empleada = "Única"

            inicio = (var_inicio.get() or "").strip()
            fin = (var_fin.get() or "").strip()

            if not inicio or not fin:
                messagebox.showwarning("Horario", "Selecciona inicio y fin.")
                return

            ok, msg = self._hora_valida(inicio, fin)
            if not ok:
                messagebox.showwarning("Horario", msg)
                return

            if self._hay_conflicto(fecha, inicio, fin, empleada if self.es_unias else None):
                if self.es_unias:
                    messagebox.showerror("Conflicto", f"Ya hay cita para {empleada} en ese horario.")
                else:
                    messagebox.showerror("Conflicto", "Ya hay una cita en ese horario.")
                return

            if cid is None:
                nuevo_id = db.insertar_cita(
                    self.sede_id, fecha, cliente, servicio_nombre, inicio, fin,
                    servicio_id=servicio_id, servicio_nombre=servicio_nombre, precio=precio, empleada=empleada
                )
                self._stack_acciones.append(("add", {"id": nuevo_id}))
                messagebox.showinfo("Citas", "Cita creada.")
            else:
                self._stack_acciones.append(("edit", {
                    "id": cid,
                    "prev": {
                        "cliente": prev["cliente"], "servicio": prev["servicio"],
                        "inicio": prev["inicio"], "fin": prev["fin"],
                        "servicio_id": prev["servicio_id"], "servicio_nombre": prev["servicio_nombre"],
                        "precio": prev["precio"], "empleada": prev["empleada"]
                    }
                }))
                db.actualizar_cita(
                    cid, cliente, servicio_nombre, inicio, fin,
                    servicio_id=servicio_id, servicio_nombre=servicio_nombre, precio=precio, empleada=empleada
                )
                messagebox.showinfo("Citas", "Cita modificada.")

            form.destroy()
            self._cargar()

        tk.Button(barra, text="GUARDAR", bg=BUTTONS, bd=0, command=_guardar).pack(side="left", padx=6)
        tk.Button(barra, text="CANCELAR", bg="#E4E4E4", bd=0, command=form.destroy).pack(side="left", padx=6)