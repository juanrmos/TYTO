# Especificación del motor de estimación

## Aplicación web para la estimación de afluencia turística en la Cueva de las Lechuzas

**Versión:** 0.1  
**Estado:** Especificación aprobada  
**Documentos relacionados:**

- `01-definicion-y-alcance-del-proyecto.md`
- `02-requisitos-del-sistema.md`

---

## 1. Propósito

Este documento define con precisión matemática todas las reglas, factores, fórmulas, umbrales y casos de prueba que el motor de estimación debe implementar.

Los agentes de desarrollo deberán leer este documento como fuente de verdad para la lógica de cálculo. Ninguna fórmula, umbral o regla de desempate podrá ser inventada o modificada durante la implementación sin actualizar primero este documento.

---

## 2. Entradas del motor

Para evaluar una fecha concreta el motor requiere:

| Entrada | Fuente | Obligatoria |
|---|---|---|
| Fecha a evaluar (`date`) | Solicitud del sistema | Sí |
| Registros mensuales oficiales (2022–2026) | Base de datos | Sí |
| Calendario turístico local | Configuración versionada | Sí |
| Variables meteorológicas del proveedor | API Open-Meteo | Para conveniencia completa |

---

## 3. Referencia mensual

### 3.1. Objetivo

El motor necesita saber cuántos visitantes se espera que lleguen en el mes que contiene la fecha evaluada. A esta cantidad la llamamos **referencia mensual** (`ref_mensual`).

### 3.2. Casos de disponibilidad

| Caso | Condición | Acción |
|---|---|---|
| Mes actual disponible | Existe registro oficial `AVAILABLE` para año y mes de la fecha | Usar ese valor directamente |
| Mes actual no publicado | No existe registro para ese mes y año | Calcular mediana histórica (sección 3.3) |
| Mes actual incompleto | Estado `INCOMPLETE` | Usar mediana histórica |
| Mes con cero reportado | Estado `ZERO_REPORTED` | Usar cero como referencia válida |

### 3.3. Cálculo de la mediana histórica

Cuando el mes de la fecha evaluada no tiene registro oficial del año en curso:

1. Recopilar todos los valores `AVAILABLE` del mismo mes calendario en el periodo 2022–2025.
2. Ordenar los valores de menor a mayor.
3. Calcular la mediana:
   - Si hay cantidad impar de valores → valor central.
   - Si hay cantidad par de valores → promedio de los dos valores centrales, redondeado al entero más cercano.
4. Si no existe ningún registro del mismo mes en todo el periodo regular → `ref_mensual = null` → el motor produce afluencia degradada (ver sección 9.1).

**Ejemplo:**

```
Mes evaluado: octubre de 2026 (sin registro publicado)
Valores disponibles de octubre:
  2022: 1 840
  2023: 2 105
  2024: 1 990
  2025: 2 230

Ordenados: [1 840, 1 990, 2 105, 2 230]
Mediana = (1 990 + 2 105) / 2 = 2 047  →  ref_mensual = 2 047
```

---

## 4. Distribución diaria sintética

### 4.1. Principio de conservación mensual

La distribución debe cumplir estrictamente:

```
Σ visitantes_dia(d) para todo d en el mes = ref_mensual
```

### 4.2. Peso diario base

Cada día del mes recibe un peso según su tipo:

```
peso_base(d) = factor_semana(d) × factor_tipo_fecha(d) × factor_temporada(mes)
```

### 4.3. Factor por día de la semana (`factor_semana`)

| Día | Factor |
|---|---|
| Lunes | 0.70 |
| Martes | 0.70 |
| Miércoles | 0.75 |
| Jueves | 0.80 |
| Viernes | 1.00 |
| Sábado | 1.50 |
| Domingo | 1.35 |

**Justificación:** El turismo de naturaleza en Perú concentra mayor afluencia en fines de semana. El viernes presenta ya un incremento por inicio de fin de semana típico.

### 4.4. Factor por tipo de fecha (`factor_tipo_fecha`)

Los tipos se evalúan en orden de precedencia (el primero que aplique gana):

