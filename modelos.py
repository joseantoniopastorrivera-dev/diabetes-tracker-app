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


# Rango 70-180 mg/dL: el del consenso internacional de tiempo en rango (TIR).
# Se usa SOLO para describir el pasado, nunca para recomendar nada.
RANGO_OBJETIVO = (70, 180)


@dataclass
class Resumen:
    """Estadística descriptiva de los registros confirmados de un periodo."""
    desde: datetime
    hasta: datetime
    registros: list[Registro]

    @property
    def glucosas(self) -> list[int]:
        # Solo la glucosa principal de cada registro: la gráfica de una captura suele
        # repetir ese mismo valor y contaríamos lecturas dos veces.
        return [r.glucosa for r in self.registros if r.glucosa is not None]

    def _suma(self, campo: str) -> float:
        return sum(getattr(r, campo) for r in self.registros if getattr(r, campo) is not None)

    @property
    def total_rapida(self) -> float:
        return self._suma("insulina_rapida")

    @property
    def total_basal(self) -> float:
        return self._suma("insulina_basal")

    @property
    def total_hidratos(self) -> float:
        return self._suma("hidratos_hc")

    @property
    def media_glucosa(self) -> float | None:
        return sum(self.glucosas) / len(self.glucosas) if self.glucosas else None

    @property
    def tiempo_en_rango(self) -> float | None:
        """% de lecturas dentro de 70-180. Aproximado: son lecturas sueltas, no el sensor continuo."""
        if not self.glucosas:
            return None
        minimo, maximo = RANGO_OBJETIVO
        return 100 * sum(minimo <= g <= maximo for g in self.glucosas) / len(self.glucosas)

    @property
    def hipoglucemias(self) -> int:
        """Registros con una bajada anotada o con glucosa por debajo de 70."""
        return sum(r.hipoglucemia is not None or (r.glucosa is not None and r.glucosa < RANGO_OBJETIVO[0])
                   for r in self.registros)

    @property
    def dias_con_registro(self) -> int:
        return len({r.fecha_hora.date() for r in self.registros})
