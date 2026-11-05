"""Pruebas del repositorio SQLite. Todos los datos son inventados."""
import sqlite3
from datetime import datetime

import pytest

from datos.repositorio import MIGRACIONES, Repositorio
from modelos import Estado, LecturaTendencia, Registro


@pytest.fixture
def repo(tmp_path):
    r = Repositorio(str(tmp_path / "prueba.db"))
    r.migrar()
    return r


def registro_de_prueba(**cambios) -> Registro:
    datos = dict(usuario_id=1, fecha_hora=datetime(2026, 11, 5, 14, 30), texto_original="120 y 4 de rápida",
                 glucosa=120, insulina_rapida=4.0)
    datos.update(cambios)
    return Registro(**datos)


def test_bd_nueva_queda_en_la_ultima_version(repo):
    assert repo.version() == len(MIGRACIONES)


def test_migrar_dos_veces_no_falla(repo):
    assert repo.migrar() == len(MIGRACIONES)


def test_migra_una_bd_de_la_v1_conservando_los_datos(tmp_path):
    ruta = tmp_path / "v1.db"
    with sqlite3.connect(ruta) as conn:  # BD tal y como la dejaba la v1 (user_version = 0)
        conn.execute(MIGRACIONES[0][0])
        conn.execute(
            "INSERT INTO registros (fecha_hora, usuario_id, usuario_alias, glucosa, insulina, comida, ejercicio, texto_original)"
            " VALUES ('2026-10-09 13:00:00', 7, 'Prueba', 150, 3.5, 'lentejas', NULL, 'texto')"
        )
    conn.close()

    repo = Repositorio(str(ruta))
    assert repo.migrar() == len(MIGRACIONES)

    antiguo = repo.obtener(1)
    assert antiguo.glucosa == 150
    assert antiguo.insulina_rapida == 3.5          # la columna "insulina" se renombró
    assert antiguo.comida == "lentejas"
    assert antiguo.estado is Estado.CONFIRMADO     # lo de la v1 cuenta como confirmado
    assert antiguo.insulina_basal is None


def test_guardar_y_obtener_con_tendencia(repo):
    r = registro_de_prueba(tendencia=[LecturaTendencia("13:00", 180), LecturaTendencia("14:00", 140)])
    nuevo_id = repo.guardar(r)

    leido = repo.obtener(nuevo_id)
    assert leido.estado is Estado.PENDIENTE
    assert leido.fecha_hora == datetime(2026, 11, 5, 14, 30)
    assert [(l.hora, l.glucosa) for l in leido.tendencia] == [("13:00", 180), ("14:00", 140)]


def test_actualizar_datos_reemplaza_la_tendencia(repo):
    r = registro_de_prueba(tendencia=[LecturaTendencia("13:00", 180)])
    repo.guardar(r)
    r.insulina_rapida = 3.0
    r.tendencia = []
    repo.actualizar_datos(r)

    leido = repo.obtener(r.id)
    assert leido.insulina_rapida == 3.0
    assert leido.tendencia == []


def test_confirmados_entre_filtra_por_estado_usuario_y_fechas(repo):
    a = registro_de_prueba(fecha_hora=datetime(2026, 11, 5, 9, 0))
    b = registro_de_prueba(fecha_hora=datetime(2026, 11, 5, 21, 0))
    pendiente = registro_de_prueba(fecha_hora=datetime(2026, 11, 5, 10, 0))
    otro_usuario = registro_de_prueba(usuario_id=2, fecha_hora=datetime(2026, 11, 5, 11, 0))
    ayer = registro_de_prueba(fecha_hora=datetime(2026, 11, 4, 23, 59))
    for r in (a, b, pendiente, otro_usuario, ayer):
        repo.guardar(r)
    for r in (a, b, otro_usuario, ayer):
        repo.cambiar_estado(r.id, Estado.CONFIRMADO)

    del_dia = repo.confirmados_entre(1, datetime(2026, 11, 5), datetime(2026, 11, 6))
    assert [r.id for r in del_dia] == [a.id, b.id]


def test_ultimo_por_estado(repo):
    primero = registro_de_prueba()
    segundo = registro_de_prueba()
    repo.guardar(primero)
    repo.guardar(segundo)
    assert repo.ultimo(1, Estado.PENDIENTE).id == segundo.id
    assert repo.ultimo(1, Estado.CONFIRMADO) is None
