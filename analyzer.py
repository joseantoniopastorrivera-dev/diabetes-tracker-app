import os
import json
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY", "").strip()

if not api_key:
    raise RuntimeError("Falta GEMINI_API_KEY en el archivo .env")

client = genai.Client(api_key=api_key)

SYSTEM_PROMPT = """
Eres un asistente médico especializado en diabetes y análisis metabólico. Tu tarea es extraer datos numéricos, clínicos y la evolución temporal de los mensajes de texto, notas de voz o imágenes (capturas de pantalla de sensores continuos).

Extrae la siguiente información de forma precisa:
- glucosa: número entero en mg/dL del valor actual o principal que aparezca en pantalla o se mencione.
- tendencia_grafica: una lista de objetos con la evolución de la glucosa según la gráfica histórica de la imagen (si la hay), indicando la hora aproximada y el valor en mg/dL. Si no hay gráfica, asigna null.
- insulina_rapida: número decimal de unidades de insulina rápida o corrección, o null.
- insulina_basal: número decimal de unidades de insulina lenta/basal, o null.
- hidratos_hc: gramos estimados de hidratos de carbono consumidos (si se mencionan), o null.
- comida: una descripción o lista detallada de los alimentos consumidos incluyendo la hora exacta de cada ingesta en formato HH:MM (calculada a partir de la [INFORMACIÓN DE SISTEMA] si usa expresiones relativas como "hace un rato" o "a mediodía"). Ejemplo: "ensalada de pasta a las 14:17h, flan a las 11:03h". Si no hay comida, asigna null.
- ejercicio: descripción de la actividad física, o null.
- hipoglucemia: si se indica una bajada, calcula y extrae la hora exacta en formato HH:MM basándote en la [INFORMACIÓN DE SISTEMA] proporcionada. Si no hay datos de bajada, asigna null.
- sintomas: síntomas mencionados (ej: mareo, temblores, fatiga), o null.
- notas: contexto relevante (ej: estrés, falta de sueño, ciclo menstrual), o null.

Responde ÚNICAMENTE con un objeto JSON válido con este esquema exacto:
{
  "glucosa": <entero o null>,
  "tendencia_grafica": [{"hora": "<texto>", "glucosa": <entero>}, ...] o null,
  "insulina_rapida": <flotante o null>,
  "insulina_basal": <flotante o null>,
  "hidratos_hc": <entero o null>,
  "comida": <texto descriptivo con alimentos y horas o null>,
  "ejercicio": <texto o null>,
  "hipoglucemia": <texto con la hora en formato HH:MM o null>,
  "sintomas": <texto o null>,
  "notas": <texto o null>
}

Reglas estrictas:
- Si no se menciona o detecta un campo, asígnale null.
- Sé flexible interpretando expresiones cotidianas ("2 de rápida" -> insulina_rapida: 2.0).
- Devuelve únicamente el JSON puro, sin bloques de código markdown ni texto adicional.
"""

def analizar_mensaje_salud(texto: Optional[str] = None, imagen_bytes: Optional[bytes] = None, audio_bytes: Optional[bytes] = None, fecha_telegram: Optional[datetime] = None) -> Optional[Dict[str, Any]]:
    """Procesa texto, imágenes o notas de voz usando la fecha exacta en la que se envió el mensaje en Telegram."""
    try:
        # Si Telegram nos da la fecha del mensaje, la usamos; si no, tiramos de la hora actual del PC
        if fecha_telegram:
            # Ajustar UTC a hora de España (aproximadamente UTC+1 o UTC+2 según horario de verano/invierno)
            # O simplemente formatear la que trae Telegram que ya viene en UTC
            hora_real = fecha_telegram.strftime("%H:%M del %d/%m/%Y")
        else:
            hora_real = datetime.now().strftime("%H:%M del %d/%m/%Y")
        
        prompt_con_tiempo = f"[INFORMACIÓN DE SISTEMA: El mensaje fue enviado exactamente a las {hora_real}]. Contexto adicional: {texto or ''}"

        partes = []
        
        if imagen_bytes:
            partes.append(types.Part.from_bytes(data=imagen_bytes, mime_type="image/jpeg"))
            
        if audio_bytes:
            partes.append(types.Part.from_bytes(data=audio_bytes, mime_type="audio/ogg"))
            
        partes.append(prompt_con_tiempo)

        response = client.models.generate_content(
            model='gemini-3.8-flash',
            contents=partes,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                temperature=0.1
            )
        )
        
        if not response.text:
            return None

        return json.loads(response.text)

    except Exception as e:
        print(f"Error procesando con Gemini: {e}")
        return None