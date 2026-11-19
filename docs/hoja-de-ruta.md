# Hoja de ruta de Federico

Fases de la versión 2, alineadas con el calendario de la memoria del proyecto emprendedor (apartado 1.4). Cada fase empieza con su **fase 0** (preparación: skill `preparar-fase`) y termina con su **plan de pruebas** con la usuaria experta (skill `plan-pruebas-fase`).

Estados posibles: ⬜ pendiente · 🟡 en curso · ✅ hecha.

**Fuera de alcance en todas las fases:** calcular dosis, recomendar tratamientos o emitir alertas terapéuticas. Eso convertiría la app en producto sanitario (MDR, regla 11). Ver `docs/decisiones.md` (D7 y D9).

---

## Fase 1 · Federico sólido · 🟡 (noviembre-diciembre de 2026)
Rama `v2-fase1`, fusionada en `main` el 16-11-2026. Objetivo: cumplir lo que la memoria ya promete, sin cambiar de canal.
- ✅ Arquitectura por capas (modelos, datos, ia, servicios y Telegram).
- ✅ Esquema completo con migración de la BD de la v1.
- ✅ Confirmación con botones Guardar, Corregir y Descartar.
- ✅ `/hoy`, `/semana`, `/deshacer` y `/ayuda`.
- ✅ Lista blanca, aviso de IA y aviso legal.
- ✅ Tests y registro de decisiones.
- ✅ Fusión en `main`, adelantada a la prueba para que el repositorio público muestre la v2.
- ⬜ Prueba real con la usuaria experta (`docs/plan-pruebas-fase1.pdf` y `docs/guion-prueba-usuaria.pdf`). Hasta entonces la fase sigue en curso.

## Fase 2 · Piloto · ⬜ (1.er trimestre de 2027, de 5 a 10 usuarios)
Objetivo: validar con usuarios reales y medir. Las funciones marcadas **(Premium)** serán de pago en la fase 4; en el piloto son gratis para los participantes (ver `docs/producto.md`).
- Alta con **consentimiento explícito** (RGPD) y `/borrarmisdatos`. Sustituye a la lista blanca fija.
- **Exportar mi historial** (`/exportar`, CSV): el usuario puede llevarse sus datos, además de borrarlos.
- **Resumen semanal con IA** e **informe PDF para el endocrino** (Premium), que es la propuesta de valor diferencial.
- **Modo cuidador** (Premium; buyer persona Javier): invitar a un familiar a ver el día.
- **Recordatorios** configurables, por ejemplo, la basal (Premium).
- **Métricas del piloto**, con objetivo:
  - segundos por registro: **menos de 15 s**;
  - retención a 30 días: **más del 40 %**;
  - correcciones de la IA por cada 100 registros (sin objetivo fijo; sirve para decidir el modelo).

## Fase 3 · Beta multiplataforma · ⬜ (2.º trimestre de 2027)
Objetivo: dejar de depender de Telegram como único canal.
- **API REST** (por ejemplo, FastAPI) sobre `servicios.py`. Telegram pasa a ser un cliente más.
- **App móvil** con gráficas. El stack está por decidir.
- **Importación automática**: Health Connect / Apple Health y Nightscout / LibreView.
- **Segundo proveedor de IA** detrás de `Extractor` (por ejemplo, Mistral o un modelo local).
- Cifrado en reposo y despliegue en la UE.
- Accesibilidad WCAG 2.2 AA en la app (alto contraste, texto escalable y registro por voz).

## Fase 4 · Lanzamiento · ⬜ (2.º semestre de 2027)
Objetivo: publicar en las tiendas con el modelo *freemium* (ver `docs/modelo-de-negocio.md`).
- Publicación en **Google Play y App Store** (cuentas de desarrollador, ficha y ASO).
- **Cobro del Premium** dentro de la app: 2,99 €/mes o 24,99 €/año. Oferta: 3 meses gratis para los usuarios del piloto.
- Aviso legal, política de privacidad y EIPD publicados antes del lanzamiento.
- **Métricas de negocio:** conversión a Premium del **3–5 %**; punto de equilibrio en unos **45 usuarios de pago**.
