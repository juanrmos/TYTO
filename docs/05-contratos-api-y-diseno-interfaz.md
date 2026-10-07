# Contratos API y diseño de interfaz

## Aplicación web para la estimación de afluencia turística en la Cueva de las Lechuzas

**Versión:** 0.1  
**Estado:** Aprobado  
**Documentos relacionados:**

- `03-especificacion-motor-estimacion.md`
- `04-arquitectura-y-modelo-de-datos.md`

---

## 1. Propósito

Este documento define los contratos de las APIs del sistema y el diseño funcional mínimo de la interfaz. Los agentes no pueden cambiar nombres de campos, rutas, códigos de estado ni estructuras de respuesta sin actualizar este documento.

---

## 2. Convenciones generales

| Convención | Valor |
|---|---|
| Zona horaria de fechas | `America/Lima` (UTC−5) |
| Formato de fechas | `YYYY-MM-DD` |
| Formato de timestamps | ISO 8601 con offset: `2026-10-06T13:00:00-05:00` |
| Codificación | UTF-8 |
| Content-Type | `application/json` |
| Idioma de los textos de respuesta | Español |
| Versión de la API | `/api/v1/` |
| CORS | Permitido desde el dominio del frontend (configurable por variable de entorno) |

---

## 3. API pública del STP

### 3.1. Endpoint de salud

```
GET /health
```

**Respuesta 200:**

```json
{
  "status": "ok",
  "service": "stp",
  "version": "1.0.0"
}
```

---

### 3.2. Obtener el pronóstico semanal de un destino

Este es el endpoint principal consumido por el frontend.

```
GET /api/v1/forecast/{destination_slug}
```

**Parámetros de ruta:**

| Parámetro | Tipo | Descripción |
|---|---|---|
| `destination_slug` | `string` | Identificador del destino (p.ej. `cueva-lechuzas`) |

**Parámetros de consulta opcionales:**

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `from_date` | `string (YYYY-MM-DD)` | Hoy (Lima) | Primera fecha del horizonte |

**Respuesta 200 — pronóstico completo:**

```json
{
  "destination": {
    "slug": "cueva-lechuzas",
    "name": "Cueva de las Lechuzas",
    "official_url": "https://sernanp.gob.pe/tingo-maria",
    "tickets_url": "https://entradas.sernanp.gob.pe",
    "directions_url": "https://sernanp.gob.pe/tingo-maria#como-llegar"
  },
  "generated_at": "2026-10-06T13:00:00-05:00",
  "engine_version": "ME-1.0",
  "generator_version": "SG-1.0",
  "weather_fetched_at": "2026-10-06T10:30:00-05:00",
  "best_day": {
    "date": "2026-10-07",
    "label": "MEJOR_OPCION"
  },
  "week_warning": null,
  "days": [
    {
      "date": "2026-10-06",
      "day_of_week": "Martes",
      "is_today": true,
      "is_best": false,
      "best_label": null,
      "calendar_note": null,
      "affuence": {
        "score": 28,
        "level": "BAJA",
        "level_label": "Baja"
      },
      "convenience": {
        "score": 88,
        "category": "RECOMENDADO",
        "category_label": "Recomendado"
      },
      "weather": {
        "condition_label": "Parcialmente nublado",
        "weather_code": 2,
        "temp_max_c": 28,
        "temp_min_c": 20,
        "rain_mm": 1.2,
        "rain_probability_pct": 15,
        "wind_max_kmh": 12,
        "uv_max": 7,
        "sunshine_hours": 6.2
      },
      "recommendation": {
        "text": "Condiciones aceptables para la visita. Se espera una concurrencia moderada con buen clima. Verifique horarios en los canales oficiales.",
        "template_key": "RECOMENDADO_MEDIA_FAVORABLE"
      },
      "active_factors": [
        "El mes presenta afluencia histórica baja",
        "Es martes ordinario"
      ],
      "is_degraded": false,
      "degraded_reason": null
    }
  ],
  "methodology_warning": "La puntuación de afluencia es una estimación académica calculada mediante datos mensuales oficiales, distribución diaria sintética y pronóstico meteorológico. No representa ocupación real ni conteo en tiempo real. Antes de visitar, consulte horarios, entradas y restricciones en los canales oficiales de SERNANP."
}
```