| Precedencia | Tipo | Factor |
|---|---|---|
| 1 | Feriado en fin de semana largo (≥ 3 días consecutivos no laborables) | 1.80 |
| 2 | Feriado aislado (día laborable declarado feriado) | 1.40 |
| 3 | Puente oficial (día entre feriado y fin de semana) | 1.30 |
| 4 | Periodo especial turístico (Semana Santa, vacaciones escolares, etc.) | 1.20 |
| 5 | Día ordinario (laborable o fin de semana sin excepción) | 1.00 |

> Los tipos 1–4 se determinan exclusivamente desde el calendario turístico local versionado. No se infieren automáticamente de la fecha.

### 4.5. Factor de temporada (`factor_temporada`)

| Mes | Factor | Referencia |
|---|---|---|
| Enero | 1.10 | Vacaciones de verano escolar peruano |
| Febrero | 1.05 | Continuación de vacaciones |
| Marzo | 1.00 | Retorno escolar |
| Abril | 1.15 | Semana Santa (amplificado por calendario) |
| Mayo | 0.90 | Mes bajo típico |
| Junio | 0.85 | Mes bajo |
| Julio | 1.25 | Vacaciones de invierno escolar peruano |
| Agosto | 1.20 | Continuación de vacaciones de invierno |
| Septiembre | 0.90 | Retorno escolar |
| Octubre | 0.95 | Inicio de lluvias, demanda moderada |
| Noviembre | 0.90 | Temporada lluviosa |
| Diciembre | 1.10 | Navidad y fin de año |

> Estos factores son ajustables mediante configuración sin reescribir el motor.

### 4.6. Variación sintética controlada

Para evitar que todos los lunes del mes sean idénticos se aplica una variación pseudoaleatoria:

```
variacion(d) = 1.0 + (pseudoaleatorio(semilla, d) × 0.06 − 0.03)
```

- El rango de variación es ±3 % del peso base.
- La semilla de reproducibilidad es: `SHA-256(año || mes || version_generador)` → primeros 8 caracteres → convertido a entero.
- `pseudoaleatorio` usa LCG (Lehmer) con la semilla anterior y el número ordinal del día en el mes como offset.
- El peso no puede caer por debajo de 0.01.

```
peso_final(d) = max(peso_base(d) × variacion(d), 0.01)
```

### 4.7. Cálculo de visitantes diarios

```
visitantes_bruto(d) = ref_mensual × peso_final(d) / Σ peso_final(d) para todo d en el mes
```

### 4.8. Corrección de redondeo

```
visitantes_dia(d) = round(visitantes_bruto(d))

suma_redondeada = Σ visitantes_dia(d)
diferencia = ref_mensual − suma_redondeada

# Agregar `diferencia` (puede ser positiva o negativa) al día con mayor peso_final(d)
```

**Garantía:** `Σ visitantes_dia(d) = ref_mensual` siempre.

---

## 5. Normalización de afluencia (0–100)

### 5.1. Referencia de normalización

La referencia para escalar es el **percentil 95 de todos los valores diarios sintéticos** del periodo regular (2022–agosto 2026). Este valor se denomina `p95_global`.

- Se calcula una sola vez al cargar o regenerar los datos sintéticos del periodo regular.
- Se almacena junto con la versión del generador.

### 5.2. Fórmula

```
score_afluencia(d) = min(round(visitantes_dia(d) / p95_global × 100), 100)
```

Resultado siempre en [0, 100].

### 5.3. Umbrales de nivel de afluencia

| Rango | Nivel |
|---|---|
| 0 – 33 | Baja |
| 34 – 66 | Media |
| 67 – 100 | Alta |

> El color de la UI proviene de la **recomendación de conveniencia**, no del nivel de afluencia (RN-09 del `02`).

---

## 6. Variables meteorológicas

### 6.1. Variables de Open-Meteo (endpoint `/v1/forecast`, variables diarias)

