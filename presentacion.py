"""Cómo se muestran los datos en Telegram (HTML). Funciones puras: fáciles de probar."""
from html import escape

from modelos import Registro


def numero(valor: float | int) -> str:
    """4.0 -> "4", 4.5 -> "4,5" (formato español, sin decimales inútiles)."""
    return f"{valor:g}".replace(".", ",")


def texto_registro(registro: Registro, avisos: list[str] | None = None) -> str:
    """Resumen del registro. Solo muestra lo que tiene valor, para que se lea de un vistazo."""
    lineas = [f"🕒 <b>{registro.fecha_hora:%d/%m %H:%M}</b>"]
    if registro.glucosa is not None:
        lineas.append(f"🩸 Glucosa: <b>{registro.glucosa}</b> mg/dL")
    if registro.insulina_rapida is not None:
        lineas.append(f"💉 Rápida: <b>{numero(registro.insulina_rapida)}</b> u")
    if registro.insulina_basal is not None:
        lineas.append(f"⏱️ Basal: <b>{numero(registro.insulina_basal)}</b> u")
    if registro.hidratos_hc is not None:
        lineas.append(f"🥖 Hidratos: <b>{registro.hidratos_hc}</b> g")
    # escape(): el texto viene de la usuaria o de la IA; un "<" suelto rompería el HTML de Telegram
    for emoji, nombre, valor in (("🍽️", "Comida", registro.comida), ("🏃", "Ejercicio", registro.ejercicio),
                                 ("⚠️", "Hipoglucemia", registro.hipoglucemia), ("🤒", "Síntomas", registro.sintomas),
                                 ("📝", "Notas", registro.notas)):
        if valor:
            lineas.append(f"{emoji} {nombre}: {escape(valor)}")
    if registro.tendencia:
        puntos = " → ".join(f"{escape(l.hora)} {l.glucosa}" for l in registro.tendencia)
        lineas.append(f"📈 Gráfica: {puntos}")
    if avisos:
        lineas.append("")
        lineas.extend(f"❗ Revisa: {escape(a)}" for a in avisos)
    return "\n".join(lineas)
