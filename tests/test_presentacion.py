from datetime import datetime

from modelos import LecturaTendencia, Registro
from presentacion import numero, texto_registro


def test_numero_en_formato_espanol():
    assert numero(4.0) == "4"
    assert numero(4.5) == "4,5"


def test_solo_muestra_campos_con_valor_y_escapa_html():
    r = Registro(usuario_id=1, fecha_hora=datetime(2026, 11, 5, 14, 30), texto_original="x",
                 glucosa=120, comida="pan <integral> & aceite",
                 tendencia=[LecturaTendencia("13:00", 180)])
    texto = texto_registro(r, ["glucosa = 900 parece fuera de lo normal"])
    assert "05/11 14:30" in texto
    assert "<b>120</b>" in texto
    assert "Rápida" not in texto
    assert "pan &lt;integral&gt; &amp; aceite" in texto
    assert "13:00 180" in texto
    assert "❗ Revisa: glucosa = 900" in texto


def test_textos_de_resumen():
    from modelos import Resumen
    from presentacion import texto_dia, texto_semana

    r = Registro(usuario_id=1, fecha_hora=datetime(2026, 11, 5, 14, 30), texto_original="x",
                 glucosa=120, insulina_rapida=4.0, comida="lentejas")
    dia = Resumen(datetime(2026, 11, 5), datetime(2026, 11, 6), [r])
    assert "14:30 · 🩸120 · 💉4 · lentejas" in texto_dia(dia)
    assert "En rango 70-180: <b>100 %</b>" in texto_dia(dia)

    semana = Resumen(datetime(2026, 10, 30), datetime(2026, 11, 6), [])
    assert "(30/10 - 05/11)" in texto_semana(semana)
    assert "No hay registros" in texto_semana(semana)
