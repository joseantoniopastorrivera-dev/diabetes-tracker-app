# Registro de decisiones

Cada decisión importante, con su motivo. Es el "registro de decisiones" que promete la memoria del proyecto emprendedor (apartado 4.3). Las nuevas van al final.

## D1 · Arquitectura por capas (v2, fase 1, noviembre de 2026)
**Decisión:** separar el código en `modelos` → `datos` (SQLite) → `ia` (extractor) → `servicios` (lógica) → `telegram_bot` (canal).
**Motivo:** en la v1, `bot.py` mezclaba Telegram, la lógica y el formato. La fase 3 añadirá una API y una app móvil: con capas, eso consiste en añadir un cliente que llame a `servicios`, sin reescribir nada.
**Alternativa descartada:** mantener los tres ficheros de la v1. Es más rápido hoy, pero obliga a duplicar la lógica después.

## D2 · Nada se guarda sin confirmar
**Decisión:** cada registro nace `pendiente` y solo cuenta en resúmenes cuando la usuaria pulsa ✅. Los estados son pendiente, confirmado, descartado y anulado.
**Motivo:** la IA se equivoca (DAFO: debilidad). La ficha de producto promete que "el 100 % de los registros los confirma el usuario".
**Detalle:** el pendiente se guarda en la BD, no en memoria, para que sobreviva a un reinicio del bot.

## D3 · Deshacer no borra
**Decisión:** `/deshacer` marca el registro como `anulado`; no hace `DELETE`.
**Motivo:** con datos de salud, perder información por un toque accidental es peor que conservar un registro anulado. Además deja rastro de auditoría.

## D4 · Migraciones con `PRAGMA user_version`
**Decisión:** la BD lleva su número de versión y el programa aplica en orden las migraciones que falten, cada una en su transacción.
**Motivo:** conservar los registros reales de la v1 (renombrando `insulina` a `insulina_rapida` y añadiendo columnas) en vez de crear una BD nueva. Lo que se guardó en la v1 se da por `confirmado`.

## D5 · Interfaz `Extractor` delante de Gemini
**Decisión:** la lógica solo conoce el protocolo `Extractor.extraer(Entrada) -> DatosExtraidos`; `GeminiExtractor` es una implementación.
**Motivo:** CAME, "corregir debilidades": no depender de un proveedor de IA. También permite tests con un extractor falso, sin red ni coste.

## D6 · Salida estructurada con esquema Pydantic
**Decisión:** se pasa `response_schema=DatosExtraidos` a Gemini en lugar de pedirle "solo JSON" y hacer `json.loads`.
**Motivo:** el modelo queda obligado a devolver ese formato y los tipos se validan. Si aun así falla, se lanza `ErrorExtraccion` y la usuaria recibe un aviso, no un cuelgue.

## D7 · Prompt sin consejo médico
**Decisión:** el prompt dice "asistente de REGISTRO" y prohíbe recomendar dosis o tratamientos. Antes decía "asistente médico".
**Motivo:** la línea roja del MDR (regla 11). Si el software sugiere dosis, pasa a ser producto sanitario de clase IIa.

## D8 · Rangos de plausibilidad, no clínicos
**Decisión:** si un valor está fuera de lo físicamente plausible (por ejemplo, glucosa fuera de 20-600), el resumen muestra "❗ Revisa", pero no se bloquea.
**Motivo:** detectar lecturas erróneas de la IA sin emitir juicios clínicos.

## D9 · Resúmenes descriptivos
**Decisión:** `/hoy` y `/semana` muestran totales, la media, el tiempo en rango 70-180 y el número de hipoglucemias. Sin interpretaciones ni recomendaciones.
**Motivo:** el MDR, otra vez. Para la media y el tiempo en rango solo se usa la glucosa principal de cada registro, porque la gráfica de una captura repite ese valor y se contaría dos veces. Es aproximado: son lecturas sueltas, no el sensor continuo.

## D10 · Hora de España explícita
**Decisión:** la hora del mensaje viene de Telegram (UTC) y se convierte a `Europe/Madrid` con `zoneinfo`. En la BD se guarda la hora local sin zona, con el mismo formato que en la v1.
**Motivo:** en la v1 se usaba la hora del PC e ignoraba la del mensaje. Si el bot se despliega en un servidor en UTC, todas las horas saldrían desplazadas.

## D11 · Lista blanca obligatoria
**Decisión:** `ALLOWED_USER_IDS` en el `.env`. Si está vacío, el bot no arranca. Un guardián en el grupo -1 bloquea cualquier update de usuarios no permitidos.
**Motivo:** son datos de salud (RGPD, art. 9). En la v1, cualquiera que encontrase el bot podía escribirle y sus mensajes se enviaban a Gemini y se guardaban.

## D12 · La BD real no se sube a GitHub
**Decisión:** la copia de seguridad de la BD está en `backups/`, que está en `.gitignore`. No se versiona.
**Motivo:** el repositorio es público y la BD contiene datos de salud reales de una tercera persona. Subirla contradiría la privacidad por diseño de la memoria y el RGPD, y el historial de Git la conservaría aunque luego se borrase.

## D13 · Logs sin datos de salud ni token
**Decisión:** los logs solo registran IDs y tipos de error. `httpx` se sube a WARNING.
**Motivo:** `httpx` registra en INFO cada URL de la API de Telegram, y esa URL incluye el token del bot.
