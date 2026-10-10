import sqlite3
from datetime import datetime
from typing import Optional, List, Tuple

DB_PATH = "diabetes_tracker.db"

def init_db() -> None:
    """Inicializa la base de datos y crea la tabla si no existe."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_hora TEXT NOT NULL,
                usuario_id INTEGER NOT NULL,
                usuario_alias TEXT,
                glucosa INTEGER,
                insulina REAL,
                comida TEXT,
                ejercicio TEXT,
                texto_original TEXT NOT NULL
            )
        """)
        conn.commit()

def guardar_registro(
    usuario_id: int,
    usuario_alias: Optional[str],
    glucosa: Optional[int],
    insulina: Optional[float],
    comida: Optional[str],
    ejercicio: Optional[str],
    texto_original: str
) -> int:
    """Inserta un nuevo registro y retorna su ID generado."""
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO registros (
                fecha_hora,
                usuario_id,
                usuario_alias,
                glucosa,
                insulina,
                comida,
                ejercicio,
                texto_original
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            fecha_actual,
            usuario_id,
            usuario_alias,
            glucosa,
            insulina,
            comida,
            ejercicio,
            texto_original
        ))
        conn.commit()
        return cursor.lastrowid or 0

def obtener_ultimos_registros(usuario_id: int, limite: int = 5) -> List[Tuple]:
    """Obtiene el histórico más reciente de un usuario."""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT fecha_hora, glucosa, insulina, comida, ejercicio
            FROM registros
            WHERE usuario_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (usuario_id, limite))
        return cursor.fetchall()