🤖 Federico - Asistente de Gestión de Diabetes (Multimodal)
Federico es un asistente inteligente diseñado para Telegram que facilita el seguimiento y registro diario de datos clínicos en personas con diabetes. Utiliza las capacidades multimodales de la API de Google Gemini para procesar entradas en lenguaje natural a través de texto, imágenes (capturas de sensores de glucosa) y notas de voz, estructurando toda la información de forma automática en una base de datos local SQLite.

🚀 Características Principales
Entrada Multimodal: Capacidad de interpretar mensajes de texto, audios de voz (notas de Telegram) y capturas de pantalla de gráficos de glucemia continua.

Inteligencia Artificial (Gemini): Extracción precisa de variables clínicas complejas mediante el SDK oficial de Google GenAI (gemini-3.8-flash).

Contexto Temporal Inteligente: Inyección de marcas de tiempo del sistema y de los mensajes de Telegram para traducir expresiones relativas ("hace media hora") en horas exactas (HH:MM).

Estructuración de Datos: Registro automático de:

Niveles de glucemia actual y tendencias gráficas.

Insulina rápida y basal.

Hidratos de carbono (HC) consumidos y desglose de comidas con sus respectivas horas.

Episodios de hipoglucemia con marca temporal.

Ejercicio físico, síntomas y notas contextuales (estrés, ciclo menstrual, etc.).

Almacenamiento Local Seguro: Persistencia de datos estructurados mediante SQLite.

📂 Estructura del Proyecto
Diabetes-Tracker-App/
│
├── bot.py          # Lógica principal del bot de Telegram (polling, manejadores de texto/foto/voz)
├── analyzer.py     # Módulo de integración con Gemini API y prompts del sistema estructurados
├── database.py     # Gestión de la base de datos SQLite y esquemas de guardado
├── .env            # Variables de entorno y credenciales (Excluido del control de versiones)
├── .gitignore      # Archivos ignorados por Git (seguridad para credenciales y DB)
└── README.md       # Documentación del proyecto

🛠️ Tecnologías y Librerías
Python (v3.11+)

python-telegram-bot (Interacción con la API de Telegram)

google-genai (SDK oficial para modelos Gemini)

SQLite (Base de datos embebida)

python-dotenv (Gestión segura de variables de entorno)

⚙️ Configuración e Instalación Local
1. Clona el repositorio:
git clone [https://github.com/tu-usuario/diabetes-tracker-bot.git](https://github.com/tu-usuario/diabetes-tracker-bot.git)
cd Diabetes-Tracker-App

2. Crea y activa un entorno virtual (recomendado):
python -m venv venv
# En Windows (Git Bash):
source venv/Scripts/activate

3. Instala las dependencias:
pip install python-telegram-bot google-genai python-dotenv

4. Configura tus credenciales:
Crea un archivo llamado .env en la raíz del proyecto y añade tus claves secretas:
TELEGRAM_BOT_TOKEN=tu_token_de_telegram_aqui
GEMINI_API_KEY=tu_api_key_de_gemini_aqui

5. Ejecuta el bot:
python bot.py
