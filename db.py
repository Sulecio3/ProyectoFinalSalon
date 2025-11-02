import sqlite3

DB_FILE = "salon.db"

def get_connection():
    return sqlite3.connect(DB_FILE)


#---------------------------------LOGIIIIIIIIN-----------------------

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


#---------------------------------------------SEDEEEEES-----------------------------------------------------
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

#-----------------------------------------------------------------INVENTARIO-------------------------------------------
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

def crear_tabla_inventario():
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sede_id INTEGER NOT NULL,
            nombre TEXT NOT NULL,
            stock INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY(sede_id) REFERENCES sedes(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    conn.close()

def listar_inventario(sede_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, stock FROM inventario WHERE sede_id=?", (sede_id,))
    rows = cur.fetchall()
    conn.close()
    return rows

def insertar_producto(sede_id, nombre, stock):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO inventario(sede_id, nombre, stock) VALUES (?,?,?)",
        (sede_id, nombre, int(stock)),
    )
    conn.commit()
    conn.close()

def actualizar_producto(pid, nombre, stock):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE inventario SET nombre=?, stock=? WHERE id=?",
        (nombre, int(stock), int(pid)),
    )
    conn.commit()
    conn.close()

def eliminar_producto(pid):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM inventario WHERE id=?", (int(pid),))
    conn.commit()
    conn.close()

#------------------------------------VENTAAAAAAS-------------------------------------------------------------------
def crear_tabla_inventario():
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
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

def crear_tabla_ventas():
    conn = get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
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
    conn.execute("PRAGMA foreign_keys = ON")
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
        raise ValueError("Cantidad inválida o insuficiente stock.")

    nuevo_stock = stock_actual - cantidad
    cur.execute("UPDATE inventario SET stock=? WHERE id=?", (nuevo_stock, producto_id))

    total = float(precio_unitario) * cantidad
    cur.execute("""
        INSERT INTO ventas(sede_id, producto_id, cantidad, precio_unitario, total)
        VALUES (?,?,?,?,?)
    """, (sede_id, producto_id, cantidad, float(precio_unitario), total))

    conn.commit()
    conn.close()