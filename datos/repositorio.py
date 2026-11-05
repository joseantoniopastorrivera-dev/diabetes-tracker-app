"""Acceso a SQLite. Es la única parte del programa que escribe SQL."""
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime

from modelos import Estado, LecturaTendencia, Registro

FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"   # el mismo que usaba la v1, para no romper sus datos

# Cada migración lleva la BD de la versión N-1 a la N. Nunca se edita una que
# ya se haya ejecutado: si hace falta otro cambio, se añade una nueva al final.
MIGRACIONES: list[list[str]] = [
    # 1 · Esquema de la v1. IF NOT EXISTS: en una BD de la v1 ya existe y no hace nada.
    [
        """CREATE TABLE IF NOT EXISTS registros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha_hora TEXT NOT NULL,
            usuario_id INTEGER NOT NULL,
            usuario_alias TEXT,
            glucosa INTEGER,
            insulina REAL,
            comida TEXT,
            ejercicio TEXT,
            texto_original TEXT NOT NULL
        )""",
    ],
    # 2 · v2: guardar todo lo que extrae la IA, estado de confirmación y tendencia.
    [
        "ALTER TABLE registros RENAME COLUMN insulina TO insulina_rapida",
        "ALTER TABLE registros ADD COLUMN insulina_basal REAL",
        "ALTER TABLE registros ADD COLUMN hidratos_hc INTEGER",
        "ALTER TABLE registros ADD COLUMN hipoglucemia TEXT",
        "ALTER TABLE registros ADD COLUMN sintomas TEXT",
        "ALTER TABLE registros ADD COLUMN notas TEXT",
        # Lo que había en la v1 se guardó sin preguntar: lo damos por confirmado.
        "ALTER TABLE registros ADD COLUMN estado TEXT NOT NULL DEFAULT 'confirmado'",
        """CREATE TABLE lecturas_tendencia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            registro_id INTEGER NOT NULL REFERENCES registros(id) ON DELETE CASCADE,
            hora TEXT NOT NULL,
            glucosa INTEGER NOT NULL
        )""",
        "CREATE INDEX idx_registros_usuario_fecha ON registros(usuario_id, fecha_hora)",
    ],
]

CAMPOS_DATOS = ("glucosa", "insulina_rapida", "insulina_basal", "hidratos_hc", "comida",
                "ejercicio", "hipoglucemia", "sintomas", "notas")


