"""Pruebas de la capa de IA que no llaman a la API (no gastan cuota)."""
from datetime import datetime

from config import ZONA_HORARIA
from ia.extractor import DatosExtraidos, Entrada
from ia.gemini import construir_prompt

MOMENTO = datetime(2026, 11, 5, 14, 7, tzinfo=ZONA_HORARIA)


def test_prompt_incluye_hora_de_espana_y_mensaje():
    prompt = construir_prompt(Entrada(momento=MOMENTO, texto="120 y 4 de rápida"))
    assert "14:07 del 05/11/2026" in prompt
    assert "Mensaje: 120 y 4 de rápida" in prompt


def test_prompt_de_correccion_incluye_registro_anterior():
    anterior = DatosExtraidos(glucosa=120, insulina_rapida=4.0)
    prompt = construir_prompt(Entrada(momento=MOMENTO, texto="eran 3 de rápida", corrige_a=anterior))
    assert '"insulina_rapida":4.0' in prompt
    assert "CORRECCIÓN de la usuaria: eran 3 de rápida" in prompt
    assert "null" not in prompt  # no mandamos campos vacíos: menos tokens


def test_esquema_acepta_respuesta_parcial():
    datos = DatosExtraidos.model_validate_json('{"glucosa": 95, "tendencia_grafica": [{"hora": "13:00", "glucosa": 110}]}')
    assert datos.glucosa == 95
    assert datos.insulina_rapida is None
    assert datos.tendencia_grafica[0].glucosa == 110