**Notas sobre el array `days`:**

- Siempre contiene exactamente **7 elementos** ordenados cronológicamente.
- El primer elemento corresponde a `from_date` (hoy por defecto).
- `is_today` es `true` solo para el elemento cuya fecha coincide con la fecha local actual.
- `is_best` es `true` para el día seleccionado como mejor opción o mejor alternativa.
- `best_label` puede ser `"MEJOR_OPCION"`, `"MEJOR_ALTERNATIVA"` o `"MENOR_AFLUENCIA"`, o `null`.
- `calendar_note` puede ser `"Feriado"`, `"Feriado largo"`, `"Puente"`, `"Periodo especial"` o `null`.
- `week_warning` en la raíz puede ser `null` o una cadena de texto si ningún día es recomendable.

**Respuesta 200 — día con datos degradados (sin meteorología):**

```json
{
  "date": "2026-10-10",
  "day_of_week": "Sábado",
  "is_today": false,
  "is_best": false,
  "best_label": null,
  "calendar_note": null,
  "affuence": {
    "score": 72,
    "level": "ALTA",
    "level_label": "Alta"
  },
  "convenience": {
    "score": null,
    "category": "SIN_DATOS",
    "category_label": "Sin datos meteorológicos"
  },
  "weather": null,
  "recommendation": {
    "text": "No se dispone de pronóstico meteorológico para esta fecha. La afluencia estimada es Alta, pero la conveniencia no puede calcularse. Consulte fuentes meteorológicas antes de planificar.",
    "template_key": "SIN_DATOS_METEOROLOGICOS"
  },
  "active_factors": ["Es fin de semana", "El mes presenta afluencia histórica alta"],
  "is_degraded": true,
  "degraded_reason": "WEATHER_UNAVAILABLE"
}
```

---

**Respuesta 404 — destino no encontrado:**

```json
{
  "error": "DESTINATION_NOT_FOUND",
  "message": "El destino solicitado no existe o no está disponible.",
  "detail": null
}
```

**Respuesta 503 — servicio meteorológico no disponible (pero continúa degradado):**

> El STP **no** devuelve 503 si el SMS falla. En ese caso, devuelve 200 con los días afectados marcados como `is_degraded: true` y `degraded_reason: "WEATHER_UNAVAILABLE"`. Solo devuelve 503 si el propio STP no puede calcular ni siquiera la afluencia.

---

### 3.3. Listar destinos disponibles

```
GET /api/v1/destinations
```

**Respuesta 200:**

```json
{
  "destinations": [
    {
      "slug": "cueva-lechuzas",
      "name": "Cueva de las Lechuzas",
      "is_active": true
    }
  ]
}
```

---

### 3.4. Endpoint de salud extendido (para monitoreo)

```
GET /api/v1/health/full
```

**Respuesta 200:**

```json
{
  "status": "ok",
  "database": "ok",
  "weather_service": "ok",
  "engine_version": "ME-1.0",
  "generator_version": "SG-1.0"
}
```

Posibles valores por componente: `"ok"`, `"degraded"`, `"error"`.

---

## 4. API interna del SMS

Este contrato es exclusivamente entre STP y SMS. No es accesible desde el exterior.

### 4.1. Endpoint de salud

```
GET /health
```

**Respuesta 200:**

```json
{
  "status": "ok",
  "service": "sms",
  "cache_status": "HIT",
  "cache_valid_until": "2026-10-06T16:30:00-05:00"
}
```

`cache_status` puede ser `"HIT"` (se usó caché) o `"MISS"` (se llamó a Open-Meteo).

---

