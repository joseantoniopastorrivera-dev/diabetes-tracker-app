# Plan de pruebas de Federico v2 (fase 1)

| | |
|---|---|
| **Proyecto** | Diabetes Tracker App · bot "Federico" |
| **Versión que se prueba** | rama `v2-fase1` |
| **Usuaria de prueba** | Marta (paciente cero, diabetes tipo 1) |
| **Responsable** | José Antonio Pastor Rivera |
| **Fecha** | ____ / ____ / 2026 |
| **Lugar** | ______________________________ |
| **Hora de inicio / fin** | ________ / ________ |

---

## 1. Objetivo

Comprobar con la usuaria real que la versión 2 cumple lo que promete la memoria del proyecto:

- Ningún dato se guarda sin que Marta lo confirme.
- Se guardan todos los datos que entiende la IA (antes se perdían la basal, los hidratos, las hipos, los síntomas y las notas).
- Los resúmenes `/hoy` y `/semana` cuadran con lo registrado.
- Los datos antiguos de la v1 siguen ahí después de la migración.
- Registrar algo lleva **menos de 15 segundos** y la IA responde en **menos de 5 segundos** (ficha de producto, apartado 5.1).

---

## 2. ¿Dónde tiene que estar encendido el bot?

Federico funciona por *polling*: el programa `bot.py` pregunta continuamente a Telegram si hay mensajes nuevos. Por eso:

- **El móvil de Marta puede estar en cualquier sitio.** Le escribe al bot por Telegram como siempre.
- **El ordenador que ejecuta `bot.py` tiene que estar encendido y con internet** mientras dure la prueba. Si se apaga o se cierra la terminal, el bot deja de contestar (los mensajes no se pierden: Telegram los guarda unas 24 horas y llegan al volver a arrancarlo).
- **La base de datos vive en ese ordenador.** Los registros se guardan donde se ejecuta el bot.
- **Solo puede haber UN bot arrancado a la vez.** Si se arranca en dos ordenadores con el mismo token, Telegram da el error `Conflict: terminated by other getUpdates request`.

| Opción | Cómo | Ventajas | Inconvenientes |
|---|---|---|---|
| **A. Portátil propio en la oficina (recomendada)** | Llevar el portátil con el proyecto, el `.env` y la BD | Los datos de salud no salen de un equipo tuyo; puedes ver el log en directo | Hay que llevar la BD real al portátil si no está ya en él |
| B. PC de casa encendido | Dejar `bot.py` corriendo en casa | No hay que mover nada | No ves el log durante la prueba; si se cuelga, no puedes reiniciarlo |
| C. PC de la oficina | Instalar Python y el proyecto allí | No hay que cargar con el portátil | Datos de salud y claves en un equipo compartido: **desaconsejado** |

> Si hay que mover la BD real entre ordenadores, hazlo con un USB o por cable, **nunca por GitHub, correo ni la nube**. Al terminar, la BD buena es la del ordenador donde se ha usado el bot.

---

## 3. Preparación (antes de ver a Marta)

| ✔ | Tarea | Cómo se comprueba |
|---|---|---|
| ☐ | Estar en la rama correcta | `git switch v2-fase1` |
| ☐ | Dependencias instaladas | `.venv/Scripts/python -m pip install -r requirements.txt` |
| ☐ | Tests en verde | `.venv/Scripts/python -m pytest` → `24 passed` |
| ☐ | Copia de seguridad de la BD real | Existe `backups/diabetes_tracker_v1_2026-11-05.db` |
| ☐ | `ALLOWED_USER_IDS` en el `.env` con tu ID | Si no sabes el de Marta, se obtiene en la prueba P02 |
| ☐ | La red deja hablar con Telegram | Abrir `https://api.telegram.org` en el navegador: debe cargar (sale una página de Telegram) |
| ☐ | Portátil enchufado y suspensión desactivada | Si el portátil se suspende, el bot se para |
| ☐ | Llevar este plan impreso y un bolígrafo | |

---

## 4. Ronda 1: pruebas funcionales en una BD de pruebas

Primero se prueba en una **BD aparte**, para que los datos absurdos (glucosa 900, registros descartados...) no ensucien el historial real.