| Variable Open-Meteo | Nombre interno | Uso |
|---|---|---|
| `precipitation_sum` | `lluvia_mm` | Penalización de conveniencia |
| `precipitation_probability_max` | `prob_lluvia_pct` | Penalización de conveniencia |
| `precipitation_hours` | `horas_lluvia` | Penalización de conveniencia |
| `weather_code` | `codigo_wmo` | Condición general y penalización |
| `temperature_2m_max` | `temp_max_c` | Informativo y penalización extrema |
| `temperature_2m_min` | `temp_min_c` | Informativo |
| `apparent_temperature_max` | `sensacion_max_c` | Penalización por calor |
| `wind_speed_10m_max` | `viento_max_kmh` | Penalización de conveniencia |
| `uv_index_max` | `uv_max` | Penalización de conveniencia |
| `sunshine_duration` | `horas_sol_s` | Bonus de conveniencia |

**Coordenadas del destino:**

```
latitud:  -9.3008
longitud: -76.0026
timezone: America/Lima
```

### 6.2. Clasificación del código WMO

| Rango de código WMO | Condición | Penalización |
|---|---|---|
| 0 – 1 | Despejado | 0 |
| 2 – 3 | Parcialmente nublado | 0 |
| 45 – 48 | Niebla | −5 |
| 51 – 57 | Llovizna | −10 |
| 61 – 65 | Lluvia moderada a fuerte | −20 |
| 80 – 82 | Chubascos | −15 |
| 95 | Tormenta eléctrica | −30 |
| 96 – 99 | Tormenta con granizo | −35 |

---

## 7. Puntuación de conveniencia (0–100)

### 7.1. Fórmula

```
score_conveniencia = 100
  − penalizacion_lluvia(d)
  − penalizacion_viento(d)
  − penalizacion_uv(d)
  − penalizacion_calor(d)
  + bonus_sol(d)
  − penalizacion_wmo(d)
  − penalizacion_afluencia(d)

score_conveniencia = max(min(score_conveniencia, 100), 0)
```

### 7.2. Penalización por lluvia (máx. −40)

```
penalizacion_lluvia =
    min(lluvia_mm / 2.0, 20)         # hasta −20
  + min(prob_lluvia_pct / 5.0, 10)  # hasta −10
  + min(horas_lluvia × 2.0, 10)     # hasta −10
```

### 7.3. Penalización por viento (máx. −15)

```
penalizacion_viento =
    0                               si viento_max_kmh < 20
    (viento_max_kmh − 20) × 0.5    si 20 ≤ viento_max_kmh < 50
    15                              si viento_max_kmh ≥ 50
```

### 7.4. Penalización por UV (máx. −10)

```
penalizacion_uv =
    0     si uv_max ≤ 6
    5     si 7 ≤ uv_max ≤ 9
    10    si uv_max ≥ 10
```

### 7.5. Penalización por calor extremo (máx. −10)

```
penalizacion_calor =
    0     si sensacion_max_c ≤ 32
    5     si 32 < sensacion_max_c ≤ 36
    10    si sensacion_max_c > 36
```

### 7.6. Bonus por horas de sol (máx. +5)

```
bonus_sol = min(horas_sol_s / 3600 × 1.0, 5)
```

### 7.7. Penalización por código WMO

Ver tabla sección 6.2. Se aplica directamente como penalización.

### 7.8. Penalización por afluencia alta (máx. −10)

```
penalizacion_afluencia =
    0     si score_afluencia ≤ 50
    5     si 51 ≤ score_afluencia ≤ 75
    10    si score_afluencia > 75
```

### 7.9. Conveniencia sin datos meteorológicos

Si el pronóstico no está disponible:

- `score_conveniencia = null`
- Categoría: `SIN_DATOS_METEOROLOGICOS`
- La tarjeta no recibe color (gris neutro)
- Se muestra mensaje de datos insuficientes

---

## 8. Clasificación de la recomendación

### 8.1. Categorías y colores

| Rango de score_conveniencia | Categoría | Color UI |
|---|---|---|
| 70 – 100 | Recomendado | Verde |
| 40 – 69 | Visitable con precaución | Ámbar |
| 0 – 39 | No recomendado | Rojo |
| null | Sin datos meteorológicos | Gris |

### 8.2. Condición mínima para "Recomendado"

Un día clasifica como **Recomendado** solo si cumple **todas**:

1. `score_conveniencia ≥ 70`
2. `prob_lluvia_pct < 70`
3. `codigo_wmo` no está en rango 95–99
4. El pronóstico meteorológico está disponible

Si alguna condición falla pero `score_conveniencia ≥ 70`, el día baja a `Visitable con precaución`.