### 4.2. Obtener pronóstico normalizado

```
GET /internal/weather
```

**Parámetros de consulta:**

| Parámetro | Tipo | Requerido | Descripción |
|---|---|---|---|
| `latitude` | `float` | Sí | Latitud del destino |
| `longitude` | `float` | Sí | Longitud del destino |
| `days` | `integer` | No (default 7) | Número de días a solicitar |
| `timezone` | `string` | No (default `America/Lima`) | Zona horaria |

**Respuesta 200:**

```json
{
  "fetched_at": "2026-10-06T10:30:00-05:00",
  "valid_until": "2026-10-06T13:30:00-05:00",
  "provider": "open-meteo",
  "days": [
    {
      "date": "2026-10-06",
      "lluvia_mm": 1.2,
      "prob_lluvia_pct": 15,
      "horas_lluvia": 0.5,
      "codigo_wmo": 2,
      "temp_max_c": 28.0,
      "temp_min_c": 20.0,
      "sensacion_max_c": 30.0,
      "viento_max_kmh": 12.0,
      "uv_max": 7.0,
      "horas_sol_s": 22320.0
    }
  ]
}
```

**Respuesta 503 — Open-Meteo no disponible:**

```json
{
  "error": "WEATHER_PROVIDER_UNAVAILABLE",
  "message": "No se pudo obtener el pronóstico meteorológico del proveedor externo.",
  "detail": "Connection timeout after 10s"
}
```

> El STP debe manejar el 503 del SMS con gracia: continuar el cálculo marcando los días como `is_degraded: true`.

---

## 5. Enumeraciones de la API

### 5.1. `nivel_afluencia`

| Valor | Etiqueta en español |
|---|---|
| `BAJA` | Baja |
| `MEDIA` | Media |
| `ALTA` | Alta |

### 5.2. `categoria_recomendacion`

| Valor | Etiqueta en español | Color UI |
|---|---|---|
| `RECOMENDADO` | Recomendado | Verde |
| `PRECAUCION` | Visitable con precaución | Ámbar |
| `NO_RECOMENDADO` | No recomendado | Rojo |
| `SIN_DATOS` | Sin datos meteorológicos | Gris |

### 5.3. `best_label`

| Valor | Significado |
|---|---|
| `MEJOR_OPCION` | Mejor día recomendable de la semana |
| `MEJOR_ALTERNATIVA` | Mejor día cuando ninguno es recomendable |
| `MENOR_AFLUENCIA` | Mejor día cuando no hay datos meteorológicos |

### 5.4. `degraded_reason`

| Valor | Causa |
|---|---|
| `WEATHER_UNAVAILABLE` | El SMS no pudo obtener pronóstico |
| `NO_HISTORICAL_DATA` | No hay datos históricos para el mes evaluado |
| `ZERO_REPORTED_MONTH` | El mes tiene cero visitantes reportados oficialmente |

---

## 6. Manejo de errores general

Todos los errores de la API siguen esta estructura:

```json
{
  "error": "ERROR_CODE",
  "message": "Descripción legible en español.",
  "detail": "Información técnica opcional (solo en desarrollo)"
}
```

| Código HTTP | Cuando se usa |
|---|---|
| `200` | Respuesta exitosa, incluso si hay días degradados |
| `400` | Parámetros inválidos en la solicitud |
| `404` | Recurso no encontrado (destino) |
| `422` | Error de validación de Pydantic |
| `500` | Error interno no controlado |
| `503` | El servicio no puede responder en absoluto |

---

## 7. Diseño funcional de la interfaz

### 7.1. Estructura general del dashboard