class Repositorio:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def _sesion(self) -> Iterator[sqlite3.Connection]:
        """Abre conexión, hace commit (o rollback si hay excepción) y SIEMPRE la cierra.

        Ojo: `with sqlite3.connect(...)` por sí solo hace commit pero NO cierra la conexión.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row             # filas accesibles por nombre: fila["glucosa"]
        conn.execute("PRAGMA foreign_keys = ON")    # SQLite no comprueba las FK si no se activa
        try:
            with conn:
                yield conn
        finally:
            conn.close()

    # ---------- Esquema ----------

    def version(self) -> int:
        with self._sesion() as conn:
            return conn.execute("PRAGMA user_version").fetchone()[0]

    def migrar(self) -> int:
        """Aplica las migraciones pendientes, cada una en su transacción. Devuelve la versión final."""
        actual = self.version()
        for numero, sentencias in enumerate(MIGRACIONES, start=1):
            if numero <= actual:
                continue
            with self._sesion() as conn:  # una transacción por migración: o entera o nada
                for sql in sentencias:
                    conn.execute(sql)
                conn.execute(f"PRAGMA user_version = {numero}")
        return self.version()

    # ---------- Escritura ----------

    def guardar(self, registro: Registro) -> int:
        """Inserta el registro (normalmente en estado pendiente) y su tendencia."""
        columnas = ("fecha_hora", "usuario_id", "usuario_alias", "texto_original", "estado") + CAMPOS_DATOS
        valores = (
            registro.fecha_hora.strftime(FORMATO_FECHA), registro.usuario_id, registro.usuario_alias,
            registro.texto_original, registro.estado.value,
            *(getattr(registro, c) for c in CAMPOS_DATOS),
        )
        huecos = ", ".join("?" for _ in columnas)
        with self._sesion() as conn:  # registro y tendencia en la misma transacción
            cur = conn.execute(f"INSERT INTO registros ({', '.join(columnas)}) VALUES ({huecos})", valores)
            registro.id = cur.lastrowid
            self._guardar_tendencia(conn, registro)
        return registro.id

    def actualizar_datos(self, registro: Registro) -> None:
        """Sobrescribe los datos extraídos (tras una corrección) y la tendencia."""
        asignaciones = ", ".join(f"{c} = ?" for c in CAMPOS_DATOS)
        with self._sesion() as conn:
            conn.execute(
                f"UPDATE registros SET {asignaciones}, texto_original = ? WHERE id = ?",
                (*(getattr(registro, c) for c in CAMPOS_DATOS), registro.texto_original, registro.id),
            )
            conn.execute("DELETE FROM lecturas_tendencia WHERE registro_id = ?", (registro.id,))
            self._guardar_tendencia(conn, registro)

    def cambiar_estado(self, registro_id: int, estado: Estado) -> None:
        with self._sesion() as conn:
            conn.execute("UPDATE registros SET estado = ? WHERE id = ?", (estado.value, registro_id))

    @staticmethod
    def _guardar_tendencia(conn: sqlite3.Connection, registro: Registro) -> None:
        conn.executemany(
            "INSERT INTO lecturas_tendencia (registro_id, hora, glucosa) VALUES (?, ?, ?)",
            [(registro.id, l.hora, l.glucosa) for l in registro.tendencia],
        )

    # ---------- Lectura ----------

    def obtener(self, registro_id: int) -> Registro | None:
        with self._sesion() as conn:
            fila = conn.execute("SELECT * FROM registros WHERE id = ?", (registro_id,)).fetchone()
            return self._a_registro(conn, fila) if fila else None

    def ultimo(self, usuario_id: int, estado: Estado) -> Registro | None:
        with self._sesion() as conn:
            fila = conn.execute(
                "SELECT * FROM registros WHERE usuario_id = ? AND estado = ? ORDER BY id DESC LIMIT 1",
                (usuario_id, estado.value),
            ).fetchone()
            return self._a_registro(conn, fila) if fila else None

    def confirmados_entre(self, usuario_id: int, desde: datetime, hasta: datetime) -> list[Registro]:
        """Registros confirmados con desde <= fecha_hora < hasta, en orden cronológico."""
        with self._sesion() as conn:
            filas = conn.execute(
                """SELECT * FROM registros
                   WHERE usuario_id = ? AND estado = ? AND fecha_hora >= ? AND fecha_hora < ?
                   ORDER BY fecha_hora""",
                (usuario_id, Estado.CONFIRMADO.value, desde.strftime(FORMATO_FECHA), hasta.strftime(FORMATO_FECHA)),
            ).fetchall()
            return [self._a_registro(conn, f) for f in filas]

    @staticmethod
    def _a_registro(conn: sqlite3.Connection, fila: sqlite3.Row) -> Registro:
        tendencia = [
            LecturaTendencia(hora=t["hora"], glucosa=t["glucosa"])
            for t in conn.execute(
                "SELECT hora, glucosa FROM lecturas_tendencia WHERE registro_id = ? ORDER BY id", (fila["id"],)
            )
        ]
        return Registro(
            id=fila["id"],
            usuario_id=fila["usuario_id"],
            usuario_alias=fila["usuario_alias"],
            fecha_hora=datetime.strptime(fila["fecha_hora"], FORMATO_FECHA),
            texto_original=fila["texto_original"],
            estado=Estado(fila["estado"]),
            tendencia=tendencia,
            **{c: fila[c] for c in CAMPOS_DATOS},
        )
