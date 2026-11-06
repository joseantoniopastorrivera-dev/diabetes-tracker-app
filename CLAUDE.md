# Diabetes-Tracker-App ("Federico", bot de Telegram)

## Cómo trabajar conmigo
Reglas comunes a todos mis repos (copia de mi `C:\dev\CLAUDE.md`, para que también las lean las sesiones en la nube). Soy estudiante de DAM en el IES Isidra de Guzmán.
- En prácticas evaluables, resuélvelas completas (sin modo de pistas). Al terminar, crea junto a la entrega (en `docs/` si existe) un `guia-defensa-<practica>.md` para defenderla en clase, al estilo de la guía de DataStock. No se añade a Git salvo que lo pida.
- Estructura de la guía de defensa: cómo usarla; cómo arrancar, ejecutar y ensayar sin estropear la entrega; qué pide el enunciado y dónde se cumple cada requisito; visión general (capas, flujo, decisiones de diseño a justificar); y por cada requisito: qué pide, dónde está, explicación línea a línea, cómo demostrarlo, errores típicos, preguntas de la profesora con su respuesta y 🔧 modificaciones en directo (el cambio que podrían pedir, con el código exacto y dónde va). Al final: casos prácticos «¿qué pasaría si…?», «corrige este error» (síntoma → causa → arreglo) y chuleta con plan de ensayo.
- Si la tarea es grande, antes de tocar nada dime cómo lo harías (plan por pasos) y espera a que lo apruebe o lo corrija.
- Cuando escribas código, explícalo línea por línea y di por qué elegiste esa forma y no otra.
- Si ves un error de concepto o algo que no entiendo bien, dímelo aunque no te lo pregunte.
- Responde en español.
- No hagas commit ni push sin que te lo pida. Commits sin `Co-Authored-By` ni líneas de atribución.
- No subas binarios generados (`target/`, `*.class`, `__pycache__/`, `*.pyc`, `bin/`, `obj/`, `Library/` de Unity).
- Nunca leas, muestres ni subas ficheros `.env`, tokens ni credenciales.
- PDFs, .docx, .odt y .pptx son apuntes o enunciados: léelos solo si hacen falta para la tarea.

Bot personal que registra datos de diabetes (glucemia, comidas, insulina) a partir de texto, audios y capturas, usando Gemini para extraer los datos. Es el prototipo del proyecto emprendedor de IPE II.

## Arquitectura (v2)
Capas: `modelos.py` → `datos/repositorio.py` (único sitio con SQL) → `ia/` (interfaz `Extractor` + `gemini.py`) → `servicios.py` (lógica, sin Telegram) → `telegram_bot.py` (canal) → `bot.py` (punto de entrada). El porqué de cada decisión está en `docs/decisiones.md`; añade ahí las nuevas.

## Fases
- Las fases y su estado están en `docs/hoja-de-ruta.md`.
- Cada fase se arranca con la skill `preparar-fase` y se cierra con `plan-pruebas-fase`. Vienen del plugin `desarrollo-por-fases` del repo [claude-code-skills](https://github.com/joseantoniopastorrivera-dev/claude-code-skills), activado en `.claude/settings.json`.

## Skills de fases
Datos que usan `preparar-fase` y `plan-pruebas-fase` en este proyecto:
- Hoja de ruta: `docs/hoja-de-ruta.md`. Decisiones: `docs/decisiones.md`.
- Rama de cada fase: `v2-faseN`.
- Copia de seguridad antes de empezar, **sin abrir la BD**: `cp diabetes_tracker.db backups/diabetes_tracker_<AAAA-MM-DD>.db`.
- Dependencias: `.venv/Scripts/python -m pip install -r requirements.txt`. Tests: `.venv/Scripts/python -m pytest`.
- Capas, en este orden: modelos → datos → ia → servicios → telegram_bot. La lógica nunca va en `telegram_bot.py`.
- Versión de esquema esperada: `len(MIGRACIONES)` en `datos/repositorio.py` (`PRAGMA user_version`). Se lee del código, nunca de la BD real.
- Comprobación extra del plan: **MDR**. Si una función calcula dosis, recomienda tratamiento o alerta para decidir terapia, sale de la fase (ver "Límites del producto").
- Plantilla del plan de pruebas: `docs/plantilla-plan-pruebas.md`.
- Persona que prueba: Marta, paciente cero (diabetes tipo 1), por Telegram. Ronda 1 con `DB_PATH=pruebas_marta.db` y ronda 2 con la BD real.
- Ningún caso de prueba puede pedir a la app dosis ni consejo médico, ni esperar que los dé.
- Autor del PDF: José Antonio Pastor Rivera.

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
