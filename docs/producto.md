# Especificación del producto

Qué tiene que ser Diabetes Tracker App cuando deje de ser un prototipo. Sale de la memoria del proyecto emprendedor de IPE II (apartados 5.1 y 5.2) y sirve como lista de comprobación de las fases de `docs/hoja-de-ruta.md`.

> **Aviso legal:** «Herramienta de registro y apoyo. No sustituye el criterio de tu equipo médico.»

## Ficha de producto

| Característica | Especificación |
|---|---|
| Nombre | Diabetes Tracker App (prototipo actual: el bot «Federico») |
| Categoría | App de salud y bienestar (registro y seguimiento). **No es un producto sanitario.** |
| Plataformas | Android 8.0 o superior e iOS 15 o superior (beta en 2027). Hoy, Telegram. |
| Tecnología | Desarrollo multiplataforma, backend en Python, base de datos cifrada, IA multimodal (Gemini, modelo ligero) detrás de la interfaz `Extractor`. |
| Idioma | Español. Inglés previsto para 2028. |

## Gratis y Premium

El registro básico es **gratis para siempre**: es un compromiso del proyecto, no una oferta de lanzamiento.

| Plan | Precio | Funciones | Estado |
|---|---|---|---|
| Gratis | 0 € | Registro por voz, foto o texto; confirmación de cada dato; historial ilimitado; gráfica diaria; resumen semanal básico | ✅ Registro, confirmación, historial y `/semana` en el bot. ⬜ Gráfica. |
| Premium | 2,99 €/mes o 24,99 €/año | Informe completo con IA para la consulta; exportación PDF/CSV; gráficas semanales y mensuales; acceso para cuidadores; recordatorios | ⬜ Fase 2 (piloto, gratis para los participantes) y fase 4 (cobro) |

## Requisitos de calidad

Son medibles. El plan de pruebas de cada fase debe comprobar los que le toquen.

| Requisito | Objetivo | Cómo se comprueba |
|---|---|---|
| Rapidez del registro | Registro completo en **menos de 15 segundos** | Cronómetro en el plan de pruebas (pruebas ⏱) y métrica del piloto |
| Rapidez de la IA | Respuesta en **menos de 5 segundos** | Tiempo entre el mensaje y la propuesta de registro |
| Fiabilidad | El **100 %** de los registros los confirma el usuario antes de guardarse | Estados del registro (D2): nada cuenta sin ✅ |
| Disponibilidad | **≥ 99 %** del servicio | Monitorización en el despliegue (fase 3) |
| Seguridad | Cifrado en tránsito (TLS) y en reposo; servidores en la UE; RGPD; evaluación de impacto (EIPD) | Fase 2 (consentimiento) y fase 3 (cifrado y despliegue) |
| Accesibilidad | WCAG 2.2, nivel AA: alto contraste, texto escalable y registro por voz | Revisión de la app móvil (fase 3) |

## Límites que no se cruzan

- **No calcular dosis, no recomendar tratamientos, no emitir alertas terapéuticas.** Convertiría la app en producto sanitario de clase IIa (MDR, regla 11). Ver D7 y D9 en `docs/decisiones.md`.
- **No vender ni ceder datos** a terceros ni a aseguradoras.
- **A la IA solo se envía el mensaje que se está procesando**, nunca el historial completo.
- **Ninguna función vital detrás de un pago** y sin *dark patterns*.
- **El usuario puede exportar y borrar su historial** (fase 2).