En el `.env`, de forma temporal: `DB_PATH=pruebas_marta.db`. Después, arrancar con `.venv/Scripts/python bot.py` y comprobar que el log dice `Base de datos en versión 2`.

Marta hace las acciones desde su móvil. Tú anotas el resultado. **Cronometra** las pruebas marcadas con ⏱ (desde que Marta empieza a escribir o hablar hasta que pulsa ✅).

### 4.1. Acceso y bienvenida

| ID | Acción de Marta | Resultado esperado | OK / Fallo | Notas |
|---|---|---|---|---|
| P01 | Escribe `/start` | Bienvenida con el aviso de IA, el aviso médico y el de privacidad | ☐ / ☐ | |
| P02 | (Si su ID aún no está en el `.env`) escribe "hola" | Responde "🔒 Este bot es privado" y en el log sale `Acceso denegado al usuario id=…`. Apunta ese ID, añádelo a `ALLOWED_USER_IDS` y reinicia el bot | ☐ / ☐ | ID: __________ |
| P03 | Escribe `/ayuda` | Lista de comandos | ☐ / ☐ | |

### 4.2. Registro y confirmación

| ID | Acción de Marta | Resultado esperado | OK / Fallo | Notas |
|---|---|---|---|---|
| P04 ⏱ | Escribe: `120 y me he puesto 4 de rápida` | Resumen con glucosa 120 y rápida 4, botones ✅ ✏️ ❌. Pulsa ✅ → "✅ Guardado" y desaparecen los botones | ☐ / ☐ | ____ s |
| P05 ⏱ | Nota de voz: "he comido lentejas con pan, unos 50 de hidratos" | Comida con la hora y hidratos 50 | ☐ / ☐ | ____ s |
| P06 ⏱ | Manda una **captura del sensor** | Glucosa = el número grande de la pantalla; aparece "📈 Gráfica" con varios puntos | ☐ / ☐ | ____ s |
| P07 | Escribe: `me he puesto 10 de lenta` | Basal 10 (no rápida) | ☐ / ☐ | |
| P08 | Escribe: `hace media hora me dio una bajada y estaba temblando` | Hipoglucemia con una hora = hora actual menos 30 min; síntomas "temblores" | ☐ / ☐ | Hora OK: ☐ |
| P09 | Escribe: `hola qué tal` | "No he encontrado datos que apuntar..." y no aparecen botones | ☐ / ☐ | |
| P10 | Escribe: `tengo 900 de glucosa` | Sale "❗ Revisa: glucosa = 900 parece fuera de lo normal". Pulsa ❌ → "Descartado" | ☐ / ☐ | |

### 4.3. Corrección, cancelación y doble clic

| ID | Acción de Marta | Resultado esperado | OK / Fallo | Notas |
|---|---|---|---|---|
| P11 | Escribe `150 y 5 de rápida`, pulsa ✏️ y escribe `eran 3 de rápida` | Nuevo resumen con glucosa 150 (se conserva) y rápida 3. Pulsa ✅ | ☐ / ☐ | |
| P12 | Escribe `130`, pulsa ✏️ y corrige **por voz**: "no, eran 140" | Resumen con glucosa 140 | ☐ / ☐ | |
| P13 | Escribe `100`, pulsa ✏️ y luego `/cancelar` | "Vale, dejo el registro como estaba". El registro sigue pendiente | ☐ / ☐ | |
| P14 | En un registro ya guardado, pulsa ✅ otra vez muy rápido (doble toque) | Aviso emergente "Ese registro ya está confirmado"; no se duplica | ☐ / ☐ | |
| P15 | Escribe `110`, **sin pulsar nada** reinicia el bot (Ctrl+C y arrancar otra vez), y después pulsa ✅ | Se guarda bien: el pendiente sobrevive al reinicio | ☐ / ☐ | |

### 4.4. Consultas y deshacer

