# Diabetes-Tracker-App ("Federico", bot de Telegram)

## Cómo trabajar conmigo
Reglas comunes a todos mis repos (copia de mi `C:\dev\CLAUDE.md`, para que también las lean las sesiones en la nube). Soy estudiante de DAM en el IES Isidra de Guzmán.
- En prácticas evaluables, resuélvelas completas (sin modo de pistas). Al terminar, crea junto a la entrega (en `docs/` si existe) un `guia-defensa-<practica>.md` para defenderla en clase, al estilo de la guía de DataStock. Las guías de defensa no se suben nunca a GitHub: cada repo tiene `guia-defensa-*.md` en su `.gitignore` (añádelo si falta).
- Estructura de la guía de defensa: cómo usarla; cómo arrancar, ejecutar y ensayar sin estropear la entrega; qué pide el enunciado y dónde se cumple cada requisito; visión general (capas, flujo, decisiones de diseño a justificar); y por cada requisito: qué pide, dónde está, explicación línea a línea, cómo demostrarlo, errores típicos, preguntas de la profesora con su respuesta y 🔧 modificaciones en directo (el cambio que podrían pedir, con el código exacto y dónde va). Al final: casos prácticos «¿qué pasaría si…?», «corrige este error» (síntoma → causa → arreglo) y chuleta con plan de ensayo.
- Si la tarea es grande, antes de tocar nada dime cómo lo harías (plan por pasos) y espera a que lo apruebe o lo corrija.
- Cuando escribas código, explícalo línea por línea y di por qué elegiste esa forma y no otra.
- Si ves un error de concepto o algo que no entiendo bien, dímelo aunque no te lo pregunte.
- Responde en español.
- No hagas commit ni push sin que te lo pida. Commits con `Co-Authored-By: Claude <noreply@anthropic.com>` (repo personal); en los repos de asignaturas del grado, nunca.
- **Pull requests en todos los repos (asignaturas y personales):** nunca se commitea directo en `main`. Una rama por cambio (nombre con guiones, sin barra: con barra GitHub dio error 500), sus commits pequeños, `gh pr create --fill --base main`, tests en local y CI en verde (`gh pr checks <n> --watch`), y `gh pr merge <n> --merge --delete-branch` (nunca squash, para que cada commit quede en el historial). Si el repo no tiene tests o CI para lo que cambia, dilo y propón añadirlos. Si la carpeta la comparten otras sesiones, trabaja en un worktree propio y no cambies de rama allí. Sigue valiendo que el commit, push y merge solo se hacen cuando yo lo pida.
- No subas binarios generados (`target/`, `*.class`, `__pycache__/`, `*.pyc`, `bin/`, `obj/`, `Library/` de Unity).
- Nunca leas, muestres ni subas ficheros `.env`, tokens ni credenciales.
- PDFs, .docx, .odt y .pptx son apuntes o enunciados: léelos solo si hacen falta para la tarea.

Bot personal que registra datos de diabetes (glucemia, comidas, insulina) a partir de texto, audios y capturas, usando Gemini para extraer los datos. Es el prototipo del proyecto emprendedor de IPE II.

## Arquitectura (v2)
Capas: `modelos.py` → `datos/repositorio.py` (único sitio con SQL) → `ia/` (interfaz `Extractor` + `gemini.py`) → `servicios.py` (lógica, sin Telegram) → `telegram_bot.py` (canal) → `bot.py` (punto de entrada). El porqué de cada decisión está en `docs/decisiones.md`; añade ahí las nuevas.

## Fases
- Las fases y su estado están en `docs/hoja-de-ruta.md`.
- Cada fase se arranca con la skill `prepare-phase` y se cierra con `phase-test-plan`. Vienen del plugin `phased-development` del repo privado `claude-code-skills-private` (antes `desarrollo-por-fases` del repo público), activado en `.claude/settings.json`.

## Skills de fases
Datos que usan `prepare-phase` y `phase-test-plan` en este proyecto (las skills leen esta sección con este título):
- Hoja de ruta: `docs/hoja-de-ruta.md`. Decisiones: `docs/decisiones.md`.
- Rama de cada fase: `v2-faseN`.
- Copia de seguridad antes de empezar, **sin abrir la BD**: `cp diabetes_tracker.db backups/diabetes_tracker_<AAAA-MM-DD>.db`.
- Dependencias: `.venv/Scripts/python -m pip install -r requirements.txt`. Tests: `.venv/Scripts/python -m pytest`.
- Capas, en este orden: modelos → datos → ia → servicios → telegram_bot. La lógica nunca va en `telegram_bot.py`.
- Versión de esquema esperada: `len(MIGRACIONES)` en `datos/repositorio.py` (`PRAGMA user_version`). Se lee del código, nunca de la BD real.
- Comprobación extra del plan: **MDR**. Si una función calcula dosis, recomienda tratamiento o alerta para decidir terapia, sale de la fase (ver "Límites del producto").
- Plantilla del plan de pruebas: `docs/plantilla-plan-pruebas.md`.
- Persona que prueba: la usuaria experta, paciente cero (diabetes tipo 1), por Telegram. Ronda 1 con `DB_PATH=pruebas_usuaria.db` y ronda 2 con la BD real.
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
- Con `Co-Authored-By: Claude <noreply@anthropic.com>` y sin otras líneas extra.
- Solo hacer commit si `pytest` pasa.

## Privacidad (importante)
- Son datos de salud reales de otra persona: nunca leas, muestres ni subas `diabetes_tracker.db`, `backups/` ni `.env`. El repositorio es público.
- Para probar, usa datos inventados (`DB_PATH` a otra BD).
- Antes de cambiar el modelo de Gemini o el SDK, consulta la documentación actual (Context7).

## Karpathy guidelines

Source: <https://github.com/multica-ai/andrej-karpathy-skills> (CLAUDE.md at commit 2c60614, MIT, by forrestchang), derived from <https://x.com/karpathy/status/2015883857489522876>. Text copied verbatim below; only the file's own "# CLAUDE.md" title line was dropped, and blank lines, link brackets and a code-fence language were added so it passes markdownlint.

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:

- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:

- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:

```text
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

### How the Karpathy guidelines fit my rules

My own rules (C:\dev\CLAUDE.md, each repo's CLAUDE.md, memory) win where they are more specific. Read them together like this:

1. **"No features beyond what was asked":** in graded practicals, everything in the assignment statement or required by my own rules (the defence guide, a screenshot of every step, the AI-use section) counts as asked, including optional and extra-credit items. Anything else is proposed first, never added silently.
2. **"Loop independently":** the verify-and-fix loop starts only after I approve the plan of a large task, and it never includes commit, push or merge unless I ask.
3. **"Write a test that reproduces it":** use the repo's tests when they exist. When they don't (reports, documents), state the concrete check instead (open the PDF, start Odoo, take a screenshot) and propose adding tests.
4. **"Match existing style" / "Minimum code":** the assignment statement's required structure wins. Line-by-line explanations go in the chat, not in the code, so they don't count against simplicity.
