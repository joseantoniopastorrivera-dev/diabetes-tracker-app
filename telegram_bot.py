"""Adaptador de Telegram: traduce mensajes y botones a llamadas al servicio."""
import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import (Application, CallbackQueryHandler, CommandHandler, ContextTypes,
                          MessageHandler, filters)

from config import ZONA_HORARIA, Config
from ia.extractor import Entrada, ErrorExtraccion
from modelos import avisos_de_rango
from presentacion import texto_registro
from servicios import ErrorOperacion, ServicioRegistros

log = logging.getLogger(__name__)

CORRIGIENDO = "corrigiendo"   # clave en user_data: id del registro que se está corrigiendo


def teclado(registro_id: int) -> InlineKeyboardMarkup:
    # callback_data viaja con el botón y vuelve cuando se pulsa: "accion:id"
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Guardar", callback_data=f"ok:{registro_id}"),
        InlineKeyboardButton("✏️ Corregir", callback_data=f"fix:{registro_id}"),
        InlineKeyboardButton("❌ Descartar", callback_data=f"no:{registro_id}"),
    ]])


def _servicio(context: ContextTypes.DEFAULT_TYPE) -> ServicioRegistros:
    return context.bot_data["servicio"]


async def _descargar(context: ContextTypes.DEFAULT_TYPE, file_id: str) -> bytes:
    archivo = await context.bot.get_file(file_id)
    return bytes(await archivo.download_as_bytearray())


# ---------- Comandos ----------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text(
        "¡Hola! Soy Federico.\n\n"
        "Escríbeme, mándame una nota de voz o una captura del sensor y apunto glucosa, "
        "insulina, hidratos y comidas. Antes de guardar nada te pediré que lo confirmes."
    )


async def cmd_cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.pop(CORRIGIENDO, None) is None:
        await update.effective_message.reply_text("No había nada que cancelar.")
    else:
        await update.effective_message.reply_text("Vale, dejo el registro como estaba. Sigue esperando tu ✅ o ❌.")


# ---------- Mensajes (texto, foto, voz) ----------

async def recibir_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mensaje = update.effective_message
    usuario = update.effective_user

    entrada = Entrada(
        momento=mensaje.date.astimezone(ZONA_HORARIA),   # Telegram da la hora en UTC
        texto=mensaje.text or mensaje.caption or "",
    )
    if mensaje.photo:
        entrada.imagen = await _descargar(context, mensaje.photo[-1].file_id)  # [-1] = mayor resolución
    if mensaje.voice:
        entrada.audio = await _descargar(context, mensaje.voice.file_id)

    await context.bot.send_chat_action(mensaje.chat_id, ChatAction.TYPING)  # "escribiendo..." mientras piensa

    corrigiendo = context.user_data.pop(CORRIGIENDO, None)
    try:
        if corrigiendo is not None:
            registro = await _servicio(context).corregir(usuario.id, corrigiendo, entrada)
        else:
            registro = await _servicio(context).analizar(usuario.id, usuario.first_name, entrada)
    except ErrorExtraccion:
        if corrigiendo is not None:
            context.user_data[CORRIGIENDO] = corrigiendo  # que pueda reintentar la corrección
        await mensaje.reply_text("⚠️ No he podido analizarlo ahora mismo. Inténtalo de nuevo en un momento.")
        return
    except ErrorOperacion as e:
        await mensaje.reply_text(str(e))
        return

    if registro.id is None:
        await mensaje.reply_text("No he encontrado datos que apuntar en ese mensaje. 🤔")
        return

    await mensaje.reply_text(
        texto_registro(registro, avisos_de_rango(registro)) + "\n\n¿Lo guardo?",
        parse_mode=ParseMode.HTML,
        reply_markup=teclado(registro.id),
    )


# ---------- Botones ----------

async def pulsar_boton(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    accion, _, id_texto = (query.data or "").partition(":")
    if not id_texto.isdigit():
        await query.answer()
        return
    registro_id, usuario_id = int(id_texto), update.effective_user.id
    servicio = _servicio(context)

    try:
        if accion == "ok":
            registro = servicio.confirmar(usuario_id, registro_id)
            await query.answer("Guardado")
            await query.edit_message_text(texto_registro(registro) + "\n\n✅ <b>Guardado</b>", parse_mode=ParseMode.HTML)
        elif accion == "no":
            registro = servicio.descartar(usuario_id, registro_id)
            await query.answer("Descartado")
            await query.edit_message_text(texto_registro(registro) + "\n\n❌ <i>Descartado</i>", parse_mode=ParseMode.HTML)
        elif accion == "fix":
            servicio.obtener_pendiente(usuario_id, registro_id)   # falla si ya no está pendiente
            context.user_data[CORRIGIENDO] = registro_id
            await query.answer()
            await query.edit_message_reply_markup(None)           # quita los botones del mensaje viejo
            await query.message.reply_text(
                "✏️ Dime qué cambio (texto, voz o foto). Por ejemplo: «eran 3 de rápida».\n"
                "Si al final está bien, escribe /cancelar."
            )
        else:
            await query.answer()
    except ErrorOperacion as e:
        await query.answer(str(e), show_alert=True)


async def registrar_error(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    log.error("Error no controlado", exc_info=context.error)


def crear_aplicacion(config: Config, servicio: ServicioRegistros) -> Application:
    app = Application.builder().token(config.telegram_token).build()
    app.bot_data["servicio"] = servicio   # bot_data: compartido por todos los handlers

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("cancelar", cmd_cancelar))
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO | filters.VOICE) & ~filters.COMMAND, recibir_mensaje))
    app.add_handler(CallbackQueryHandler(pulsar_boton))
    app.add_error_handler(registrar_error)
    return app
