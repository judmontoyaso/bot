import os
import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime
from dotenv import load_dotenv
import logging
import time

# Configurar el logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('database')

load_dotenv()

class Database:
    def __init__(self):
        # Obtener variables de entorno
        self.db_url = os.getenv('DATABASE_URL')
        if not self.db_url:
            logger.error("DATABASE_URL no está configurada en las variables de entorno")
            raise ValueError("DATABASE_URL no está configurada en las variables de entorno")
        
        self.max_retries = 3
        self.retry_delay = 5  # segundos
        self.connect()
    
    def connect(self):
        """Establece la conexión a la base de datos con reintentos"""
        for attempt in range(self.max_retries):
            try:
                # Conectar a la base de datos con parámetros SSL
                logger.info(f"Intento {attempt + 1} de {self.max_retries} para conectar a la base de datos: {self.db_url.split('@')[1]}")
                self.conn = psycopg2.connect(
                    self.db_url,
                    sslmode='require',
                    connect_timeout=10,
                    keepalives=1,
                    keepalives_idle=30,
                    keepalives_interval=10,
                    keepalives_count=5
                )
                self.cursor = self.conn.cursor(cursor_factory=DictCursor)
                logger.info("Conexión a la base de datos establecida correctamente")
                
                # Crear tablas si no existen
                self.create_tables()
                return
            except psycopg2.OperationalError as e:
                logger.error(f"Error de conexión (intento {attempt + 1}): {str(e)}")
                if attempt < self.max_retries - 1:
                    logger.info(f"Reintentando en {self.retry_delay} segundos...")
                    time.sleep(self.retry_delay)
                else:
                    logger.error("Se agotaron los intentos de conexión")
                    raise
            except Exception as e:
                logger.error(f"Error inesperado al conectar a la base de datos: {str(e)}")
                raise
    
    def ensure_connection(self):
        """Asegura que la conexión está activa"""
        try:
            if not hasattr(self, 'conn') or not self.conn or self.conn.closed:
                logger.info("Reconectando a la base de datos...")
                self.connect()
            elif self.cursor.closed:
                logger.info("Recreando cursor...")
                self.cursor = self.conn.cursor(cursor_factory=DictCursor)
            
            # Verificar que la conexión está viva
            self.cursor.execute('SELECT 1')
            self.cursor.fetchone()
        except Exception as e:
            logger.error(f"Error al asegurar la conexión: {str(e)}")
            self.connect()  # Intentar reconectar si hay error
    
    def create_tables(self):
        """Crea las tablas necesarias si no existen"""
        try:
            # Tabla de usuarios
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Tabla de notas
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id SERIAL PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    book TEXT NOT NULL,
                    chapter INTEGER NOT NULL,
                    verse INTEGER NOT NULL,
                    verse_text TEXT NOT NULL,
                    note TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
            
            self.conn.commit()
            logger.info("Tablas creadas o verificadas correctamente")
        except Exception as e:
            logger.error(f"Error al crear las tablas: {str(e)}")
            raise
    
    def get_or_create_user(self, user_id, username):
        """Obtiene o crea un usuario"""
        try:
            self.ensure_connection()
            self.cursor.execute('SELECT id FROM users WHERE id = %s', (user_id,))
            result = self.cursor.fetchone()
            
            if not result:
                logger.info(f"Creando nuevo usuario: {username} (ID: {user_id})")
                self.cursor.execute(
                    'INSERT INTO users (id, username) VALUES (%s, %s)',
                    (user_id, username)
                )
                self.conn.commit()
            else:
                logger.info(f"Usuario existente: {username} (ID: {user_id})")
            
            return user_id
        except Exception as e:
            logger.error(f"Error en get_or_create_user: {str(e)}")
            self.conn.rollback()
            raise
    
    def add_note(self, user_id, book, chapter, verse, verse_text, note):
        """Añade una nota a un versículo"""
        try:
            self.ensure_connection()
            logger.info(f"Añadiendo nota para {book} {chapter}:{verse} del usuario {user_id}")
            self.cursor.execute('''
                INSERT INTO notes (user_id, book, chapter, verse, verse_text, note)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (user_id, book, chapter, verse, verse_text, note))
            self.conn.commit()
            logger.info("Nota guardada correctamente")
        except Exception as e:
            logger.error(f"Error al añadir nota: {str(e)}")
            self.conn.rollback()
            raise
    
    def get_user_notes(self, user_id):
        """Obtiene todas las notas de un usuario"""
        try:
            self.ensure_connection()
            logger.info(f"Obteniendo notas del usuario {user_id}")
            self.cursor.execute('''
                SELECT note, created_at, book, chapter, verse
                FROM notes
                WHERE user_id = %s
                ORDER BY created_at DESC
            ''', (user_id,))
            result = self.cursor.fetchall()
            logger.info(f"Se encontraron {len(result)} notas")
            
            # Imprimir cada nota para depuración
            for i, note_data in enumerate(result):
                logger.info(f"Nota {i+1}: {note_data}")
            
            return result
        except Exception as e:
            logger.error(f"Error al obtener notas: {str(e)}")
            raise
    
    def __del__(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'conn'):
            try:
                self.conn.close()
                logger.info("Conexión a la base de datos cerrada correctamente")
            except Exception as e:
                logger.error(f"Error al cerrar la conexión: {str(e)}") 