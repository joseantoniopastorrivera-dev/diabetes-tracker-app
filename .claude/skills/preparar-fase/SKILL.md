---
name: preparar-fase
description: Arranca una fase de la hoja de ruta de Federico (fase 0 de preparación más el plan por pasos). Úsala cuando el usuario diga "preparar la fase N", "empezar la fase N" o "siguiente fase".
---

# Preparar una fase de Federico

Hay dos etapas y una parada obligatoria entre ellas: no se escribe código de la fase hasta que el usuario apruebe el plan.

## 1. Fase 0: preparación (sin pedir permiso)

1. Lee `docs/hoja-de-ruta.md` (qué entra en la fase N) y `docs/decisiones.md` (qué ya está decidido).
2. Comprueba que la fase anterior está fusionada en `main`. Si no lo está, para y díselo.
3. `git switch main` y después `git switch -c v2-faseN`.
4. Copia de seguridad de la BD real **sin abrirla**: `cp diabetes_tracker.db backups/diabetes_tracker_<AAAA-MM-DD>.db`. Si no existe la BD, sigue y avísalo.
5. Entorno: `.venv/Scripts/python -m pip install -r requirements.txt`. Las dependencias nuevas se fijan en `requirements.txt`.
6. Línea base: `.venv/Scripts/python -m pytest` tiene que pasar antes de tocar nada. Apunta el número de tests.
7. En `docs/hoja-de-ruta.md`, marca la fase como 🟡 y haz commit.

## 2. Plan por pasos (y parar)

Presenta al usuario, sin escribir código:
- Los pasos en orden, cada uno con los ficheros que toca y su test.
- Qué capa cambia en cada paso (modelos → datos → ia → servicios → telegram_bot). La lógica nunca va en `telegram_bot.py`.
- Cualquier cambio de esquema, como migración **nueva** al final de `MIGRACIONES`.
- **Comprobación del MDR** de cada función: si calcula dosis, recomienda tratamiento o alerta para decidir terapia, sácala de la fase y explica por qué.
- Las decisiones que tiene que tomar el usuario, con tu recomendación.

Para y espera su aprobación o sus correcciones.

## 3. Durante la fase

- Un commit por cambio pequeño, en el formato de `CLAUDE.md`, y solo si pytest devuelve 0. Comprueba el código de salida: un `| tail` lo oculta.
- Cada decisión con alternativas va a `docs/decisiones.md` (Dn, con su motivo).
- Al terminar: marca los puntos con ✅ en la hoja de ruta y ofrece la skill `plan-pruebas-fase`.
