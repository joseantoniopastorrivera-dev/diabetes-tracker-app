"""Cómo se muestran los datos en Telegram (HTML). Funciones puras: fáciles de probar."""
from datetime import timedelta
from html import escape

from modelos import Registro, Resumen


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


def _linea_corta(r: Registro) -> str:
    """Una línea por registro para /hoy: 14:30 · 🩸120 · 💉4 · 🥖45 · lentejas"""
    trozos = [f"{r.fecha_hora:%H:%M}"]
    if r.glucosa is not None:
        trozos.append(f"🩸{r.glucosa}")
    if r.insulina_rapida is not None:
        trozos.append(f"💉{numero(r.insulina_rapida)}")
    if r.insulina_basal is not None:
        trozos.append(f"⏱️{numero(r.insulina_basal)}")
    if r.hidratos_hc is not None:
        trozos.append(f"🥖{r.hidratos_hc}")
    if r.hipoglucemia is not None:
        trozos.append("⚠️hipo")
    if r.comida:
        comida = r.comida if len(r.comida) <= 40 else r.comida[:39] + "…"
        trozos.append(escape(comida))
    return " · ".join(trozos)


def _totales(resumen: Resumen) -> list[str]:
    lineas = [
        f"💉 Rápida: <b>{numero(resumen.total_rapida)}</b> u · ⏱️ Basal: <b>{numero(resumen.total_basal)}</b> u",
        f"🥖 Hidratos: <b>{numero(resumen.total_hidratos)}</b> g",
    ]
    if resumen.media_glucosa is not None:
        lineas.append(f"🩸 Glucosa media: <b>{resumen.media_glucosa:.0f}</b> mg/dL "
                      f"(mín. {min(resumen.glucosas)}, máx. {max(resumen.glucosas)}, {len(resumen.glucosas)} lecturas)")
        lineas.append(f"🎯 En rango 70-180: <b>{resumen.tiempo_en_rango:.0f} %</b> de las lecturas")
    lineas.append(f"⚠️ Hipoglucemias: <b>{resumen.hipoglucemias}</b>")
    return lineas


def texto_dia(resumen: Resumen) -> str:
    if not resumen.registros:
        return f"📅 <b>{resumen.desde:%d/%m}</b>
Todavía no hay registros guardados hoy."
    lineas = [f"📅 <b>{resumen.desde:%d/%m}</b> · {len(resumen.registros)} registros", ""]
    lineas += [_linea_corta(r) for r in resumen.registros]
    return "
".join(lineas + [""] + _totales(resumen))


def texto_semana(resumen: Resumen) -> str:
    cabecera = f"📊 <b>Últimos 7 días</b> ({resumen.desde:%d/%m} - {resumen.hasta - timedelta(days=1):%d/%m})"
    if not resumen.registros:
        return cabecera + "
No hay registros guardados en estos días."
    lineas = [cabecera, f"{len(resumen.registros)} registros en {resumen.dias_con_registro} días", ""]
    lineas += _totales(resumen)
    lineas += ["", "<i>Datos descriptivos de tus registros. No sustituyen el criterio de tu equipo médico.</i>"]
    return "
".join(lineas)
