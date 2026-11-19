# Guion rápido de la prueba con la usuaria experta

Acompaña al **plan de pruebas de la fase 1** (`plan-pruebas-fase1.pdf`, casos P01 a P21). El plan dice *qué* se comprueba; este guion dice *en qué orden*, *qué preparar antes* y *qué más mirar* para que la sesión dure unos 45 minutos.

Lleva impresos los dos. En el plan marcas OK o Fallo; aquí tienes los comandos y las frases.

---

## 1. Antes de quedar con la usuaria experta (15 minutos, tú solo)

Hazlo uno o dos días antes. Cada punto quita una parada durante la sesión.

| ✔ | Qué | Para qué |
|---|---|---|
| ☐ | **Conseguir ya el ID de Telegram de la usuaria experta.** Arranca el bot una tarde, pídele que le escriba "hola" y copia el número de la línea `Acceso denegado al usuario id=…` del log. Añádelo a `ALLOWED_USER_IDS` en el `.env`. | Te ahorra un reinicio del bot con ella delante. La prueba P02 queda hecha. |
| ☐ | **Ensayo general a solas** con la BD de pruebas: haz tú P01, P04, P06 y P09 desde tu móvil. | Si falla la clave de Gemini, la cuota o la red, lo descubres hoy y no con la usuaria experta esperando. |
| ☐ | **Mandar a la usuaria experta el mensaje de preparación** (apartado 2). | Llega con todo listo en el móvil. |
| ☐ | **Imprimir** el plan y este guion. Bolígrafo. | Apuntar a mano es más rápido que cambiar de ventana. |
| ☐ | **Cronómetro** en tu móvil, en la pantalla de inicio. | Tres pruebas van cronometradas. |
| ☐ | Portátil enchufado, **suspensión desactivada**, y datos del móvil listos para compartir por si la wifi bloquea Telegram. | Si el portátil se suspende, el bot se para. |

Comprobado el 16-11-2026: los 24 tests pasan, la v2 está en `main` y existe la copia `backups/diabetes_tracker_v1_2026-11-05.db`.

---

## 2. Mensaje para la usuaria experta

Cópialo y envíaselo tal cual:

> El finde probamos la versión nueva de Federico, unos 45 minutos. Para ir rápido, ten esto preparado en el móvil:
> 1. Telegram actualizado y el chat de Federico a mano.
> 2. Una **captura de pantalla del sensor** de hoy guardada en la galería.
> 3. Una **foto de un plato de comida** cualquiera.
> 4. Un sitio sin mucho ruido, porque hay que mandar un par de notas de voz.
>
> No tienes que estudiar nada: yo te digo qué escribir. Si algo te parece raro o incómodo, dímelo en el momento, que eso es justo lo que quiero saber.

---

## 3. Arranque el día de la prueba

En PowerShell, desde la carpeta del proyecto:

```
cd C:\dev\diabetes-tracker-app
git switch main
.venv\Scripts\python -m pytest
```

Tiene que decir `24 passed`. Después, **ronda 1** con la BD de pruebas:

```
$env:DB_PATH = "pruebas_usuaria.db"; .venv\Scripts\python bot.py
```

El log debe decir `Base de datos en versión 2`. No hace falta tocar el `.env`: la variable solo vive en esa terminal.

Para la **ronda 2** con la BD real: para el bot con Ctrl+C, **cierra esa terminal**, abre otra y arranca sin la variable:

```
cd C:\dev\diabetes-tracker-app
.venv\Scripts\python bot.py
```

---

## 4. Orden y tiempos

| Bloque | Casos del plan | Minutos | Truco para ir rápido |
|---|---|---|---|
| A. Acceso | P01, P03 (P02 ya hecha) | 3 | Que lea la bienvenida en voz alta: ves si se entiende. |
| B. Registrar | P04 a P10 | 12 | Díctale las frases del apartado 5. Cronometra P04, P05 y P06. |
| C. Corregir | P11 a P14 | 8 | No le expliques el botón ✏️: mira si lo encuentra sola. |
| D. Reinicio | P15 | 3 | Es la única prueba en la que tocas el portátil. Hazla aparte. |
| E. Consultas | P16 a P18 | 5 | Antes de `/hoy`, suma tú en el papel la rápida total. |
| F. Extra | E01 a E10 (apartado 6) | 5 | Solo si vais bien de tiempo. |
| G. BD real | P19 a P21 | 4 | Cambio de terminal (apartado 3). |
| H. Preguntas | Apartado 7 del plan | 5 | Deja que hable; apunta sus palabras literales. |

**Regla de oro: si algo falla, apunta y sigue.** No depures con la usuaria experta delante. Pídele una captura de pantalla del fallo y pasa al siguiente caso.

---

## 5. Frases para dictar a la usuaria experta

