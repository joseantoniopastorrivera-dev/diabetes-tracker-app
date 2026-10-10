import os
import io
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from database import init_db, guardar_registro
from analyzer import analizar_mensaje_salud

load_dotenv()
token_env = os.getenv("TELEGRAM_BOT_TOKEN")

if not token_env:
    raise RuntimeError("Variable crítica faltante: 'TELEGRAM_BOT_TOKEN' en .env")

TOKEN: str = token_env

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    saludo = (
        "¡Hola! Soy Federico.\n\n"
        "Puedes escribirme, enviarme capturas de pantalla de tu sensor o "
        "incluso **mandarme notas de voz** contándome qué has comido o cómo te encuentras."
    )
    await update.message.reply_text(saludo)

async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return

    texto = update.message.text or update.message.caption or ""
    imagen_bytes = None
    audio_bytes = None

    # Procesar si adjunta foto
    if update.message.photo:
        foto = update.message.photo[-1]
        archivo = await context.bot.get_file(foto.file_id)
        buffer = io.BytesIO()
        await archivo.download_to_memory(buffer)
        imagen_bytes = buffer.getvalue()

    # Procesar si adjunta nota de voz
    if update.message.voice:
        voz = update.message.voice
        archivo = await context.bot.get_file(voz.file_id)
        buffer = io.BytesIO()
        await archivo.download_to_memory(buffer)
        audio_bytes = buffer.getvalue()
        texto = "[Nota de voz enviada por el usuario]"

    if not texto and not imagen_bytes and not audio_bytes:
        return

    user = update.message.from_user
    usuario_id = user.id if user else 0
    usuario_alias = user.first_name if user else "Anonimo"

    # Procesar con Gemini Multimodal (Texto + Imagen + Audio)
    datos = analizar_mensaje_salud(texto=texto, imagen_bytes=imagen_bytes, audio_bytes=audio_bytes)

    if not datos:
        await update.message.reply_text("⚠️ No pude procesar el mensaje o el audio. Inténtalo de nuevo.")
        return

    # Guardar en SQLite
    guardar_registro(
        usuario_id=usuario_id,
        usuario_alias=usuario_alias,
        glucosa=datos.get("glucosa"),
        insulina=datos.get("insulina_rapida"),
        comida=datos.get("comida"),
        ejercicio=datos.get("ejercicio"),
        texto_original=texto
    )

    # Construir resumen detallado para Telegram
    tendencia = datos.get("tendencia_grafica")
    tendencia_str = ""
    if tendencia:
        puntos = [f"• {p['hora']} ➔ {p['glucosa']} mg/dL" for p in tendencia]
        tendencia_str = "\n📈 *Evolución en gráfica:*\n" + "\n".join(puntos)

    resumen = (
        "✅ *Registro guardado (audio/multimodal):*\n\n"
        f"• 🩸 *Glucosa actual:* {datos.get('glucosa') or 'No indicado'} mg/dL\n"
        f"• 💉 *Insulina rápida:* {datos.get('insulina_rapida') or 'No indicado'} u\n"
        f"• ⏱️ *Insulina basal:* {datos.get('insulina_basal') or 'No indicado'} u\n"
        f"• 🥖 *Hidratos (HC):* {datos.get('hidratos_hc') or 'No indicado'} g\n"
        f"• 🍽️ *Comida:* {datos.get('comida') or 'No indicado'}\n"
        f"• 🏃 *Deporte:* {datos.get('ejercicio') or 'No indicado'}\n"
        f"• ⚠️ *Hipoglucemia:* {datos.get('hipoglucemia') or 'No'}\n"
        f"• 📝 *Notas:* {datos.get('notas') or '-'}"
        f"{tendencia_str}"
    )
    await update.message.reply_text(resumen, parse_mode="Markdown")

def main():
    init_db()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    # Escucha texto, fotos y notas de voz
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.VOICE) & ~filters.COMMAND, manejar_mensaje))

    print("🤖 Federico listo con soporte total (Texto + Fotos + Notas de voz)...")
    app.run_polling()

if __name__ == "__main__":
    main()