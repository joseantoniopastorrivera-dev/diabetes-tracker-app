"""Punto de entrada de Federico: monta las piezas y arranca el bot."""
import logging

from config import cargar_config
from datos.repositorio import Repositorio
from ia.gemini import GeminiExtractor
from servicios import ServicioRegistros
from telegram_bot import crear_aplicacion


def main() -> None:
    logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
    # httpx registra cada URL de la API de Telegram, y esa URL lleva el token del bot dentro.
    logging.getLogger("httpx").setLevel(logging.WARNING)

    config = cargar_config()
    repo = Repositorio(config.db_path)
    version = repo.migrar()
    logging.info("Base de datos en versión %s", version)

    servicio = ServicioRegistros(repo, GeminiExtractor(config.gemini_api_key, config.gemini_model))
    logging.info("Federico listo (texto, fotos y notas de voz)")
    crear_aplicacion(config, servicio).run_polling()


if __name__ == "__main__":
    main()