---

## 9. Selección de la mejor opción

### 9.1. Algoritmo

```
1. Filtrar días con categoría "Recomendado".
2. Si hay al menos uno:
   → Ordenar: score_conveniencia DESC, score_afluencia ASC, fecha ASC
   → El primero = "Mejor opción"
3. Si ninguno es "Recomendado":
   → Tomar días con score_conveniencia no nulo
   → Aplicar mismo orden
   → El primero = "Mejor alternativa disponible"
   → Mostrar advertencia de semana desfavorable
4. Si todos tienen conveniencia nula:
   → Seleccionar el día con menor score_afluencia
   → Etiqueta: "Menor afluencia estimada"
   → Mostrar advertencia de ausencia de datos meteorológicos
```

### 9.2. Regla de desempate formal

| Prioridad | Criterio | Dirección |
|---|---|---|
| 1 | `score_conveniencia` | Mayor primero |
| 2 | `score_afluencia` | Menor primero |
| 3 | `fecha` | Más cercana primero |

> Diferencia ≤ 1 punto en conveniencia se considera empate a efectos del desempate por afluencia.

---

## 10. Plantillas de recomendación textual

Las recomendaciones se generan por selección de plantilla. No se genera texto libre en tiempo de ejecución.

### 10.1. Recomendado

| Condición | Texto |
|---|---|
| Afluencia baja + clima favorable | "Buen momento para visitar. Se espera poca concurrencia y condiciones meteorológicas favorables. Consulte horarios y disponibilidad de entradas en los canales oficiales." |
| Afluencia media + clima favorable | "Condiciones aceptables para la visita. Se espera una concurrencia moderada con buen clima. Verifique horarios en los canales oficiales." |
| Afluencia alta + clima favorable | "El clima es favorable, aunque se espera alta concurrencia. Planifique con anticipación y confirme disponibilidad de entradas." |

### 10.2. Visitable con precaución

| Condición | Texto |
|---|---|
| Lluvia probable (`prob_lluvia_pct ≥ 40`) | "Se esperan lluvias. Puede visitarse con precaución llevando equipo adecuado. Consulte las condiciones antes de salir." |
| Afluencia alta + clima moderado | "Alta concurrencia esperada. Las condiciones meteorológicas son aceptables, pero planifique con tiempo para evitar esperas." |
| Condiciones mixtas | "Las condiciones presentan factores a considerar. Revise el pronóstico actualizado y consulte los canales oficiales antes de la visita." |

### 10.3. No recomendado

| Condición | Texto |
|---|---|
| Lluvia intensa (`lluvia_mm ≥ 15`) | "No se recomienda la visita por condiciones meteorológicas adversas. Considere otro día del horizonte disponible." |
| Tormenta eléctrica (`codigo_wmo ≥ 95`) | "Se esperan tormentas eléctricas. No se recomienda la visita por razones de seguridad. Consulte los próximos días." |
| Condiciones desfavorables generales | "Las condiciones del día no son favorables para la visita. Se sugiere evaluar los demás días disponibles." |

### 10.4. Sin datos meteorológicos

> "No se dispone de pronóstico meteorológico para esta fecha. La afluencia estimada es [NIVEL], pero la conveniencia no puede calcularse. Consulte fuentes meteorológicas antes de planificar."

### 10.5. Semana completamente desfavorable

> "Ninguno de los próximos siete días presenta condiciones completamente recomendables. La mejor alternativa disponible es [DÍA], donde se espera menor concurrencia y condiciones relativamente mejores."

---

## 11. Factores principales a mostrar

El motor produce una lista de factores activos (máximo 4, mínimo 1) ordenados por relevancia:

| Condición activa | Texto del factor |
|---|---|
| `factor_tipo_fecha` = feriado largo | "Es feriado largo" |
| `factor_tipo_fecha` = feriado | "Es feriado" |
| `factor_tipo_fecha` = puente | "Es día puente" |
| `factor_tipo_fecha` = periodo especial | "Periodo turístico especial" |
| Día = sábado o domingo | "Es fin de semana" |
| `factor_temporada` ≥ 1.15 | "El mes presenta afluencia histórica alta" |
| `factor_temporada` ≤ 0.90 | "El mes presenta afluencia histórica baja" |
| `prob_lluvia_pct` ≥ 60 | "Alta probabilidad de lluvia" |
| `lluvia_mm` ≥ 10 | "Se esperan lluvias significativas" |
| `codigo_wmo` ≥ 95 | "Se esperan tormentas eléctricas" |
| `viento_max_kmh` ≥ 40 | "Vientos fuertes esperados" |
| `uv_max` ≥ 10 | "Índice UV muy alto" |
| `score_afluencia` ≤ 25 | "Afluencia histórica baja para esta fecha" |
| `score_afluencia` ≥ 75 | "Afluencia histórica alta para esta fecha" |

---

## 12. Versiones del motor y el generador

### 12.1. Versión del generador sintético

Formato: `SG-MAJOR.MINOR`

- `MAJOR` cambia cuando cambian factores base (día de semana, temporada, tipo de fecha).
- `MINOR` cambia cuando solo cambia la semilla u otros parámetros menores.
- Versión inicial: `SG-1.0`

### 12.2. Versión del motor de estimación

Formato: `ME-MAJOR.MINOR`

- `MAJOR` cambia cuando cambian fórmulas, umbrales o variables meteorológicas.
- `MINOR` cambia cuando se ajustan pesos sin cambiar la estructura.
- Versión inicial: `ME-1.0`

Cada predicción almacenada debe registrar `version_generador` y `version_motor`.

---

## 13. Casos de prueba del motor

### CP-01. Día laborable ordinario con clima favorable

**Entrada:**
- Miércoles, mayo (temporada baja, `factor_temporada = 0.90`)
- `lluvia_mm = 0`, `prob_lluvia_pct = 5`, `codigo_wmo = 1`
- `viento_max_kmh = 10`, `uv_max = 6`, `sensacion_max_c = 27`
- `score_afluencia` ≈ 20

**Esperado:**
- `score_conveniencia` ≥ 85
- Categoría: `Recomendado`
- Factores incluyen: "El mes presenta afluencia histórica baja"

---

### CP-02. Fin de semana con clima favorable y afluencia alta

**Entrada:**
- Sábado, julio (temporada alta, `factor_temporada = 1.25`)
- `lluvia_mm = 2`, `prob_lluvia_pct = 20`, `codigo_wmo = 2`
- `viento_max_kmh = 8`, `uv_max = 8`, `sensacion_max_c = 28`
- `score_afluencia` ≈ 82

**Esperado:**
- `penalizacion_afluencia = 10`
- `score_conveniencia` en rango 65–80
- Factores incluyen: "Es fin de semana", "Afluencia histórica alta para esta fecha"

---

### CP-03. Feriado con lluvia intensa

**Entrada:**
- Feriado aislado (lunes), abril
- `lluvia_mm = 25`, `prob_lluvia_pct = 90`, `horas_lluvia = 6`
- `codigo_wmo = 63`, `viento_max_kmh = 15`
- `score_afluencia` ≥ 85

**Esperado:**
- `penalizacion_lluvia` = min(12.5, 20) + min(18, 10) + min(12, 10) = 12.5 + 10 + 10 = 32.5
- `penalizacion_wmo` = 20
- `score_conveniencia` ≤ 35
- Categoría: `No recomendado`
- Factores incluyen: "Es feriado", "Alta probabilidad de lluvia", "Se esperan lluvias significativas"

---

### CP-04. Baja afluencia con tormenta eléctrica

**Entrada:**
- Martes ordinario, junio
- `codigo_wmo = 95`, `lluvia_mm = 30`, `prob_lluvia_pct = 95`
- `score_afluencia` ≤ 20

**Esperado:**
- `penalizacion_wmo = 30`
- `score_conveniencia` ≤ 20
- Categoría: `No recomendado`
- `penalizacion_afluencia = 0` (afluencia baja no penaliza)
- Factores incluyen: "Se esperan tormentas eléctricas"

---

### CP-05. Semana sin días recomendables

**Entrada:**
- Los 7 días tienen `score_conveniencia` entre 30 y 55
- Ninguno alcanza categoría `Recomendado`