```
┌──────────────────────────────────────────────────────────────────┐
│  CABECERA                                                        │
│  [Ícono destino] Cueva de las Lechuzas                          │
│  Parque Nacional Tingo María · Huánuco, Perú                    │
│  Pronóstico actualizado: martes 6 de octubre de 2026, 10:30 am  │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  SELECTOR DE SIETE DÍAS (tarjetas horizontales o carrusel)       │
│                                                                  │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ...    │
│  │ Mar 6  │ │ Mié 7  │ │ Jue 8  │ │ Vie 9  │ │ Sáb 10 │        │
│  │ HOY    │ │★MEJOR  │ │        │ │        │ │        │        │
│  │ 🟢 88  │ │ 🟢 91  │ │ 🟡 55  │ │ 🟡 62  │ │ 🔴 35  │        │
│  │ Aflu:28│ │ Aflu:22│ │ Aflu:45│ │ Aflu:51│ │ Aflu:78│        │
│  │ ⛅ 28° │ │ ☀ 29°  │ │ 🌧 24° │ │ 🌧 25° │ │ ⛅ 27° │        │
│  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │
└──────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────┐
│  PANEL DETALLE (día seleccionado)                                │
│                                                                  │
│  Martes, 6 de octubre de 2026                                   │
│                                                                  │
│  ┌─────────────────────┐  ┌─────────────────────────────────┐   │
│  │  AFLUENCIA          │  │  CONVENIENCIA                   │   │
│  │  28 / 100           │  │  88 / 100                       │   │
│  │  ● Baja             │  │  ✓ Recomendado                  │   │
│  └─────────────────────┘  └─────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  CLIMA                                                   │   │
│  │  ⛅ Parcialmente nublado                                  │   │
│  │  🌡 Máx 28°C · Mín 20°C · Sensación 30°C               │   │
│  │  🌧 1.2 mm · 15% prob. lluvia · 0.5 h lluvia            │   │
│  │  💨 Viento máx 12 km/h · ☀ UV 7 · 🌞 6.2 h de sol     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  RECOMENDACIÓN                                           │   │
│  │  "Condiciones aceptables para la visita. Se espera una   │   │
│  │   concurrencia moderada con buen clima. Verifique         │   │
│  │   horarios en los canales oficiales."                    │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  FACTORES PRINCIPALES                                    │   │
│  │  • El mes presenta afluencia histórica baja              │   │
│  │  • Es martes ordinario                                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  INFORMACIÓN OFICIAL                                     │   │
│  │  [→ Información del parque]  [→ Comprar entrada]        │   │
│  │  [→ Cómo llegar]                                         │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ⚠ ADVERTENCIA METODOLÓGICA                              │   │
│  │  La puntuación de afluencia es una estimación académica  │   │
│  │  calculada mediante datos mensuales oficiales...         │   │
│  │  [Leer más ▾]                                            │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────────────┘
```

---

### 7.2. Tarjeta diaria — contenido mínimo

| Elemento | Descripción |
|---|---|
| Día de la semana y fecha | p.ej. "Mar 6" |
| Etiqueta HOY | Solo si es el día actual |
| Etiqueta MEJOR / ALTERNATIVA | Si aplica |
| Puntuación de conveniencia | Número con color de fondo o borde (verde/ámbar/rojo) |
| Nivel de afluencia | Número y nivel textual |
| Icono meteorológico | Representación visual del código WMO |
| Temperatura máxima | En grados Celsius |
| Nota de calendario | Si es feriado, puente o periodo especial |

---

### 7.3. Reglas visuales de las tarjetas

1. El color de fondo o borde de la tarjeta corresponde a la **categoría de conveniencia**, no al nivel de afluencia.
2. La tarjeta seleccionada tiene un indicador de selección independiente del color de recomendación (p.ej. borde más grueso o sombra).
3. La etiqueta de "Mejor opción" o "Mejor alternativa" es visible en la tarjeta sin necesidad de seleccionarla.
4. El color nunca es el único medio de comunicar la recomendación; el texto de categoría es siempre visible.
5. En móvil, las tarjetas se muestran en una fila horizontal con desplazamiento lateral (scroll horizontal controlado).

---

### 7.4. Estados de la interfaz

#### Estado 1: Carga inicial