| ID | Acción de Marta | Resultado esperado | OK / Fallo | Notas |
|---|---|---|---|---|
| P16 | Escribe `/hoy` | Una línea por cada registro **confirmado** de hoy. No salen ni el descartado (P10) ni el pendiente (P13). Los totales cuadran con lo que habéis registrado | ☐ / ☐ | Rápida total: ____ |
| P17 | Escribe `/semana` | Resumen con la media, el % en rango y las hipos. Aviso final de "no sustituye al equipo médico" | ☐ / ☐ | |
| P18 | Escribe `/deshacer` | "↩️ He anulado este registro" con el último guardado. `/hoy` ya no lo muestra | ☐ / ☐ | |

---

## 5. Ronda 2: paso a la BD real

1. Para el bot (Ctrl+C).
2. En el `.env`, borra la línea `DB_PATH=pruebas_marta.db`, o pon `DB_PATH=diabetes_tracker.db`.
3. Comprueba que existe la copia en `backups/`.
4. Arranca el bot.

| ID | Comprobación | Resultado esperado | OK / Fallo | Notas |
|---|---|---|---|---|
| P19 | Log al arrancar | `Base de datos en versión 2`, sin errores | ☐ / ☐ | |
| P20 | Marta escribe `/semana` | Aparecen los registros de la v1 de los últimos 7 días (si los hay) | ☐ / ☐ | |
| P21 | Un registro real de Marta, con ✅ | Se guarda y aparece en `/hoy` | ☐ / ☐ | |

> Si P19 falla: para el bot, copia `backups/diabetes_tracker_v1_2026-11-05.db` encima de `diabetes_tracker.db` y avísame con el mensaje de error (sin datos de Marta).

---

## 6. Si algo falla

| Síntoma | Causa probable | Qué hacer |
|---|---|---|
| El bot no arranca: "Faltan variables en .env" o "ALLOWED_USER_IDS está vacío" | El `.env` está incompleto | Revisa las tres variables obligatorias (`.env.example`) |
| "⚠️ No he podido analizarlo" en todos los mensajes | La clave de Gemini, el nombre del modelo o la cuota | Mira en el log la línea `Error llamando a Gemini: <tipo>`. Prueba a cambiar `GEMINI_MODEL` |
| `Conflict: terminated by other getUpdates request` | El bot está arrancado en otro ordenador | Ciérralo allí |
| El bot no contesta nada | El portátil está suspendido o la red de la oficina bloquea Telegram | Revisa la terminal; prueba con los datos del móvil compartidos |
| Horas desplazadas 1 o 2 horas | Fallo en la zona horaria | Anótalo con un ejemplo (hora real y hora mostrada) |

---

## 7. Preguntas a Marta (5 minutos al final)

Valora del 1 (nada) al 5 (mucho):

| Pregunta | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|
| ¿Es más cómodo que la versión anterior? | ☐ | ☐ | ☐ | ☐ | ☐ |
| ¿Confirmar con ✅ te resulta pesado? | ☐ | ☐ | ☐ | ☐ | ☐ |
| ¿Corregir hablando es fácil? | ☐ | ☐ | ☐ | ☐ | ☐ |
| ¿Entiendes los resúmenes `/hoy` y `/semana`? | ☐ | ☐ | ☐ | ☐ | ☐ |
| ¿Lo usarías todos los días? | ☐ | ☐ | ☐ | ☐ | ☐ |

¿Qué echas en falta? ______________________________________________________________

¿Qué te sobra o te molesta? __________________________________________________________

¿Qué le enseñarías a tu endocrino? ____________________________________________________

---

## 8. Resultado

| Métrica | Objetivo | Medido |
|---|---|---|
| Pruebas superadas | 21 / 21 | ____ / 21 |
| Tiempo medio por registro (P04 a P06) | < 15 s | ____ s |
| Respuesta de la IA (desde que envía hasta que aparece el resumen) | < 5 s | ____ s |
| Correcciones necesarias en P04 a P08 | 0 | ____ |

**Decisión:** ☐ Fusionar `v2-fase1` en `main` ☐ Corregir fallos y repetir

### Incidencias

| Nº | Prueba | Qué pasó | Gravedad (alta / media / baja) |
|---|---|---|---|
| 1 | | | |
| 2 | | | |
| 3 | | | |
| 4 | | | |
