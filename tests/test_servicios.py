"""Pruebas de la lógica con un extractor falso: sin red, sin coste, deterministas."""
from datetime import datetime, timezone

import pytest

from datos.repositorio import Repositorio
from ia.extractor import DatosExtraidos, Entrada
from modelos import Estado
from servicios import ErrorOperacion, ServicioRegistros

MARTA, OTRA = 1, 2
# 13:30 UTC del 5/11 = 14:30 en Madrid (horario de invierno, UTC+1)
MOMENTO_UTC = datetime(2026, 11, 5, 13, 30, tzinfo=timezone.utc)


class ExtractorFalso:
    """Devuelve siempre lo que le digamos y apunta qué le han pedido."""

    def __init__(self, respuesta: DatosExtraidos):
        self.respuesta = respuesta
        self.recibido: list[Entrada] = []

    async def extraer(self, entrada: Entrada) -> DatosExtraidos:
        self.recibido.append(entrada)
        return self.respuesta


@pytest.fixture
def repo(tmp_path):
    r = Repositorio(str(tmp_path / "prueba.db"))
    r.migrar()
    return r


def servicio(repo, **datos) -> ServicioRegistros:
    return ServicioRegistros(repo, ExtractorFalso(DatosExtraidos(**datos)))


async def test_analizar_guarda_pendiente_en_hora_de_espana(repo):
    s = servicio(repo, glucosa=120, insulina_rapida=4.0)
    r = await s.analizar(MARTA, "Marta", Entrada(momento=MOMENTO_UTC, texto="120 y 4 de rápida"))

    guardado = repo.obtener(r.id)
    assert guardado.estado is Estado.PENDIENTE
    assert guardado.fecha_hora == datetime(2026, 11, 5, 14, 30)
    assert guardado.insulina_rapida == 4.0


async def test_analizar_sin_datos_no_guarda(repo):
    s = servicio(repo)  # la IA no encuentra nada
    r = await s.analizar(MARTA, None, Entrada(momento=MOMENTO_UTC, texto="hola"))
    assert r.id is None


async def test_confirmar_y_doble_clic(repo):
    s = servicio(repo, glucosa=120)
    r = await s.analizar(MARTA, None, Entrada(momento=MOMENTO_UTC, texto="120"))

    s.confirmar(MARTA, r.id)
    assert repo.obtener(r.id).estado is Estado.CONFIRMADO
    with pytest.raises(ErrorOperacion, match="ya está confirmado"):
        s.confirmar(MARTA, r.id)


async def test_no_se_puede_tocar_un_registro_ajeno(repo):
    s = servicio(repo, glucosa=120)
    r = await s.analizar(MARTA, None, Entrada(momento=MOMENTO_UTC, texto="120"))
    with pytest.raises(ErrorOperacion):
        s.confirmar(OTRA, r.id)


async def test_corregir_manda_el_registro_anterior_y_guarda_rastro(repo):
    s = servicio(repo, glucosa=120, insulina_rapida=4.0)
    r = await s.analizar(MARTA, None, Entrada(momento=MOMENTO_UTC, texto="120 y 4 de rápida"))

    s.extractor.respuesta = DatosExtraidos(glucosa=120, insulina_rapida=3.0)
    await s.corregir(MARTA, r.id, Entrada(momento=MOMENTO_UTC, texto="eran 3"))

    assert s.extractor.recibido[-1].corrige_a.insulina_rapida == 4.0
    corregido = repo.obtener(r.id)
    assert corregido.insulina_rapida == 3.0
    assert corregido.estado is Estado.PENDIENTE          # sigue esperando el ✅
    assert "[corrección] eran 3" in corregido.texto_original


async def test_descartar(repo):
    s = servicio(repo, glucosa=120)
    r = await s.analizar(MARTA, None, Entrada(momento=MOMENTO_UTC, texto="120"))
    s.descartar(MARTA, r.id)
    assert repo.obtener(r.id).estado is Estado.DESCARTADO


async def test_deshacer_anula_el_ultimo_confirmado(repo):
    s = servicio(repo, glucosa=120)
    primero = await s.analizar(MARTA, None, Entrada(momento=MOMENTO_UTC, texto="120"))
    segundo = await s.analizar(MARTA, None, Entrada(momento=MOMENTO_UTC, texto="120"))
    s.confirmar(MARTA, primero.id)
    s.confirmar(MARTA, segundo.id)

    assert s.deshacer(MARTA).id == segundo.id
    assert repo.obtener(segundo.id).estado is Estado.ANULADO
    assert repo.obtener(primero.id).estado is Estado.CONFIRMADO


def test_deshacer_sin_nada(repo):
    with pytest.raises(ErrorOperacion):
        servicio(repo).deshacer(MARTA)
