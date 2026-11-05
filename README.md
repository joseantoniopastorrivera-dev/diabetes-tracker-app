# 🤖 Federico: asistente de registro para la diabetes (v2)

Federico es un bot de Telegram que registra el día a día de una persona con diabetes a partir de **texto, notas de voz o capturas del sensor de glucosa**. Usa la IA multimodal de Google Gemini para extraer los datos y **siempre pide confirmación antes de guardarlos**.

Es el prototipo funcional del proyecto emprendedor *Diabetes Tracker App*.

> Herramienta de registro y apoyo. No sustituye el criterio del equipo médico y no recomienda dosis ni tratamientos.

---

## 🚀 Qué hace

- **Registro multimodal:** texto, notas de voz y capturas del sensor.
- **Confirmación obligatoria:** muestra lo que ha entendido con tres botones: ✅ Guardar, ✏️ Corregir o ❌ Descartar. Para corregir basta con decir "eran 3 de rápida".
- **Datos que guarda:** glucosa, insulina rápida y basal, hidratos, comidas con hora, ejercicio, hipoglucemias, síntomas, notas y los puntos de la gráfica del sensor.
- **Avisos de lectura dudosa:** si un valor no es plausible (por ejemplo, 900 mg/dL), pide revisarlo.
- **Resúmenes descriptivos:** `/hoy` y `/semana` (totales, glucosa media, tiempo en rango 70-180 e hipoglucemias).
- **`/deshacer`:** anula el último registro guardado sin borrarlo.
- **Privado:** solo responde a los IDs de Telegram de la lista blanca.

## 📂 Estructura

```
Diabetes-Tracker-App/
├── bot.py              # Punto de entrada: monta las capas y arranca
├── config.py           # Lectura del .env, zona horaria y lista blanca
├── modelos.py          # Registro, estados, Resumen y avisos de rango
├── datos/
│   └── repositorio.py  # SQLite y migraciones (PRAGMA user_version)
├── ia/
│   ├── extractor.py    # Interfaz Extractor y esquema DatosExtraidos (Pydantic)
│   └── gemini.py       # Implementación con Google Gemini (asíncrona)
├── servicios.py        # Lógica: analizar, confirmar, corregir, deshacer, resúmenes
├── presentacion.py     # Formato HTML de los mensajes
├── telegram_bot.py     # Handlers, botones, comandos y lista blanca
├── tests/              # pytest (sin red ni API: usa un extractor falso)
└── docs/decisiones.md  # Por qué se hizo cada cosa
```

## 🛠️ Tecnologías

Python 3.13 · python-telegram-bot 22 · google-genai · Pydantic · SQLite · pytest

## ⚙️ Instalación

1. Clona el repositorio y crea el entorno virtual:
   ```bash
   git clone https://github.com/joseantoniopastorrivera-dev/Diabetes-Tracker-App.git
   cd Diabetes-Tracker-App
   python -m venv .venv
   source .venv/Scripts/activate   # Windows (Git Bash)
   pip install -r requirements.txt
   ```
2. Copia `.env.example` como `.env` y rellénalo. `ALLOWED_USER_IDS` es obligatorio: sin él, el bot no arranca. Para saber tu ID, escribe a @userinfobot. Si alguien no autorizado escribe al bot, su ID aparece en el log como "Acceso denegado".
3. Arranca el bot:
   ```bash
   python bot.py
   ```
   La primera vez migra automáticamente una base de datos de la v1, conservando sus registros. Haz antes una copia de seguridad.

## 🧪 Tests

```bash
python -m pytest
```

## 🔐 Privacidad

- La base de datos (`*.db`), las copias (`backups/`) y el `.env` no se suben nunca al repositorio.
- A Gemini solo se envía el mensaje que se está procesando.
- Los logs no contienen datos de salud ni el token del bot.