```
┌──────────────────────────────────────┐
│  Cueva de las Lechuzas               │
│  Cargando pronóstico...              │
│                                      │
│  [████████████████] skeleton cards  │
│                                      │
│  [████████████████] skeleton detail │
└──────────────────────────────────────┘
```

- Se muestran tarjetas skeleton (placeholder animado) mientras la API responde.
- No se muestra contenido parcial mezclado con skeleton.

---

#### Estado 2: Pronóstico completo (estado normal)

Ver wireframe principal de la sección 7.1.

---

#### Estado 3: Días con meteorología no disponible

- Las tarjetas afectadas muestran un ícono gris neutro en lugar del color verde/ámbar/rojo.
- Se muestra la etiqueta textual "Sin datos meteorológicos" dentro de la tarjeta.
- El panel detalle muestra la sección de clima como no disponible con el mensaje de la plantilla `SIN_DATOS_METEOROLOGICOS`.
- Los demás días con datos continúan funcionando con normalidad.

---

#### Estado 4: Ningún día recomendable

```
┌──────────────────────────────────────────────────────────────┐
│  ⚠ Esta semana ningún día presenta condiciones               │
│  completamente recomendables.                                │
│  La mejor alternativa disponible es el miércoles 8.         │
└──────────────────────────────────────────────────────────────┘
```

- El banner se muestra sobre el selector de días.
- La tarjeta de mejor alternativa tiene la etiqueta "Mejor alternativa".
- Las tarjetas no cambian de categoría; siguen mostrando el color real de su conveniencia.

---

#### Estado 5: Error de carga total

```
┌──────────────────────────────────────────────────────────────┐
│  No se pudo cargar el pronóstico.                            │
│  Puede deberse a una conexión inestable.                     │
│  [Reintentar]                                                │
└──────────────────────────────────────────────────────────────┘
```

- Se muestra cuando la API del STP devuelve un error 5xx o hay un timeout de red.
- Se ofrece un botón de reintento que vuelve a llamar al endpoint.

---

### 7.5. Diseño responsivo

| Breakpoint | Comportamiento |
|---|---|
| Escritorio (≥ 1024 px) | Tarjetas en fila horizontal visible completa; panel detalle a la derecha o debajo |
| Tablet (768–1023 px) | Tarjetas en fila con scroll horizontal; panel detalle debajo |
| Móvil (< 768 px) | Tarjetas en carrusel horizontal con scroll; panel detalle debajo en pantalla completa |

**Requisitos mínimos en móvil:**
- Sin scroll horizontal general de página.
- Controles con área táctil mínima de 44×44 px.
- Texto de categorías y puntuaciones legibles sin zoom.

---

### 7.6. Accesibilidad básica

1. Las tarjetas son elementos `button` o tienen `role="button"` con `aria-label` descriptivo.
2. La tarjeta seleccionada tiene `aria-pressed="true"` o `aria-selected="true"`.
3. Los colores van acompañados de texto: nunca color solo.
4. Contraste mínimo de 4.5:1 entre texto y fondo (WCAG AA).
5. El orden del DOM permite navegación con teclado en el mismo orden visual.

---

### 7.7. Textos fijos de la interfaz

| Elemento | Texto |
|---|---|
| Título de la advertencia | "Aviso metodológico" |
| Etiqueta mejor opción | "Mejor opción" |
| Etiqueta mejor alternativa | "Mejor alternativa" |
| Etiqueta menor afluencia | "Menor afluencia estimada" |
| Etiqueta hoy | "Hoy" |
| Enlace info oficial | "Información del parque" |
| Enlace entradas | "Comprar entrada" |
| Enlace cómo llegar | "Cómo llegar" |
| Cargando | "Cargando pronóstico…" |
| Error de carga | "No se pudo cargar el pronóstico." |
| Botón reintento | "Reintentar" |
| Sin meteorología | "Sin datos meteorológicos" |

---

## 8. Criterios de aceptación de los contratos