**Esperado:**
- Ningún día tiene etiqueta "Mejor opción"
- El día con mayor `score_conveniencia` tiene etiqueta "Mejor alternativa disponible"
- Se muestra la advertencia de semana desfavorable

---

### CP-06. Desempate por afluencia

**Entrada:**
- Miércoles: `score_conveniencia = 72`, `score_afluencia = 35`
- Jueves: `score_conveniencia = 72`, `score_afluencia = 28`

**Esperado:**
- El jueves es "Mejor opción" (menor afluencia)

---

### CP-07. Desempate por fecha

**Entrada:**
- Viernes: `score_conveniencia = 71`, `score_afluencia = 40`
- Sábado: `score_conveniencia = 71`, `score_afluencia = 40`

**Esperado:**
- El viernes es "Mejor opción" (fecha más cercana)

---

### CP-08. Conservación mensual

**Entrada:**
- `ref_mensual = 2 047`, mes de octubre (31 días), `version_generador = SG-1.0`

**Esperado:**
- `Σ visitantes_dia(d)` = exactamente 2 047
- Ningún día tiene valor negativo
- El día de mayor `peso_final` absorbe la corrección de redondeo

---

### CP-09. Afluencia sin historial del mes

**Entrada:**
- Fecha en un mes sin ningún registro en el periodo 2022–2025

**Esperado:**
- `ref_mensual = null`
- `score_afluencia = null`
- La predicción se almacena con estado degradado
- La interfaz muestra mensaje de datos insuficientes

---

### CP-10. Reproducibilidad del generador

**Entrada:**
- Misma `ref_mensual`, mismo mes y año, misma `version_generador`

**Esperado:**
- `visitantes_dia(d)` es idéntico en dos ejecuciones separadas
- La semilla produce el mismo ruido en el mismo orden

---

## 14. Criterios de aceptación del motor

El motor se considera correctamente implementado cuando:

1. Los casos CP-01 al CP-10 pasan de forma automatizada.
2. La conservación mensual se verifica para todos los meses del periodo 2022–agosto 2026.
3. El percentil 95 global se calcula y almacena junto con la versión del generador.
4. Los umbrales de afluencia (0–33, 34–66, 67–100) producen las categorías correctas.
5. Los umbrales de conveniencia (0–39, 40–69, 70–100) producen las categorías correctas.
6. La condición mínima de "Recomendado" rechaza días con tormenta aunque `score_conveniencia ≥ 70`.
7. Los desempates producen resultados deterministas y verificables.
8. Las plantillas de texto corresponden a la combinación correcta de categoría y condiciones.
9. La versión del motor y el generador se almacenan en cada predicción.
10. La ausencia de datos meteorológicos produce estado degradado coherente, sin error fatal.

---

## 15. Elementos fuera del alcance de este documento

- Arquitectura de microservicios y ubicación del motor en los servicios.
- Tecnología de implementación (lenguaje, framework).
- Contratos API del endpoint semanal.
- Diseño visual del dashboard.
- Estrategia de caché del pronóstico meteorológico.
- Infraestructura de AWS.

Estos puntos se definen en `04-arquitectura-y-modelo-de-datos.md` y `05-contratos-api-y-diseno-interfaz.md`.

## 16. Cierre normativo de implementación — versión 0.2 (2026-10-06)

El usuario autorizó completar los puntos pendientes con las decisiones existentes.
Esta sección precisa y, ante diferencias, sustituye las reglas anteriores afectadas.

- El factor mensual se conserva en los pesos y la trazabilidad, pero se cancela al
  distribuir un total dentro del mismo mes. La estacionalidad cuantitativa procede
  de los totales oficiales. No se aplica una segunda multiplicación al total.
- Semilla: SHA-256 de la cadena UTF-8 `YYYY-MM|SG-1.0`; primeros ocho dígitos
  hexadecimales, módulo 2147483646 más 1. Lehmer: multiplicador 48271,
  módulo 2147483647; avanzar una vez por día desde el día 1 y dividir el estado
  entre el módulo para obtener u en (0,1). Variación = 1 + u*0.06 - 0.03.
- `round` significa redondeo decimal HALF_UP a entero. Corregir el residuo en el
  día de mayor peso (fecha más temprana en empate). Si restarlo produciría un
  negativo, retirar solo los visitantes disponibles y continuar por peso
  descendente/fecha ascendente hasta agotar el residuo.
