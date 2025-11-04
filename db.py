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
    # users
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

    # resto de tablas
    crear_tabla_sedes()
    crear_tabla_inventario()
    asegurar_columna_precio()
    crear_tabla_ventas()
    crear_tabla_citas()
    ensure_sedes_iniciales()

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
            servicio TEXT NOT NULL,
            inicio TEXT NOT NULL,         -- 'HH:MM'
            fin TEXT NOT NULL,            -- 'HH:MM'
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def listar_citas(sede_id: int, fecha: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, cliente, servicio, inicio, fin
        FROM citas
        WHERE sede_id=? AND fecha=?
        ORDER BY inicio ASC
    """, (sede_id, fecha))
    rows = cur.fetchall()
    conn.close()
    return rows

def insertar_cita(sede_id: int, fecha: str, cliente: str, servicio: str, inicio: str, fin: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO citas(sede_id, fecha, cliente, servicio, inicio, fin)
        VALUES (?,?,?,?,?,?)
    """, (sede_id, fecha, cliente, servicio, inicio, fin))
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid

def actualizar_cita(cid: int, cliente: str, servicio: str, inicio: str, fin: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE citas SET cliente=?, servicio=?, inicio=?, fin=?
        WHERE id=?
    """, (cliente, servicio, inicio, fin, cid))
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
        SELECT id, sede_id, fecha, cliente, servicio, inicio, fin
        FROM citas
        WHERE id=?
    """, (cid,))
    row = cur.fetchone()
    conn.close()
    return row

