"""Implementación del Extractor con Google Gemini (SDK google-genai)."""
import logging

from google import genai
from google.genai import types
from pydantic import ValidationError

from ia.extractor import DatosExtraidos, Entrada, ErrorExtraccion

log = logging.getLogger(__name__)

INSTRUCCIONES = """
Eres un asistente de REGISTRO para una persona con diabetes. Tu única tarea es extraer datos
de su mensaje (texto, nota de voz o captura de pantalla del sensor de glucosa).

Reglas:
- No eres médico. Nunca recomiendes dosis, tratamientos ni des consejos de salud.
- Extrae solo lo que aparece o se dice. Si un dato no está, déjalo en null. No inventes.
- Interpreta expresiones cotidianas: "2 de rápida" -> insulina_rapida 2.0; "me he metido 10 de lenta" -> insulina_basal 10.0.
- Convierte horas relativas ("hace media hora", "a mediodía") a HH:MM usando la hora del mensaje que se te indica.
- En una captura del sensor, el número grande es la glucosa actual; la gráfica va en tendencia_grafica.
- Si se te da un REGISTRO ANTERIOR y una CORRECCIÓN, devuelve el registro completo ya corregido:
  conserva lo que la corrección no menciona y cambia o borra lo que sí menciona.
"""


class GeminiExtractor:
    def __init__(self, api_key: str, modelo: str):
        self._cliente = genai.Client(api_key=api_key)
        self._modelo = modelo
        self._config = types.GenerateContentConfig(
            system_instruction=INSTRUCCIONES,
            response_mime_type="application/json",
            response_schema=DatosExtraidos,   # el modelo está obligado a seguir este esquema
            temperature=0.1,                  # poca creatividad: queremos datos, no prosa
        )

    async def extraer(self, entrada: Entrada) -> DatosExtraidos:
        partes: list = []
        if entrada.imagen:
            partes.append(types.Part.from_bytes(data=entrada.imagen, mime_type="image/jpeg"))
        if entrada.audio:
            partes.append(types.Part.from_bytes(data=entrada.audio, mime_type="audio/ogg"))
        partes.append(construir_prompt(entrada))

        try:
            # client.aio = versión asíncrona: el bot sigue atendiendo mientras Gemini responde
            respuesta = await self._cliente.aio.models.generate_content(
                model=self._modelo, contents=partes, config=self._config,
            )
        except Exception as e:  # red, cuota, clave inválida... (no se loguea el contenido del mensaje)
            log.error("Error llamando a Gemini: %s", type(e).__name__)
            raise ErrorExtraccion("No se pudo contactar con la IA") from e

        if isinstance(respuesta.parsed, DatosExtraidos):
            return respuesta.parsed
        try:  # por si el SDK no pudo convertirlo: validamos el texto nosotros
            return DatosExtraidos.model_validate_json(respuesta.text or "")
        except ValidationError as e:
            raise ErrorExtraccion("La IA devolvió datos con un formato inesperado") from e


def construir_prompt(entrada: Entrada) -> str:
    """Texto que acompaña a la imagen/audio. Función aparte para poder probarla sin API."""
    lineas = [f"Hora del mensaje: {entrada.momento:%H:%M} del {entrada.momento:%d/%m/%Y} (hora de España)."]
    if entrada.corrige_a is not None:
        lineas.append("REGISTRO ANTERIOR (JSON): " + entrada.corrige_a.model_dump_json(exclude_none=True))
        lineas.append(f"CORRECCIÓN de la usuaria: {entrada.texto}")
    elif entrada.texto:
        lineas.append(f"Mensaje: {entrada.texto}")
    if entrada.audio:
        lineas.append("La usuaria ha enviado una nota de voz: transcríbela mentalmente y extrae los datos.")
    return "\n".join(lineas)
