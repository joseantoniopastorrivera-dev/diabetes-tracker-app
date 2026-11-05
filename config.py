"""Configuración de Federico, leída del archivo .env."""
import os
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

ZONA_HORARIA = ZoneInfo("Europe/Madrid")
MODELO_POR_DEFECTO = "gemini-3.8-flash"


@dataclass(frozen=True)
class Config:
    telegram_token: str
    gemini_api_key: str
    gemini_model: str
    db_path: str
    usuarios_permitidos: frozenset[int]


def _leer_ids(valor: str) -> frozenset[int]:
    """Convierte "123, 456" en {123, 456}. Ignora huecos vacíos."""
    return frozenset(int(trozo) for trozo in valor.split(",") if trozo.strip())


def cargar_config() -> Config:
    """Lee el .env y falla pronto si falta algo imprescindible."""
    load_dotenv()

    faltan = [n for n in ("TELEGRAM_BOT_TOKEN", "GEMINI_API_KEY") if not os.getenv(n, "").strip()]
    if faltan:
        raise RuntimeError(f"Faltan variables en .env: {', '.join(faltan)}")

    usuarios = _leer_ids(os.getenv("ALLOWED_USER_IDS", ""))
    if not usuarios:
        raise RuntimeError(
            "ALLOWED_USER_IDS está vacío: el bot sería público. "
            "Pon al menos tu ID de Telegram en el .env."
        )

    return Config(
        telegram_token=os.environ["TELEGRAM_BOT_TOKEN"].strip(),
        gemini_api_key=os.environ["GEMINI_API_KEY"].strip(),
        gemini_model=os.getenv("GEMINI_MODEL", MODELO_POR_DEFECTO).strip(),
        db_path=os.getenv("DB_PATH", "diabetes_tracker.db").strip(),
        usuarios_permitidos=usuarios,
    )
