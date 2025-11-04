import sqlite3

DB_FILE = "salon.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

# -------------------------- LOGIN --------------------------

def crear_bd_y_tabla():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            failed_attempts INTEGER DEFAULT 0,
            locked INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

    crear_tabla_sedes()
    crear_tabla_inventario()
    asegurar_columna_precio()
    crear_tabla_ventas()
    crear_tabla_citas()
    ensure_sedes_iniciales()
    crear_tabla_servicios()
    seed_servicios()
    asegurar_columnas_citas()

def usuario_existe(username: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
    ok = cur.fetchone() is not None
    conn.close()
    return ok

def insertar_usuario(username, first_name, last_name, email, password_hash):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users(username, first_name, last_name, email, password_hash) VALUES (?,?,?,?,?)",
        (username, first_name, last_name, email, password_hash),
    )
    conn.commit()
    conn.close()

def obtener_usuario(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, username, password_hash, failed_attempts, locked FROM users WHERE username=?",
        (username,),
    )
    row = cur.fetchone()
    conn.close()
    return row

def registrar_fallo(username: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET failed_attempts = failed_attempts + 1 WHERE username=?", (username,))
    conn.commit()
    cur.execute("SELECT failed_attempts FROM users WHERE username=?", (username,))
    fa_row = cur.fetchone()
    if fa_row and fa_row[0] >= 3:
        cur.execute("UPDATE users SET locked=1 WHERE username=?", (username,))
        conn.commit()
    conn.close()
    return fa_row[0] if fa_row else 0

def reset_intentos(username: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET failed_attempts=0, locked=0 WHERE username=?", (username,))
    conn.commit()
    conn.close()

# -------------------------- SEDES --------------------------

def crear_tabla_sedes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sedes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            ubicacion TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def ensure_sedes_iniciales():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM sedes")
    n = cur.fetchone()[0]
    if n == 0:
        cur.execute("INSERT INTO sedes(nombre, ubicacion) VALUES (?, ?)",
                    ("Salon de uñas", "Ubicación"))
        cur.execute("INSERT INTO sedes(nombre, ubicacion) VALUES (?, ?)",
                    ("Salon de cabello", "Ubicación"))
    conn.commit()
    conn.close()

def listar_sedes():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, ubicacion FROM sedes ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    return rows

def obtener_sede(sede_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, ubicacion FROM sedes WHERE id=?", (sede_id,))
    row = cur.fetchone()
    conn.close()
    return row

def insertar_sede(nombre: str, ubicacion: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO sedes(nombre, ubicacion) VALUES (?, ?)", (nombre, ubicacion))
    conn.commit()
    conn.close()

def eliminar_sede(sede_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM sedes WHERE id=?", (sede_id,))
    conn.commit()
    conn.close()

# -------------------------- INVENTARIO --------------------------

def crear_tabla_inventario():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            precio REAL NOT NULL DEFAULT 0.0,
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def asegurar_columna_precio():
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("ALTER TABLE inventario ADD COLUMN precio REAL NOT NULL DEFAULT 0.0")
        conn.commit()
    except Exception:
        pass
    conn.close()

def listar_inventario(sede_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, stock, precio FROM inventario WHERE sede_id=?", (sede_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def insertar_producto(sede_id, nombre, stock, precio):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO inventario(sede_id, nombre, stock, precio) VALUES (?,?,?,?)",
        (sede_id, nombre, int(stock), float(precio)),
    )
    conn.commit()
    conn.close()

def actualizar_producto(pid, nombre, stock, precio):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE inventario SET nombre=?, stock=?, precio=? WHERE id=?",
        (nombre, int(stock), float(precio), int(pid)),
    )
    conn.commit()
    conn.close()

def eliminar_producto(pid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventario WHERE id=?", (int(pid),))
    conn.commit()
    conn.close()

# -------------------------- VENTAS --------------------------

def crear_tabla_ventas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            precio_unitario REAL NOT NULL,
            total REAL NOT NULL,
            fecha TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE,
            FOREIGN KEY(producto_id) REFERENCES inventario(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def registrar_venta(sede_id, producto_id, cantidad, precio_unitario):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT stock FROM inventario WHERE id=? AND sede_id=?", (producto_id, sede_id))
    row = cur.fetchone()
    if not row:
        conn.close()
        raise ValueError("Producto no encontrado para esta sede.")
    stock_actual = int(row[0])
    cantidad = int(cantidad)
    if cantidad <= 0 or cantidad > stock_actual:
        conn.close()
        raise ValueError("Cantidad inválida o stock insuficiente.")

    nuevo_stock = stock_actual - cantidad
    cur.execute("UPDATE inventario SET stock=? WHERE id=?", (nuevo_stock, producto_id))

    total = float(precio_unitario) * cantidad
    cur.execute("""
        INSERT INTO ventas(sede_id, producto_id, cantidad, precio_unitario, total)
        VALUES (?,?,?,?,?)
    """, (sede_id, producto_id, cantidad, float(precio_unitario), total))

    conn.commit()
    conn.close()

# -------------------------- CITAS --------------------------

def crear_tabla_citas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,          -- 'yyyy-mm-dd'
            cliente TEXT NOT NULL,
            servicio TEXT NOT NULL,       -- legacy
            inicio TEXT NOT NULL,         -- 'HH:MM'
            fin TEXT NOT NULL,            -- 'HH:MM'
            servicio_id INTEGER,
            servicio_nombre TEXT,
            precio REAL DEFAULT 0.0,
            empleada TEXT,                -- NUEVO
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE,
            FOREIGN KEY(servicio_id) REFERENCES servicios(id) ON DELETE SET NULL
        )
    """)
    conn.commit()
    conn.close()

def listar_citas(sede_id: int, fecha: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, cliente, 
               COALESCE(servicio_nombre, servicio) as servicio_mostrar,
               inicio, fin, COALESCE(precio, 0.0) as precio_mostrar,
               empleada
        FROM citas
        WHERE sede_id=? AND fecha=?
        ORDER BY inicio ASC
    """, (sede_id, fecha))
    rows = cur.fetchall()
    conn.close()
    return rows

def insertar_cita(sede_id: int, fecha: str, cliente: str, servicio: str, inicio: str, fin: str,
                  servicio_id: int = None, servicio_nombre: str = None, precio: float = 0.0,
                  empleada: str = None) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO citas(sede_id, fecha, cliente, servicio, inicio, fin, servicio_id, servicio_nombre, precio, empleada)
        VALUES (?,?,?,?,?,?,?,?,?,?)
    """, (sede_id, fecha, cliente, servicio, inicio, fin, servicio_id, servicio_nombre, float(precio), empleada))
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid

def actualizar_cita(cid: int, cliente: str, servicio: str, inicio: str, fin: str,
                    servicio_id: int = None, servicio_nombre: str = None, precio: float = None,
                    empleada: str = None):
    conn = get_connection()
    cur = conn.cursor()
    if precio is None:
        cur.execute("""
            UPDATE citas SET cliente=?, servicio=?, inicio=?, fin=?, servicio_id=?, servicio_nombre=?, empleada=?
            WHERE id=?
        """, (cliente, servicio, inicio, fin, servicio_id, servicio_nombre, empleada, cid))
    else:
        cur.execute("""
            UPDATE citas SET cliente=?, servicio=?, inicio=?, fin=?, servicio_id=?, servicio_nombre=?, precio=?, empleada=?
            WHERE id=?
        """, (cliente, servicio, inicio, fin, servicio_id, servicio_nombre, float(precio), empleada, cid))
    conn.commit()
    conn.close()

def eliminar_cita(cid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM citas WHERE id=?", (cid,))
    conn.commit()
    conn.close()

def obtener_cita(cid: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, sede_id, fecha, cliente, servicio, inicio, fin, servicio_id, servicio_nombre, precio, empleada
        FROM citas
        WHERE id=?
    """, (cid,))
    row = cur.fetchone()
    conn.close()
    return row

def sede_es_unas(sede_id: int) -> bool:
    row = obtener_sede(sede_id)
    if not row:
        return False
    nombre = (row[1] or "").lower()
    return "uña" in nombre



# -------------------------- SERVICIOS --------------------------
def crear_tabla_servicios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS servicios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def listar_servicios(sede_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, precio FROM servicios WHERE sede_id=? ORDER BY nombre ASC", (sede_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def _servicios_cabello():
    return [
        ("Ampolla Hidratante", 60),
        ("Ampolla Miracle", 80),
        ("Ampolla para Caspa", 50),
        ("Alisado Permanente cabello corto", 500),
        ("Alisado Permanente cabello mediano", 700),
        ("Alisado Permanente cabello largo", 950),
        ("Alisado Permanente cabello extra largo", 1500),
        ("Balayage cabello corto", 650),
        ("Balayage cabello mediano", 850),
        ("Balayage cabello largo", 1050),
        ("Balayage cabello Extra largo", 1600),
        ("Base colochos cabello corto", 400),
        ("Base colochos cabello mediano", 500),
        ("Base colochos cabello largo", 600),
        ("Base colochos cabello Extra largo", 800),
        ("Combo de lavado/Corte/Planchado", 100),
        ("Corte de cabello dama", 50),
        ("corte de caballero", 40),
        ("Facial con Exfoliación y masaje", 150),
        ("Lavado de Cabello", 50),
        ("Maquillaje", 250),
        ("mechas cabello corto", 550),
        ("mechas cabello mediano", 750),
        ("mechas cabello largo", 950),
        ("mechas cabello extra largo", 1500),
        ("Nanoplatia cabello corto", 550),
        ("Nanoplatia cabello mediano", 750),
        ("Nanoplatia cabello largo", 1000),
        ("Nanoplatia cabello extra largo", 1700),
        ("Ondas Y cepillo cabello corto", 50),
        ("Ondas Y cepillo cabello mediano", 70),
        ("Ondas Y cepillo cabello Largo", 90),
        ("Ondas Y cepillo cabello Extra Largo", 120),
        ("Plan Capilar", 250),
        ("Plancho en cabello corto", 50),
        ("Plancho en cabello mediano", 60),
        ("Plancho en cabello largo", 70),
        ("Plancho en cabello extra largo", 100),
        ("rayitos cabello corto", 550),
        ("rayitos cabello mediano", 750),
        ("rayitos cabello largo", 950),
        ("rayitos cabello extra largo", 1500),
        ("Tratamientos", 220),
        ("tintes para cabello corto", 350),
        ("tintes para cabello mediano", 450),
        ("tintes para cabello largo", 650),
        ("tintes para cabello extra largo", 750),
        ("combo de 5 planchados Express", 225),
        ("combo de 5 planchados con Ampolla", 500),
        ("combo de 5 plachados + lavado + ampolla", 675),
        ("combo de 5 plachados + lavado", 400),
    ]

def _servicios_unias():
    return [
        ("Baño de acrilico uñas cortas", 160),
        ("Baño de acrilico uñas medianas", 180),
        ("Baño de acrilico uñas largas", 200),
        ("coloración de tip en pies", 155),
        ("Depilación", 180),
        ("Depilación area de bikini", 150),
        ("Depilación brazo completo", 160),
        ("Depilación de axila", 60),
        ("Depilación de bigote", 35),
        ("Depilación de ceja", 40),
        ("depilación  medio brazo", 130),
        ("depilación de barbilla", 45),
        ("depilación de patillas", 50),
        ("depilación de pierna completa", 300),
        ("depilación de media pierna", 150),
        ("depilación bikini completo", 160),
        ("diseño encapsulado, 3D, efecto sueter", 15),
        ("diseños con piedras, azúcar, espejo, marmoleado, polas y mano alzada", 10),
        ("manicure express de niñas", 45),
        ("manicure express esmalte normal", 65),
        ("manicure gelish", 80),
        ("manicure gelish con calcio", 100),
        ("manicure gelish con spa", 155),
        ("manicure spa con esmalte normal", 120),
        ("manicure spa con retoque", 205),
        ("Pedicure express esmalte normal", 80),
        ("pedicure con gelish", 120),
        ("pedicure gelish con spa", 175),
        ("pedicure gelish spa con retiro gelish", 200),
        ("pedicure spa sin nada para dama", 125),
        ("pedicure spa y baño de acrilico", 325),
        ("Pedicure spa con esmalte normal", 140),
        ("Planchado de ceja con depilación", 100),
        ("Retoque de uñas", 130),
        ("Retiro de acrilico", 50),
        ("Retiro de gelish", 40),
        ("Retiro de rubber", 40),
        ("Rizado de pestañas", 100),
        ("rubber uñas cortas", 130),
        ("rubber uñas medianas", 150),
        ("rubber uñas largas", 180),
        ("Uñas acrílicas corta", 150),
        ("uñas arilicas medianas", 175),
        ("uña acrílica larga", 200),
        ("uñas escultural cortas", 230),
        ("uñas escultural medianas", 280),
        ("uñas escultural largas", 300),
        ("Uñas con baby boomer cortas", 185),
        ("Uñas con baby boomer medianas", 200),
        ("Uñas con baby boomer largas", 220),
    ]

def seed_servicios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre FROM sedes ORDER BY id ASC")
    sedes = cur.fetchall()

    for (sid, nombre) in sedes:
        cur.execute("SELECT COUNT(*) FROM servicios WHERE sede_id=?", (sid,))
        n = cur.fetchone()[0]
        if n == 0:
            if "uña" in nombre.lower():
                data = _servicios_unias()
            else:
                data = _servicios_cabello()
            for (nom, precio) in data:
                cur.execute("INSERT INTO servicios(sede_id, nombre, precio) VALUES (?,?,?)", (sid, nom, float(precio)))
    conn.commit()
    conn.close()

# -------------------------- CITAS (extensión con servicio y precio) --------------------------
def asegurar_columnas_citas():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(citas)")
    cols = [c[1] for c in cur.fetchall()]
    try:
        if "servicio_id" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN servicio_id INTEGER")
        if "servicio_nombre" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN servicio_nombre TEXT")
        if "precio" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN precio REAL DEFAULT 0.0")
        if "empleada" not in cols:
            cur.execute("ALTER TABLE citas ADD COLUMN empleada TEXT")
        conn.commit()
    except Exception:
        pass
    conn.close()
