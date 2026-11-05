# Hoja de ruta de Federico

Fases de la versión 2, alineadas con el calendario de la memoria del proyecto emprendedor (apartado 1.4). Cada fase empieza con su **fase 0** (preparación: skill `preparar-fase`) y termina con su **plan de pruebas** con Marta (skill `plan-pruebas-fase`).

Estados posibles: ⬜ pendiente · 🟡 en curso · ✅ hecha.

**Fuera de alcance en todas las fases:** calcular dosis, recomendar tratamientos o emitir alertas terapéuticas. Eso convertiría la app en producto sanitario (MDR, regla 11). Ver `docs/decisiones.md` (D7 y D9).

---

## Fase 1 · Federico sólido · 🟡 (noviembre-diciembre de 2026)
Rama `v2-fase1`. Objetivo: cumplir lo que la memoria ya promete, sin cambiar de canal.
- ✅ Arquitectura por capas (modelos, datos, ia, servicios y Telegram).
- ✅ Esquema completo con migración de la BD de la v1.
- ✅ Confirmación con botones Guardar, Corregir y Descartar.
- ✅ `/hoy`, `/semana`, `/deshacer` y `/ayuda`.
- ✅ Lista blanca, aviso de IA y aviso legal.
- ✅ Tests y registro de decisiones.
- ⬜ Prueba real con Marta (`docs/plan-pruebas-fase1.pdf`) y fusión en `main`.

## Fase 2 · Piloto · ⬜ (1.er trimestre de 2027, de 5 a 10 usuarios)
Objetivo: validar con usuarios reales y medir.
- Alta con **consentimiento explícito** (RGPD) y `/borrarmisdatos`. Sustituye a la lista blanca fija.
- **Resumen semanal con IA** e **informe PDF para el endocrino**, que es la propuesta de valor diferencial.
- **Modo cuidador** (buyer persona Javier): invitar a un familiar a ver el día.
- **Recordatorios** configurables (por ejemplo, la basal).
- **Métricas del piloto**: segundos por registro, retención a 30 días y correcciones de la IA.

## Fase 3 · Beta multiplataforma · ⬜ (2.º trimestre de 2027)
Objetivo: dejar de depender de Telegram como único canal.
- **API REST** (por ejemplo, FastAPI) sobre `servicios.py`. Telegram pasa a ser un cliente más.
- **App móvil** con gráficas. El stack está por decidir.
- **Importación automática**: Health Connect / Apple Health y Nightscout / LibreView.
- **Segundo proveedor de IA** detrás de `Extractor` (por ejemplo, Mistral o un modelo local).
- Cifrado en reposo y despliegue en la UE.
