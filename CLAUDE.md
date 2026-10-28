# Diabetes-Tracker-App ("Federico", bot de Telegram)

Bot personal que registra datos de diabetes (glucemia, comidas, insulina) a partir de texto, audios y capturas, usando Gemini para extraer los datos.

## Archivos
- `bot.py` — punto de entrada; handlers de python-telegram-bot.
- `analyzer.py` — llamadas a Gemini (SDK `google-genai`) y extracción de variables.
- `database.py` — SQLite (`diabetes_tracker.db`, creado en local).

## Ejecutar
- Variables en `.env`: `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY` (cargadas con python-dotenv).
- `pip install python-telegram-bot google-genai python-dotenv` y `python bot.py`.
- No hay `requirements.txt`; si añades dependencias, créalo.

## Privacidad (importante)
- Son datos de salud reales de otra persona: nunca leas, muestres ni subas `diabetes_tracker.db` ni `.env`.
- Para probar, usa datos inventados.
- Antes de cambiar el modelo de Gemini o el SDK, consulta la documentación actual (Context7).
