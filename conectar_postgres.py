#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para conectarse y probar la base de datos PostgreSQL en AWS RDS
"""

import psycopg2
from tabulate import tabulate
import sys

# Colores para terminal
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{bcolors.HEADER}{bcolors.BOLD}=== {text} ==={bcolors.ENDC}\n")

def print_success(text):
    print(f"{bcolors.OKGREEN}✓ {text}{bcolors.ENDC}")

def print_error(text):
    print(f"{bcolors.FAIL}✗ {text}{bcolors.ENDC}")

def print_warning(text):
    print(f"{bcolors.WARNING}! {text}{bcolors.ENDC}")

def print_table(headers, data):
    print(tabulate(data, headers=headers, tablefmt="pretty"))

# Parámetros de conexión
host = "notas-biblot.cx04yq02qa22.us-east-2.rds.amazonaws.com"
dbname = "postgres"
user = "biblot"
password = "juan0521"
port = "5432"

# Función principal
def main():
    conn = None
    cursor = None
    
    try:
        # Conectar a la base de datos
        print_header("CONECTANDO A LA BASE DE DATOS")
        print(f"Host: {host}")
        print(f"Base de datos: {dbname}")
        print(f"Usuario: {user}")
        print(f"Puerto: {port}")
        
        # Cadena de conexión
        conn_string = f"host={host} dbname={dbname} user={user} password={password} port={port}"
        
        # Establecer conexión
        print("\nIntentando conectar...")
        conn = psycopg2.connect(conn_string)
        
        # Crear cursor
        cursor = conn.cursor()
        
        print_success("¡Conexión establecida exitosamente!")
        
        # Listar tablas
        print_header("TABLAS EN LA BASE DE DATOS")
        cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema='public'
        """)
        
        tables = cursor.fetchall()
        
        if tables:
            print_success(f"Se encontraron {len(tables)} tablas:")
            for table in tables:
                print(f"- {table[0]}")
        else:
            print_warning("No hay tablas en la base de datos.")
        
        # Verificar usuarios
        if any('users' == table[0] for table in tables):
            print_header("USUARIOS")
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            
            # Obtener nombres de columnas
            column_names = [desc[0] for desc in cursor.description]
            
            if users:
                print_success(f"Se encontraron {len(users)} usuarios:")
                print_table(column_names, users)
            else:
                print_warning("No hay usuarios registrados.")
        
        # Verificar notas
        if any('notes' == table[0] for table in tables):
            print_header("NOTAS")
            cursor.execute("""
            SELECT n.id, u.username, n.book, n.chapter, n.verse, n.verse_text, n.note, n.created_at
            FROM notes n
            JOIN users u ON n.user_id = u.id
            ORDER BY n.created_at DESC
            """)
            
            notes = cursor.fetchall()
            
            # Obtener nombres de columnas
            column_names = [desc[0] for desc in cursor.description]
            
            if notes:
                print_success(f"Se encontraron {len(notes)} notas:")
                print_table([col for col in column_names if col not in ['verse_text']], 
                           [[row[i] if i != column_names.index('verse_text') else '...' for i in range(len(row))] 
                            for row in notes])
            else:
                print_warning("No hay notas guardadas.")
        
        # Crear tabla de prueba
        print_header("CREANDO TABLA DE PRUEBA")
        try:
            # Crear tabla
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Insertar un registro
            cursor.execute("""
            INSERT INTO test_table (name) VALUES ('Test desde script Python')
            """)
            
            # Confirmar los cambios
            conn.commit()
            
            print_success("Tabla de prueba creada y datos insertados correctamente.")
            
            # Verificar datos
            cursor.execute("SELECT * FROM test_table")
            test_data = cursor.fetchall()
            
            # Obtener nombres de columnas
            column_names = [desc[0] for desc in cursor.description]
            
            if test_data:
                print_success(f"Datos en la tabla de prueba:")
                print_table(column_names, test_data)
            else:
                print_warning("No hay datos en la tabla de prueba.")
                
        except Exception as e:
            conn.rollback()
            print_error(f"Error al crear tabla de prueba: {e}")
        
    except Exception as e:
        print_error(f"Error: {e}")
    finally:
        # Cerrar cursor y conexión
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print_success("Conexión cerrada correctamente.")

if __name__ == "__main__":
    try:
        # Verificar si psycopg2 está instalado
        import psycopg2
    except ImportError:
        print_error("La biblioteca psycopg2 no está instalada.")
        print("Instálala con: pip install psycopg2-binary tabulate")
        sys.exit(1)
        
    try:
        # Verificar si tabulate está instalado
        import tabulate
    except ImportError:
        print_error("La biblioteca tabulate no está instalada.")
        print("Instálala con: pip install tabulate")
        sys.exit(1)
        
    main() 