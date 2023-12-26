# database.py
import sys
import os
import sqlite3
import hashlib
from datetime import datetime

DATABASE_FILENAME = '../data/invoices.db'

def get_db_connection():

    conn = sqlite3.connect(DATABASE_FILENAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS Factura (
            id_user INTEGER,
            id_factura INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_factura bit,
            fecha DATE,
            nombre_cliente TEXT NOT NULL,
            dni_cliente TEXT NOT NULL,
            direccion_cliente TEXT NOT NULL,
            referencia TEXT NUL,
            FOREIGN KEY (id_user) REFERENCES users (id)
        );
                    
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS presupuesto (
            id_user INTEGER,
            id_presupuesto INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_presupuesto bit,
            fecha DATE,
            nombre_cliente TEXT NOT NULL,
            dni_cliente TEXT NOT NULL,
            direccion_cliente TEXT NOT NULL,
            FOREIGN KEY (id_user) REFERENCES users (id)
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS Concepto (
            id_concepto INTEGER PRIMARY KEY AUTOINCREMENT,
            id_factura INTEGER,
            descripcion TEXT,
            cantidad INTEGER,
            precio DECIMAL,
            tecnico INTEGER,
            FOREIGN KEY (id_factura) REFERENCES Factura (id_factura)
        );
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS Concepto_presupuesto (
            id_concepto_p INTEGER PRIMARY KEY AUTOINCREMENT,
            id_presupuesto INTEGER,
            descripcion TEXT,
            cantidad INTEGER,
            precio DECIMAL,
            tecnico INTEGER,
            FOREIGN KEY (id_presupuesto) REFERENCES presupuesto (id_presupuesto)
        );
    """)

    conn.execute("""
        CREATE VIEW IF NOT EXISTS ResumenFactura AS
        SELECT
            f.id_factura,
            f.fecha,
            f.tipo_factura,
            f.nombre_cliente,
            f.dni_cliente,
            f.direccion_cliente,
            f.referencia,
            c.id_concepto,
            c.descripcion,
            c.cantidad,
            c.precio,
            c.tecnico,
            c.precio / (1 + (21 / 100.0)) AS precio_sin_iva
        FROM Factura f
        JOIN Concepto c ON f.id_factura = c.id_factura;
    """)


    conn.execute("""
        CREATE VIEW IF NOT EXISTS Resumenpresupuesto AS
        SELECT
            p.id_presupuesto,
            p.fecha,
            p.tipo_presupuesto,
            p.nombre_cliente,
            p.dni_cliente,
            p.direccion_cliente,
            c.id_concepto_p,
            c.descripcion,
            c.cantidad,
            c.precio,
            c.tecnico,
            c.precio / (1 + (21 / 100.0)) AS precio_sin_iva
        FROM presupuesto p
        JOIN Concepto_presupuesto c ON p.id_presupuesto = c.id_presupuesto;
    """)
    
    conn.close()

def update_admin_password():
    admin_username = 'admin'
    new_password = 'admin'  # Nueva contraseña deseada
    hashed_password = hash_password(new_password)
    
    conn = get_db_connection()
    with conn:
        conn.execute("UPDATE users SET password = ? WHERE username = ?", (hashed_password, admin_username))
    conn.close()

def create_admin_user():
    admin_username = 'admin'
    admin_password = 'admin'  # Nueva contraseña
    hashed_password = hash_password(admin_password)
    
    conn = get_db_connection()
    # Verifica si el usuario admin ya existe
    admin_exists = conn.execute("SELECT 1 FROM users WHERE username = ?", (admin_username,)).fetchone()
    
    if not admin_exists:
        # Si no existe, lo crea
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (admin_username, hashed_password))
        conn.commit()
    conn.close()

def hash_password(password):
    # Esto encriptará la contraseña usando SHA-256
    return hashlib.sha256(password.encode()).hexdigest()

# Función para añadir un nuevo usuario
def add_user(username, password):
    hashed_password = hash_password(password)
    conn = get_db_connection()
    with conn:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.close()

def insert_factura(id_user, nombre_cliente, dni_cliente, direccion_cliente,tipo_factura,referencia):
    conn = get_db_connection()
    fecha_actual = datetime.now().date()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO Factura (id_user, fecha, nombre_cliente, dni_cliente, direccion_cliente,tipo_factura,referencia)
            VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (id_user,fecha_actual, nombre_cliente, dni_cliente, direccion_cliente,tipo_factura,referencia))
        id_factura = cursor.lastrowid
        conn.commit()
    return id_factura

def insert_presupuesto(id_user, nombre_cliente, dni_cliente, direccion_cliente,tipo_presupuesto):
    conn = get_db_connection()
    fecha_actual = datetime.now().date()
    with conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO presupuesto (id_user, fecha, nombre_cliente, dni_cliente, direccion_cliente,tipo_presupuesto)
            VALUES (?, ?, ?, ?, ?, ?);
        """, (id_user,fecha_actual, nombre_cliente, dni_cliente, direccion_cliente,tipo_presupuesto))
        id_presupuesto = cursor.lastrowid
        conn.commit()
    return id_presupuesto

def insert_concepto(id_factura, descripcion, cantidad, precio,tecnico):
    conn = get_db_connection()
    with conn:
        conn.execute("""
            INSERT INTO Concepto (id_factura, descripcion, cantidad, precio,tecnico)
            VALUES (?, ?, ?, ?, ?);
        """, (id_factura, descripcion, cantidad, precio, tecnico))
        conn.commit()

def insert_concepto_presupuesto(id_presupuesto, descripcion, cantidad, precio,tecnico):
    conn = get_db_connection()
    with conn:
        conn.execute("""
            INSERT INTO Concepto_presupuesto (id_presupuesto, descripcion, cantidad, precio,tecnico)
            VALUES (?, ?, ?, ?, ?);
        """, (id_presupuesto, descripcion, cantidad, precio,tecnico))
        conn.commit()
        
def delete_invoice_from_database(id_factura):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First, delete the associated 'conceptos'
        cursor.execute("DELETE FROM concepto WHERE id_factura = ?", (id_factura,))

        # Then, delete the invoice
        cursor.execute("DELETE FROM factura WHERE id = ?", (id_factura,))

        # Commit the changes
        conn.commit()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    init_db()