Los contratos se consideran correctamente implementados cuando:

1. `GET /api/v1/forecast/cueva-lechuzas` devuelve exactamente 7 elementos en `days`.
2. El primer elemento tiene `is_today: true` cuando la fecha coincide con hoy en Lima.
3. Exactamente un elemento tiene `is_best: true` y un `best_label` no nulo.
4. Los campos `score`, `level` y `category` no son nulos para días con datos completos.
5. Los días sin meteorología tienen `weather: null`, `convenience.score: null` y `is_degraded: true`.
6. El SMS devuelve los campos normalizados (`lluvia_mm`, `prob_lluvia_pct`, etc.) con los nombres definidos en el `03`.
7. Un fallo del SMS no provoca un 5xx en el STP; los días afectados se marcan como degradados.
8. Todos los textos visibles de la interfaz están en español.
9. El frontend no renderiza ningún dato de una fecha que no esté en el array `days` recibido.
10. En móvil, la interfaz funciona sin scroll horizontal general de página.

## 9. Precisiones de contrato — versión 0.2 (2026-10-06)

- Se conserva la clave pública `affuence` por compatibilidad con este documento.
- `weather` incluye además `apparent_temp_max_c` y `rain_hours`, mapeados desde
  `sensacion_max_c` y `horas_lluvia`. El STP obtiene condition_label del adaptador SMS;
  no interpreta directamente la respuesta Open-Meteo.
- El SMS agrega `raw_response` (objeto original) a la raíz y `condition_label` a cada
  día. STP persiste raw_response en weather_snapshots.raw_response_json.
  Un día inválido se omite; si ninguno es válido, SMS responde 503.
- El SMS acepta days entre 1 y 7; timezone es America/Lima en este MVP.
  /health no dispara llamadas externas. Caché vacía: MISS y cache_valid_until=null.
- `from_date` se conserva para compatibilidad, pero solo se acepta hoy en Lima;
  cualquier otra fecha válida devuelve 400 INVALID_DATE_RANGE. Formato inválido: 422.
- Sin historial de una fecha: affuence.score/level/level_label nulos,
  convenience.score nulo, category=SIN_DATOS, category_label="Datos insuficientes",
  is_degraded=true, degraded_reason=NO_HISTORICAL_DATA. El clima válido puede mostrarse.
  Sin afluencia calculable en ninguno de los siete días: 503 ESTIMATION_UNAVAILABLE,
  mensaje "No hay datos suficientes para generar el pronóstico.". Con al menos
  una afluencia válida: 200 y exactamente un mejor día según docs/03 §16.
- `weather_fetched_at` es nullable. El SMS sin datos usa 503
  WEATHER_PROVIDER_UNAVAILABLE y detail=null en producción.
- /api/v1/health/full: 503 si la BD no está disponible; 200 degraded si falta
  inicialización del motor o SMS. No expone credenciales ni excepciones internas.
- Un ZERO_REPORTED conserva score=0; is_degraded=true y motivo ZERO_REPORTED_MONTH.
- Aviso metodológico fijo: "La afluencia es una estimación académica derivada de
  registros mensuales oficiales y una distribución diaria sintética con factores
  de calendario. El pronóstico meteorológico se utiliza para calcular la
  conveniencia de visita. No representa ocupación real ni conteo en tiempo real.
  Antes de visitar, consulte horarios, entradas y restricciones en los canales
  oficiales de SERNANP."
- El ejemplo de score 28 utiliza RECOMENDADO_BAJA_FAVORABLE y su plantilla en 03;
  octubre no activa el factor de temporada baja. El ejemplo anterior era ilustrativo.
- Enlaces semilla: https://visitaareasnaturales.sernanp.gob.pe/anps/parque-nacional-de-tingo-maria/
  y https://visitaareasnaturales.sernanp.gob.pe/tuticket/ . Cómo llegar apunta a la
  misma página oficial, donde se publican los accesos. Se abren con noopener noreferrer.