| Caso | Qué hace la usuaria |
|---|---|
| P01 | Escribe `/start` |
| P03 | Escribe `/ayuda` |
| P04 ⏱ | Escribe `120 y me he puesto 4 de rápida` y pulsa ✅ |
| P05 ⏱ | Nota de voz: «he comido lentejas con pan, unos 50 de hidratos» y pulsa ✅ |
| P06 ⏱ | Manda la captura del sensor y pulsa ✅ |
| P07 | Escribe `me he puesto 10 de lenta` y pulsa ✅ |
| P08 | Escribe `hace media hora me dio una bajada y estaba temblando` y pulsa ✅ |
| P09 | Escribe `hola qué tal` |
| P10 | Escribe `tengo 900 de glucosa` y pulsa ❌ |
| P11 | Escribe `150 y 5 de rápida`, pulsa ✏️, escribe `eran 3 de rápida` y pulsa ✅ |
| P12 | Escribe `130`, pulsa ✏️ y dice por voz «no, eran 140». Pulsa ✅ |
| P13 | Escribe `100`, pulsa ✏️ y escribe `/cancelar` |
| P14 | Busca un registro ya guardado y pulsa ✅ dos veces seguidas |
| P15 | Escribe `110` y **no pulsa nada**. Tú reinicias el bot. Entonces pulsa ✅ |
| P16 | Escribe `/hoy` |
| P17 | Escribe `/semana` |
| P18 | Escribe `/deshacer` y luego `/hoy` |

Rápida total que debe salir en `/hoy` si todo va bien: 4 (P04) + 3 (P11) = **7 unidades**. Basal: **10**.

---

## 6. Pruebas extra (exploratorias)

No tienen resultado fijo: sirven para descubrir cómo se comporta Federico con el lenguaje real de la usuaria experta. Apunta **qué ha entendido** y si es lo que ella quería decir. Siempre en la ronda 1 (BD de pruebas).

| ID | Qué hace la usuaria | Qué apuntar |
|---|---|---|
| E01 | Escribe `me he puesto 4,5 de rápida` | ¿Entiende el decimal con coma? Valor: ____ |
| E02 | Escribe `antes de comer tenía 110 y dos horas después 185` | ¿Qué hace con dos glucosas en un mensaje? |
| E03 | Escribe `anoche a las 11 tenía 180` | ¿Pone la fecha y la hora de ayer, o las de ahora? |
| E04 | Manda la **foto del plato de comida** | ¿Lo apunta como comida? ¿Se inventa hidratos? |
| E05 | Nota de voz hablando deprisa o con la tele de fondo | ¿Entiende bien los números? |
| E06 | Escribe `140` y, sin pulsar nada, escribe `me he puesto 2 de rápida` | ¿Salen dos pendientes? ¿Se lían los botones? |
| E07 | Escribe `/deshacer` dos veces seguidas | ¿Anula dos registros o avisa? |
| E08 | Manda solo un emoji o un sticker | ¿Responde algo comprensible? |
| E09 | Un mensaje largo con todo: `tengo 160, me he puesto 5 de rápida, he comido pasta, luego he salido a andar una hora y me duele la cabeza` | ¿Recoge los cinco datos? ¿Cuáles pierde? |
| E10 | Lo dice **como lo diría ella**, sin guion: una glucosa, una insulina y una comida | Sus palabras literales y qué entendió Federico |

Límite del producto: ninguna prueba puede pedirle a Federico una dosis ni un consejo médico. Si la usuaria experta lo pregunta por su cuenta, apunta qué responde: si recomienda algo, es una **incidencia de gravedad alta**.

---

## 7. Qué mirar en la usuaria experta, además de los resultados

- ¿Dónde duda o se queda parada?
- ¿Lee el resumen antes de pulsar ✅, o confirma sin mirar?
- ¿Lee los avisos (el de `❗ Revisa` y el de «no sustituye al equipo médico»)?
- ¿Prefiere escribir, hablar o mandar capturas?
- ¿Qué palabras usa ella? («lenta» o «basal», «pincharse», «bajada»). Sirven para mejorar la IA.
- ¿Qué intenta hacer que Federico no sabe hacer? Es la lista de ideas para la fase 2.

---

## 8. Al terminar

| ✔ | Qué |
|---|---|
| ☐ | Para el bot con Ctrl+C. |
| ☐ | Copia de seguridad de la BD real, sin abrirla: `cp diabetes_tracker.db backups/diabetes_tracker_AAAA-MM-DD.db` |
| ☐ | Rellena el apartado 8 del plan (resultado) con la usuaria experta todavía delante. |
| ☐ | Haz una foto a las hojas rellenas. |
| ☐ | Las BD **nunca** van a GitHub, al correo ni a la nube. |
| ☐ | Al contarle los fallos a Claude: mensaje de error y número de prueba, **sin datos de la usuaria experta**. |
