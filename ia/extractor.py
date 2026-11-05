"""Contrato de la capa de IA: qué entra, qué sale. No sabe nada de Gemini.

Cualquier proveedor (Gemini, Mistral, un modelo local o un falso para los tests)
solo tiene que implementar `Extractor.extraer`.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, Field


class LecturaIA(BaseModel):
    hora: str = Field(description="Hora aproximada del punto de la gráfica, formato HH:MM")
    glucosa: int = Field(description="Glucosa en mg/dL en ese punto")


class DatosExtraidos(BaseModel):
    """Lo que la IA devuelve. También sirve de esquema JSON obligatorio para el modelo."""
    glucosa: int | None = Field(None, description="Glucosa actual o principal en mg/dL")
    tendencia_grafica: list[LecturaIA] | None = Field(None, description="Puntos de la gráfica del sensor, si hay imagen con gráfica")
    insulina_rapida: float | None = Field(None, description="Unidades de insulina rápida o de corrección")
    insulina_basal: float | None = Field(None, description="Unidades de insulina lenta o basal")
    hidratos_hc: int | None = Field(None, description="Gramos de hidratos de carbono, solo si se mencionan o se pueden leer")
    comida: str | None = Field(None, description="Alimentos con la hora de cada ingesta en HH:MM")
    ejercicio: str | None = Field(None, description="Actividad física descrita")
    hipoglucemia: str | None = Field(None, description="Hora HH:MM de la bajada, si se indica")
    sintomas: str | None = Field(None, description="Síntomas mencionados (mareo, temblores...)")
    notas: str | None = Field(None, description="Contexto relevante: estrés, sueño, ciclo menstrual...")


@dataclass
class Entrada:
    momento: datetime                     # hora real del mensaje, ya en hora de España
    texto: str = ""
    imagen: bytes | None = None           # JPEG (las fotos de Telegram siempre lo son)
    audio: bytes | None = None            # OGG/Opus (notas de voz de Telegram)
    corrige_a: DatosExtraidos | None = None  # si es una corrección, el registro que se corrige


class ErrorExtraccion(Exception):
    """La IA no respondió o respondió algo que no cumple el esquema."""


class Extractor(Protocol):
    async def extraer(self, entrada: Entrada) -> DatosExtraidos: ...
