# Plan de pruebas de Federico v2 (fase {N})

| | |
|---|---|
| **Proyecto** | Diabetes Tracker App · bot "Federico" |
| **Versión que se prueba** | rama `v2-fase{N}` |
| **Usuaria de prueba** | Marta (paciente cero, diabetes tipo 1) |
| **Responsable** | José Antonio Pastor Rivera |
| **Fecha** | ____ / ____ / {AÑO} |
| **Lugar** | ______________________________ |
| **Hora de inicio / fin** | ________ / ________ |

---

## 1. Objetivo

{Qué promete esta fase según docs/hoja-de-ruta.md, en 3-6 viñetas verificables.}

---

## 2. ¿Dónde tiene que estar encendido el bot?

El ordenador que ejecuta `bot.py` tiene que estar **encendido y con internet** durante la prueba. El móvil de Marta puede estar en cualquier sitio. La base de datos vive en ese ordenador, y **solo puede haber un bot arrancado a la vez** (si no, Telegram da el error `Conflict`).

| Opción | Ventajas | Inconvenientes |
|---|---|---|
| **A. Portátil propio (recomendada)** | Los datos no salen de un equipo tuyo; ves el log en directo | Hay que llevar la BD real si no está en él |
| B. PC de casa encendido | No hay que mover nada | No ves el log ni puedes reiniciar el bot |
| C. PC compartido de la oficina | No hay que cargar con nada | Datos de salud y claves en un equipo compartido: **desaconsejado** |

> La BD real solo se mueve por USB o cable, **nunca por GitHub, correo ni la nube**.

---

## 3. Preparación (antes de ver a Marta)

| ✔ | Tarea | Cómo se comprueba |
|---|---|---|
| ☐ | Estar en la rama correcta | `git switch v2-fase{N}` |
| ☐ | Dependencias instaladas | `.venv/Scripts/python -m pip install -r requirements.txt` |
| ☐ | Tests en verde | `.venv/Scripts/python -m pytest` → `{TESTS} passed` |
| ☐ | Copia de seguridad de la BD real | Existe `backups/diabetes_tracker_<fecha>.db` |
| ☐ | `.env` completo | {Variables obligatorias de esta fase} |
| ☐ | La red deja hablar con Telegram | `https://api.telegram.org` carga en el navegador |
| ☐ | Portátil enchufado y sin suspensión | |
| ☐ | Plan impreso y bolígrafo | |
{Filas extra de preparación propias de la fase.}

---

## 4. Ronda 1: pruebas funcionales en una BD de pruebas

En el `.env`, de forma temporal: `DB_PATH=pruebas_marta.db`. Arrancar y comprobar en el log `Base de datos en versión {VERSIÓN_BD}`. Marta hace las acciones y tú anotas el resultado. Cronometra las marcadas con ⏱.

{Una subsección ### 4.x por cada grupo de funciones. Tabla:}

| ID | Acción de Marta | Resultado esperado | OK / Fallo | Notas |
|---|---|---|---|---|
| P01 | {Acción concreta, con el texto literal entre `comillas`} | {Qué debe verse exactamente} | ☐ / ☐ | |

---

## 5. Ronda 2: paso a la BD real

1. Para el bot (Ctrl+C).
2. En el `.env`, quita `DB_PATH=pruebas_marta.db`.
3. Comprueba que existe la copia en `backups/`.
4. Arranca el bot.

| ID | Comprobación | Resultado esperado | OK / Fallo | Notas |
|---|---|---|---|---|
| P{n} | Log al arrancar | `Base de datos en versión {VERSIÓN_BD}`, sin errores | ☐ / ☐ | |
| P{n+1} | `/semana` | Siguen apareciendo los registros anteriores | ☐ / ☐ | |
{Una o dos comprobaciones de las funciones nuevas sobre los datos reales.}

> Si falla el arranque: para el bot, restaura la copia de `backups/` y apunta el error (sin datos de Marta).

---

## 6. Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| No arranca: "Faltan variables en .env" | El `.env` está incompleto | Revisa `.env.example` |
| "⚠️ No he podido analizarlo" siempre | La clave, el modelo o la cuota de Gemini | Mira `Error llamando a Gemini: <tipo>` en el log |
| `Conflict: terminated by other getUpdates request` | Hay otro bot arrancado | Ciérralo |
| No contesta nada | Suspensión o red que bloquea Telegram | Revisa la terminal; prueba con los datos del móvil |
{Síntomas propios de las funciones nuevas.}

---

## 7. Preguntas a Marta (5 minutos al final)

Valora del 1 (nada) al 5 (mucho):

| Pregunta | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
{3-5 preguntas sobre las funciones nuevas de la fase, más: "¿Lo usarías todos los días?"}

¿Qué echas en falta? ______________________________________________________________

¿Qué te sobra o te molesta? __________________________________________________________

---

## 8. Resultado

| Métrica | Objetivo | Medido |
|---|---|---|
| Pruebas superadas | {TOTAL} / {TOTAL} | ____ / {TOTAL} |
| Tiempo medio por registro | < 15 s | ____ s |
| Respuesta de la IA | < 5 s | ____ s |
{Métricas propias de la fase.}

**Decisión:** ☐ Fusionar `v2-fase{N}` en `main` ☐ Corregir fallos y repetir

### Incidencias

| Nº | Prueba | Qué pasó | Gravedad (alta / media / baja) |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
