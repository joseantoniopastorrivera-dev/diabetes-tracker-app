"""Lógica de Federico. No sabe nada de Telegram: recibe datos y devuelve datos.

Así, la futura API o la app móvil podrán reutilizar exactamente estas reglas.
"""
from datetime import datetime

from config import ZONA_HORARIA
from datos.repositorio import Repositorio
from ia.extractor import DatosExtraidos, Entrada, Extractor, LecturaIA
from modelos import Estado, LecturaTendencia, Registro


class ErrorOperacion(Exception):
    """Algo que la usuaria pidió no se puede hacer. El mensaje se le puede mostrar tal cual."""


def a_hora_local(momento: datetime) -> datetime:
    """Pasa una fecha con zona (Telegram la da en UTC) a hora de España sin zona, como se guarda en la BD."""
    return momento.astimezone(ZONA_HORARIA).replace(tzinfo=None)


def aplicar_datos(registro: Registro, datos: DatosExtraidos) -> None:
    """Copia lo que devolvió la IA al registro (pydantic -> dataclass del dominio)."""
    registro.glucosa = datos.glucosa
    registro.insulina_rapida = datos.insulina_rapida
    registro.insulina_basal = datos.insulina_basal
    registro.hidratos_hc = datos.hidratos_hc
    registro.comida = datos.comida
    registro.ejercicio = datos.ejercicio
    registro.hipoglucemia = datos.hipoglucemia
    registro.sintomas = datos.sintomas
    registro.notas = datos.notas
    registro.tendencia = [LecturaTendencia(l.hora, l.glucosa) for l in (datos.tendencia_grafica or [])]


def datos_de(registro: Registro) -> DatosExtraidos:
    """Lo contrario de aplicar_datos: para mandar a la IA el registro que se va a corregir."""
    return DatosExtraidos(
        glucosa=registro.glucosa, insulina_rapida=registro.insulina_rapida,
        insulina_basal=registro.insulina_basal, hidratos_hc=registro.hidratos_hc,
        comida=registro.comida, ejercicio=registro.ejercicio, hipoglucemia=registro.hipoglucemia,
        sintomas=registro.sintomas, notas=registro.notas,
        tendencia_grafica=[LecturaIA(hora=l.hora, glucosa=l.glucosa) for l in registro.tendencia] or None,
    )


class ServicioRegistros:
    def __init__(self, repo: Repositorio, extractor: Extractor):
        self.repo = repo
        self.extractor = extractor

    async def analizar(self, usuario_id: int, alias: str | None, entrada: Entrada) -> Registro:
        """Extrae los datos y los guarda como PENDIENTES. Si no hay nada útil, no guarda (id = None)."""
        datos = await self.extractor.extraer(entrada)
        registro = Registro(
            usuario_id=usuario_id, usuario_alias=alias,
            fecha_hora=a_hora_local(entrada.momento),
            texto_original=entrada.texto or descripcion_adjuntos(entrada),
        )
        aplicar_datos(registro, datos)
        if not registro.esta_vacio():
            self.repo.guardar(registro)
        return registro

    async def corregir(self, usuario_id: int, registro_id: int, entrada: Entrada) -> Registro:
        """Rehace un registro pendiente combinando lo anterior con la corrección."""
        registro = self._pendiente_propio(usuario_id, registro_id)
        entrada.corrige_a = datos_de(registro)
        datos = await self.extractor.extraer(entrada)
        aplicar_datos(registro, datos)
        # Guardamos también la corrección: si la IA se equivoca, queda rastro de qué se dijo.
        registro.texto_original += f"\n[corrección] {entrada.texto or descripcion_adjuntos(entrada)}"
        self.repo.actualizar_datos(registro)
        return registro

    def confirmar(self, usuario_id: int, registro_id: int) -> Registro:
        registro = self._pendiente_propio(usuario_id, registro_id)
        self.repo.cambiar_estado(registro_id, Estado.CONFIRMADO)
        registro.estado = Estado.CONFIRMADO
        return registro

    def descartar(self, usuario_id: int, registro_id: int) -> Registro:
        registro = self._pendiente_propio(usuario_id, registro_id)
        self.repo.cambiar_estado(registro_id, Estado.DESCARTADO)
        registro.estado = Estado.DESCARTADO
        return registro

    def deshacer(self, usuario_id: int) -> Registro:
        """Anula el último registro confirmado. No lo borra: queda en la BD como ANULADO."""
        registro = self.repo.ultimo(usuario_id, Estado.CONFIRMADO)
        if registro is None:
            raise ErrorOperacion("No hay ningún registro guardado que deshacer.")
        self.repo.cambiar_estado(registro.id, Estado.ANULADO)
        registro.estado = Estado.ANULADO
        return registro

    def _pendiente_propio(self, usuario_id: int, registro_id: int) -> Registro:
        """Comprueba que el registro existe, es de esta usuaria y sigue pendiente.

        También evita el doble clic: si ya se confirmó, el segundo intento da error en vez de repetir.
        """
        registro = self.repo.obtener(registro_id)
        if registro is None or registro.usuario_id != usuario_id:
            raise ErrorOperacion("No encuentro ese registro.")
        if registro.estado is not Estado.PENDIENTE:
            raise ErrorOperacion(f"Ese registro ya está {registro.estado.value}.")
        return registro


def descripcion_adjuntos(entrada: Entrada) -> str:
    partes = [nombre for nombre, hay in (("[foto]", entrada.imagen), ("[nota de voz]", entrada.audio)) if hay]
    return " ".join(partes) or "[mensaje vacío]"
