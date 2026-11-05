"""Pruebas del guardián de la lista blanca con objetos simulados (sin conectar a Telegram)."""
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from telegram.ext import ApplicationHandlerStop

from telegram_bot import solo_permitidos


def actualizacion(usuario_id: int):
    mensaje = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(effective_user=SimpleNamespace(id=usuario_id), callback_query=None,
                             effective_message=mensaje)
    context = SimpleNamespace(bot_data={"permitidos": frozenset({1})})
    return update, context, mensaje


async def test_usuario_permitido_pasa():
    update, context, mensaje = actualizacion(1)
    await solo_permitidos(update, context)          # no lanza nada: sigue al siguiente handler
    mensaje.reply_text.assert_not_called()


async def test_usuario_desconocido_se_bloquea():
    update, context, mensaje = actualizacion(999)
    with pytest.raises(ApplicationHandlerStop):
        await solo_permitidos(update, context)
    mensaje.reply_text.assert_awaited_once_with("🔒 Este bot es privado.")