- Percentil 95: interpolación lineal con índice `(n-1)*0.95` sobre valores
  ordenados. Guardar y usar el resultado redondeado HALF_UP a cuatro decimales.
  Con conjunto vacío o p95 <= 0 la afluencia es nula; no dividir entre cero.
- La mediana usa meses AVAILABLE o ZERO_REPORTED del mismo mes desde 2022
  hasta el año anterior a la fecha consultada. Un cero oficial es un dato válido.
  Datos INCOMPLETE y NOT_YET_AVAILABLE se excluyen. La referencia publicada del
  propio año tiene prioridad. El periodo del p95 termina en el último mes importado.
- UV: 0 puntos si <= 6, 5 si > 6 y < 10, 10 si >= 10. Conveniencia se redondea
  HALF_UP tras limitar a [0,100]. Las penalizaciones WMO son magnitudes positivas
  que se RESTAN. Solo códigos WMO reconocidos; nieve/hielo (66,67,71,73,75,77,85,86)
  se consideran adversos con penalización 25. Desconocidos: meteorología no válida.
- Un día meteorológico incompleto, no finito, negativo en cantidades que no pueden
  ser negativas o con fecha desalineada se trata como no disponible. No se rellenan
  variables ausentes con cero.
- Si falta historial o p95, afluencia y conveniencia son nulas; categoría SIN_DATOS,
  motivo NO_HISTORICAL_DATA. Sin meteorología, conveniencia nula, motivo
  WEATHER_UNAVAILABLE. Si concurren ambos, tiene prioridad NO_HISTORICAL_DATA.
  ZERO_REPORTED_MONTH indica afluencia 0 válida y estado degradado por precaución;
  se permite calcular conveniencia con clima completo. No afirma apertura.
- Selección: primero candidatos RECOMENDADO; si no existen, candidatos con
  conveniencia. Tomar el máximo y considerar empate solo a candidatos a <= 1 punto
  de ESE máximo. Elegir menor afluencia y luego fecha. Sin conveniencias, elegir
  menor afluencia no nula y fecha. Sin ninguna afluencia, no existe mejor día.
- CP-01: horas_lluvia=0, horas_sol_s=18000; resultado 100. CP-02:
  horas_lluvia=2, horas_sol_s=0; resultado 76. CP-03: uv_max=8,
  sensacion_max_c=28, horas_sol_s=0; resultado 33 (32.5 antes de redondear).
  CP-04: horas_lluvia=5, viento_max_kmh=50, uv_max=10,
  sensacion_max_c=37, horas_sol_s=0; resultado 0. Completar temperaturas válidas
  informativas en fixtures. Estas entradas hacen verificables los CP originales.
- Factores: priorizar tormenta, lluvia, viento, UV, calendario, fin de semana,
  temporada y afluencia; máximo cuatro. Si ninguno aplica, usar
  "Estimación basada en el patrón mensual y el día de la semana".
- Plantillas con condiciones simultáneas: tormenta precede lluvia intensa;
  lluvia probable precede alta concurrencia. Sin historial usar la plantilla
  NO_HISTORICAL_DATA: "No se dispone de datos históricos suficientes para estimar
  esta fecha. Consulte el pronóstico y los canales oficiales antes de planificar."
- Advertencia sin clima: "No se dispone de pronóstico meteorológico suficiente.
  La fecha señalada corresponde a la menor afluencia estimada."
- La advertencia metodológica debe aclarar que el clima interviene en conveniencia;
  la puntuación de afluencia depende de los datos mensuales y del calendario.
- Parámetros y calendario se incluyen por contenido y hash en la versión generada.
  Si cambian entradas o configuración con una versión ya persistida, el proceso
  rechaza la sustitución: debe proporcionarse una nueva versión del generador.
- Calendario explícito 2022–2026 con feriados nacionales según su vigencia legal.
  La clasificación de feriado largo se guarda en JSON, nunca se deduce en runtime.
  Puentes solo si están respaldados por norma; no se inventan vacaciones ni eventos.
  Fuera del rango cubierto se devuelve NO_HISTORICAL_DATA hasta actualizar calendario.
