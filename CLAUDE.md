# Diabetes-Tracker-App ("Federico", bot de Telegram)

Bot personal que registra datos de diabetes (glucemia, comidas, insulina) a partir de texto, audios y capturas, usando Gemini para extraer los datos. Es el prototipo del proyecto emprendedor de IPE II.

## Arquitectura (v2)
Capas: `modelos.py` → `datos/repositorio.py` (único sitio con SQL) → `ia/` (interfaz `Extractor` + `gemini.py`) → `servicios.py` (lógica, sin Telegram) → `telegram_bot.py` (canal) → `bot.py` (punto de entrada). El porqué de cada decisión está en `docs/decisiones.md`; añade ahí las nuevas.

## Fases
- Las fases y su estado están en `docs/hoja-de-ruta.md`.
- Cada fase se arranca con la skill `preparar-fase` y se cierra con `plan-pruebas-fase` (en `.claude/skills/`).

## Ejecutar y probar
- Entorno: `.venv` con `pip install -r requirements.txt`.
- `.env`: `TELEGRAM_BOT_TOKEN`, `GEMINI_API_KEY` y `ALLOWED_USER_IDS` (obligatorias); `GEMINI_MODEL` y `DB_PATH` (opcionales). Plantilla en `.env.example`.
- Tests: `.venv/Scripts/python -m pytest`. No llaman a la API; usan un `ExtractorFalso`.
- Los cambios de esquema van como una migración NUEVA al final de `MIGRACIONES`. Nunca se edita una ya aplicada.

## Límites del producto
- No es un producto sanitario (MDR): nada de recomendar dosis, tratamientos ni alertas terapéuticas. Los resúmenes son solo descriptivos.

## Commits
- Un commit por cada cambio pequeño, en español: `tipo(ámbito): descripción` (ámbitos: config, modelo, bd, ia, servicios, bot, seguridad, skills).
- Sin `Co-Authored-By` ni líneas extra.
- Solo hacer commit si `pytest` pasa.

## Privacidad (importante)
- Son datos de salud reales de otra persona: nunca leas, muestres ni subas `diabetes_tracker.db`, `backups/` ni `.env`. El repositorio es público.
- Para probar, usa datos inventados (`DB_PATH` a otra BD).
- Antes de cambiar el modelo de Gemini o el SDK, consulta la documentación actual (Context7).
