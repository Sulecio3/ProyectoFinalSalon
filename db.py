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