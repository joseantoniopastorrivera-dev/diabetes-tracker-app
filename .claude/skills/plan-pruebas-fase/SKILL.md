---
name: plan-pruebas-fase
description: Genera el plan de pruebas imprimible (Markdown y PDF) de una fase de Federico para probarla con Marta. Úsala cuando el usuario pida "plan de pruebas de la fase N", "PDF de pruebas" o al terminar una fase.
---

# Plan de pruebas de una fase de Federico

Resultado: `docs/plan-pruebas-faseN.md` y `docs/plan-pruebas-faseN.pdf`, con un commit cada uno.

## 1. Reunir qué se prueba

- `docs/hoja-de-ruta.md`: los puntos de la fase N (eso es el objetivo, apartado 1).
- `git log --oneline main..v2-faseN`: cada commit `feat` tiene al menos un caso de prueba; los `fix`, un caso que demuestre que no vuelve a pasar.
- `.venv/Scripts/python -m pytest`: el número de tests para la preparación.
- `PRAGMA user_version` esperado = `len(MIGRACIONES)` en `datos/repositorio.py`. Léelo del código, nunca de la BD real.

## 2. Escribir el Markdown

Copia `plantilla.md` (en esta carpeta) y rellena cada `{…}`. Borra las líneas de instrucciones entre llaves.

Reglas de los casos:
- **Acción literal**: el texto exacto que escribe o dice Marta, entre comillas o `código`. Nunca "probar el registro".
- **Resultado observable**: qué se ve en Telegram o en el log, con los números concretos.
- Cubrir por cada función nueva: el caso normal, una entrada sin datos o absurda, el error del usuario (doble toque, cancelar) y la persistencia tras un reinicio del bot.
- Los datos absurdos o de prueba, solo en la ronda 1 (BD de pruebas). En la ronda 2, solo comprobaciones que no ensucien el historial real.
- Ningún caso puede pedir a la app dosis ni consejo médico, ni esperar que los dé.
- Numeración P01, P02… continua hasta el final; el total va en el apartado 8.

## 3. Generar el PDF y revisarlo

```bash
P="$HOME/.claude/skills/gstack/make-pdf/dist/pdf"
"$P" generate --page-size a4 --margins 0.75in --no-confidential --no-chapter-breaks \
  --author "José Antonio Pastor Rivera" docs/plan-pruebas-faseN.md docs/plan-pruebas-faseN.pdf
```

Para revisarlo **no abras el PDF en el navegador integrado** (lanza un diálogo de descarga). Genera la misma vista con `--to html` en el scratchpad, sírvela con `python -m http.server` en 127.0.0.1 y haz capturas: cabecera, una tabla de casos y el final. Corrige el `.md` y regenera hasta que se vea bien.

## 4. Cerrar

- Commit del `.md` y luego del `.pdf`, en el formato de `CLAUDE.md`.
- Entrega el PDF al usuario y recuérdale la preparación del apartado 3.
