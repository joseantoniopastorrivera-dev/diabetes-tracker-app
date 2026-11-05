"""Modelo de datos de Federico: qué es un registro y cuándo un valor es sospechoso."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Estado(str, Enum):
    PENDIENTE = "pendiente"      # la IA lo ha extraído, falta que la usuaria lo confirme
    CONFIRMADO = "confirmado"    # cuenta para /hoy, /semana e informes
    DESCARTADO = "descartado"    # la usuaria dijo que estaba mal
    ANULADO = "anulado"          # se confirmó y luego se deshizo con /deshacer


@dataclass
class LecturaTendencia:
    """Un punto de la gráfica del sensor: hora aproximada y glucosa."""
    hora: str
    glucosa: int


@dataclass
class Registro:
    usuario_id: int
    fecha_hora: datetime
    texto_original: str
    usuario_alias: str | None = None
    glucosa: int | None = None
    insulina_rapida: float | None = None
    insulina_basal: float | None = None
    hidratos_hc: int | None = None
    comida: str | None = None
    ejercicio: str | None = None
    hipoglucemia: str | None = None
    sintomas: str | None = None
    notas: str | None = None
    tendencia: list[LecturaTendencia] = field(default_factory=list)
    estado: Estado = Estado.PENDIENTE
    id: int | None = None

    def esta_vacio(self) -> bool:
        """True si la IA no encontró ningún dato útil en el mensaje."""
        campos = (self.glucosa, self.insulina_rapida, self.insulina_basal, self.hidratos_hc,
                  self.comida, self.ejercicio, self.hipoglucemia, self.sintomas, self.notas)
        return all(c is None for c in campos) and not self.tendencia


# Rangos físicamente plausibles. NO son objetivos clínicos: solo sirven para
# detectar que la IA ha leído mal (p. ej., 1200 mg/dL o 85 unidades de rápida).
RANGOS = {
    "glucosa": (20, 600),
    "insulina_rapida": (0, 50),
    "insulina_basal": (0, 100),
    "hidratos_hc": (0, 400),
}


def avisos_de_rango(registro: Registro) -> list[str]:
    """Devuelve un aviso por cada valor fuera de lo plausible, para que la usuaria lo revise."""
    avisos = []
    for campo, (minimo, maximo) in RANGOS.items():
        valor = getattr(registro, campo)
        if valor is not None and not (minimo <= valor <= maximo):
            avisos.append(f"{campo.replace('_', ' ')} = {valor} parece fuera de lo normal ({minimo}-{maximo})")
    for lectura in registro.tendencia:
        minimo, maximo = RANGOS["glucosa"]
        if not (minimo <= lectura.glucosa <= maximo):
            avisos.append(f"lectura de la gráfica {lectura.hora} = {lectura.glucosa} parece errónea")
    return avisos
