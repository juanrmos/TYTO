# Plan de implementación, pruebas y despliegue

## Aplicación web para la estimación de afluencia turística en la Cueva de las Lechuzas

**Versión:** 0.1  
**Estado:** Aprobado  
**Documentos relacionados:**

- `03-especificacion-motor-estimacion.md`
- `04-arquitectura-y-modelo-de-datos.md`
- `05-contratos-api-y-diseno-interfaz.md`

---

## 1. Propósito

Este documento define el orden de implementación incremental del MVP, la estrategia de pruebas por capa, los criterios de terminado de cada fase y el procedimiento de despliegue. Ningún agente debe saltar una fase ni implementar funcionalidades fuera del alcance del incremento activo.

---

## 2. Principios de la implementación incremental

1. Cada incremento produce un entregable verificable antes de iniciar el siguiente.
2. Ningún incremento introduce funcionalidades no aprobadas en los documentos `01`–`05`.
3. Las pruebas se escriben junto al código, no al final.
4. El agente no toma decisiones de diseño o arquitectura; consulta los documentos antes de implementar.
5. Si existe contradicción entre documentos, el agente detiene el trabajo y reporta el conflicto.

---

## 3. Fases de implementación

### Fase 1 — Preparación del repositorio (SDD-001)

**Objetivo:** Repositorio estructurado, configurado y listo para recibir código.

**Entregables:**
- Estructura de directorios del monorepo según `04` sección 7.
- `.gitignore` para Python, Node.js y variables de entorno.
- `.env.example` con todas las variables definidas en `04` sección 8.4.
- `docker-compose.yml` con servicios: `db` (PostgreSQL 16), `stp`, `sms`.
- `docker-compose.test.yml` con base de datos de pruebas aislada.
- `README.md` con instrucciones mínimas de arranque local.
- Linters configurados: `ruff` (Python), `eslint` + `prettier` (JavaScript).
- Archivos `requirements.txt` iniciales vacíos para STP y SMS.
- `package.json` inicial para el dashboard.

**Criterios de terminado:**
- `docker-compose up` levanta los contenedores sin error (STP y SMS con respuesta de salud dummy).
- `ruff check .` y `eslint .` pasan sin errores en el código base vacío.
- El repositorio tiene al menos un commit inicial con el mensaje `chore: initial project structure`.

---

### Fase 2 — Importación de datos oficiales (SDD-002)

**Objetivo:** Datos mensuales oficiales de MINCETUR importados y validados en la base de datos.

**Entregables:**
- Modelos SQLAlchemy: `TouristDestination`, `MonthlyVisitorRecord`.
- Migración Alembic inicial que crea las tablas.
- Script `scripts/import_monthly_data.py` que lee `data/processed/visitas_mensuales_modelo.csv` e inserta registros en la BD.
- Seed inicial: registro del destino `cueva-lechuzas` con coordenadas y URLs oficiales.
- Pruebas del script de importación (validación de esquema, duplicados, estados de disponibilidad).

**Criterios de terminado:**
- `python scripts/import_monthly_data.py` inserta los 56 registros del periodo 2022–agosto 2026 sin error.
- Ningún mes del periodo aparece con valor nulo en `total_visitors` cuando el estado es `AVAILABLE`.
- La restricción UNIQUE `(destination_id, year, month, source_reference)` impide duplicados.
- Las pruebas del script de importación pasan con `pytest`.

---

### Fase 3 — Generación diaria sintética (SDD-003)

**Objetivo:** Dataset diario sintético generado, validado y persistido para el periodo completo.

**Entregables:**
- Modelos SQLAlchemy: `SyntheticGeneratorVersion`, `SyntheticDailyRecord`.
- Migración Alembic para las nuevas tablas.
- Módulo `services/prediction/app/core/synthetic_generator.py` con:
  - Función `compute_day_weight(date, calendar_events)` → `peso_final`.
  - Función `generate_month(year, month, ref_mensual, version, calendar_events)` → lista de registros diarios.
  - Función `compute_p95_global(all_daily_records)` → valor escalar.
  - Función `apply_roundoff_correction(records, ref_mensual)` → lista corregida.
- Script `scripts/generate_synthetic_data.py` que ejecuta la generación para el periodo completo y persiste en BD.
- Archivo `data/calendar/peru_tourist_calendar.json` con los feriados peruanos 2022–2026.
- Pruebas unitarias cubriendo los casos CP-08 y CP-10 del `03`.

**Criterios de terminado:**
- `python scripts/generate_synthetic_data.py` completa sin error.
- `Σ visitantes_dia(d)` = `ref_mensual` para cada mes del periodo (validación automatizada).
- El `p95_global` se almacena en `SyntheticGeneratorVersion` con la versión `SG-1.0`.
- Ejecutar el script dos veces con la misma versión produce el mismo resultado (reproducibilidad).
- Las pruebas unitarias pasan con `pytest`.

---

### Fase 4 — Motor de estimación de afluencia (SDD-004)

**Objetivo:** Motor de afluencia y conveniencia implementado y probado con los casos del `03`.

**Entregables:**
- Módulo `services/prediction/app/core/estimation_engine.py` con:
  - `compute_affuence_score(estimated_visitors, p95_global)` → `score_afluencia`.
  - `classify_affuence_level(score)` → `BAJA | MEDIA | ALTA`.
  - `compute_convenience_score(weather_day, score_afluencia)` → `score_conveniencia`.
  - `classify_recommendation(score_conveniencia, weather_day)` → categoría.
  - `select_best_day(day_results)` → índice del mejor día + etiqueta.
  - `get_active_factors(day_context)` → lista de textos de factores.
  - `get_recommendation_text(category, affuence_level, weather_day)` → texto de plantilla.
- Modelo SQLAlchemy: `EstimationEngineVersion`.
- Migración Alembic para la nueva tabla.
- Seed de la versión `ME-1.0` con umbrales y pesos en JSON.
- Pruebas unitarias cubriendo CP-01 al CP-07 del `03`.

**Criterios de terminado:**
- Todos los casos de prueba CP-01 a CP-07 pasan con `pytest`.
- La función `select_best_day` produce resultados deterministas ante los mismos inputs.
- El módulo no importa nada de `fastapi`, `sqlalchemy` ni capas de red (es lógica pura).

---

### Fase 5 — Servicio Meteorológico (SDD-005)

**Objetivo:** SMS operativo, devolviendo pronóstico normalizado con caché.

**Entregables:**
- Aplicación FastAPI del SMS (`services/weather/app/main.py`).
- Módulo `services/weather/app/adapters/open_meteo.py` — cliente HTTP con `httpx`.
- Módulo `services/weather/app/adapters/normalizer.py` — mapeo de campos Open-Meteo a nombres internos del `03`.
- Módulo `services/weather/app/cache/memory_cache.py` — dict con timestamp y TTL.
- Router `GET /internal/weather` según contrato del `05` sección 4.2.
- Router `GET /health` según `05` sección 4.1.
- Dockerfile del SMS.
- Pruebas unitarias del normalizador con respuesta mockeada de Open-Meteo.
- Prueba de integración que verifica el caché: dos llamadas consecutivas producen solo una solicitud HTTP.

**Criterios de terminado:**
- `GET /internal/weather?latitude=-9.3008&longitude=-76.0026` responde en < 2 s con los campos normalizados.
- Los nombres de campos en la respuesta coinciden exactamente con los definidos en `05` sección 4.2.
- Una segunda llamada dentro del TTL devuelve `cache_status: "HIT"` en el endpoint de salud.
- Un timeout de Open-Meteo devuelve HTTP 503 con el cuerpo definido en `05`.

---

### Fase 6 — API semanal del STP (SDD-006)

**Objetivo:** STP exponiendo el endpoint principal de pronóstico semanal completo.

**Entregables:**
- Aplicación FastAPI del STP (`services/prediction/app/main.py`).
- Modelos SQLAlchemy: `WeatherSnapshot`, `DailyPrediction`.
- Migración Alembic para las nuevas tablas.
- Router `GET /api/v1/forecast/{destination_slug}` según contrato del `05` sección 3.2.
- Router `GET /api/v1/destinations` según `05` sección 3.3.
- Router `GET /api/v1/health/full` según `05` sección 3.4.
- Router `GET /health` básico.
- Servicio interno que orquesta: obtener datos sintéticos → llamar SMS → ejecutar motor → armar respuesta → persistir predicción.
- Dockerfile del STP.
- Pruebas de integración:
  - Respuesta con 7 días cuando todos los datos están disponibles.
  - Respuesta con días degradados cuando el SMS devuelve 503.
  - Respuesta 404 para `destination_slug` inexistente.

**Criterios de terminado:**
- `GET /api/v1/forecast/cueva-lechuzas` responde con exactamente 7 elementos en `days`.
- La estructura JSON coincide exactamente con el ejemplo del `05` sección 3.2.
- Exactamente un día tiene `is_best: true`.
- Si el SMS falla, el STP devuelve 200 con días marcados como `is_degraded: true` (no 503).
- Las predicciones se persisten en `daily_predictions` con `version_motor` y `version_generador`.

---

### Fase 7 — Dashboard web (SDD-007)

**Objetivo:** Frontend React funcional consumiendo la API del STP.

**Entregables:**
- Proyecto Vite + React en `apps/dashboard/`.
- Hook `useForecast(slug)` que llama al STP y gestiona estados de carga y error.
- Componente `DayCard` — tarjeta de un día con color según conveniencia.
- Componente `DaySelector` — fila de 7 tarjetas con selección activa.
- Componente `DayDetail` — panel detalle del día seleccionado.
- Componente `WeatherSummary` — bloque meteorológico.
- Componente `MethodologyWarning` — advertencia colapsable.
- Componente `OfficialLinks` — enlaces externos.
- Componente `WeekWarningBanner` — banner de semana desfavorable.
- Manejo de los 5 estados de interfaz definidos en `05` sección 7.4.
- Diseño responsivo según breakpoints del `05` sección 7.5.
- Variables de entorno mediante `VITE_API_BASE_URL`.
- Dockerfile de producción (nginx + bundle estático).
- Pruebas básicas de componentes con Vitest + React Testing Library:
  - Tarjeta muestra color verde para `RECOMENDADO`.
  - Tarjeta muestra color ámbar para `PRECAUCION`.
  - Tarjeta muestra color rojo para `NO_RECOMENDADO`.
  - Tarjeta de mejor opción muestra la etiqueta correcta.
  - El panel detalle cambia al seleccionar una tarjeta diferente.
  - El estado de carga muestra skeleton cards.
  - El estado de error muestra el botón de reintento.

**Criterios de terminado:**
- La aplicación carga el dashboard en < 3 s en conexión normal.
- Cambiar de tarjeta actualiza el panel detalle sin recarga de página.
- En viewport de 375 px de ancho no aparece scroll horizontal general.
- Las tarjetas muestran texto de categoría además del color.
- Las pruebas de componentes pasan con `vitest run`.

---

### Fase 8 — Integración completa y pruebas (SDD-008)

**Objetivo:** Sistema integrado localmente validado end-to-end.

**Entregables:**
- `docker-compose.yml` levanta STP + SMS + PostgreSQL + Frontend sin errores.
- Suite de pruebas de integración end-to-end en `tests/`:
  - El frontend carga datos reales del STP.
  - El STP llama al SMS y obtiene datos de Open-Meteo (o mock controlado).
  - Los datos sintéticos de la BD corresponden al periodo correcto.
- Prueba de humo: script `scripts/smoke_test.py` que verifica todos los endpoints de salud.
- Reporte de cobertura de pruebas del STP (objetivo: ≥ 70 % en módulos `core/`).
- `AGENTS.md` actualizado si alguna convención cambió durante la implementación.

**Criterios de terminado:**
- `docker-compose up` + `python scripts/smoke_test.py` pasa todos los checks.
- La suite de pruebas de integración corre en < 5 minutos.
- No hay secretos en el código ni en los Dockerfiles.
- El linter no reporta errores en ningún servicio.
- La cobertura del motor de estimación (`core/estimation_engine.py`) es ≥ 80 %.

---

### Fase 9 — Despliegue en AWS EC2 + Amplify Hosting (SDD-009)

**Objetivo:** MVP operativo y accesible mediante URL pública para la demostración.

**Entregables:**
- Documentación del procedimiento de despliegue en `infrastructure/README.md`:
  - Creación de la VM en AWS EC2, verificando capacidad y presupuesto.
  - Instalación de Docker y Docker Compose en la VM.
  - Configuración de Nginx como reverse proxy con TLS (Let's Encrypt).
  - Configuración de la base de datos en PostgreSQL 16 en un contenedor con volumen persistente en EC2.
  - Variables de entorno de producción (sin valores reales en el repositorio).
  - Procedimiento de despliegue del frontend en AWS Amplify Hosting.
  - Procedimiento de actualización (pull + restart).
  - Procedimiento de eliminación de recursos (para evitar uso innecesario).
- Script `infrastructure/deploy.sh` que automatiza pull + restart de contenedores.
- URL pública documentada en `README.md`.
- Prueba de humo en el entorno desplegado.

**Criterios de terminado:**
- `GET https://api.dominio/health` responde 200 desde internet.
- `GET https://api.dominio/api/v1/forecast/cueva-lechuzas` responde con datos reales.
- El frontend en AWS Amplify Hosting carga el dashboard en el navegador.
- La URL pública está documentada en el `README.md`.
- No hay credenciales en el repositorio.

---

## 4. Dependencias entre fases

```
Fase 1 (Repositorio)
    └──> Fase 2 (Datos oficiales)
              └──> Fase 3 (Sintético)
                        └──> Fase 4 (Motor)
                                  └──┐
         Fase 5 (SMS) ──────────────┤
                                    └──> Fase 6 (API STP)
                                               └──> Fase 7 (Frontend)
                                                         └──> Fase 8 (Integración)
                                                                   └──> Fase 9 (Despliegue)
```

**Fases en paralelo posibles:**
- Fase 5 (SMS) puede desarrollarse en paralelo con las Fases 2–4.
- Fase 7 (Frontend) puede iniciarse con datos mock del STP mientras la Fase 6 termina.

---

## 5. Estrategia de pruebas

### 5.1. Pirámide de pruebas

```
         /\
        /  \   Pruebas E2E (pocas, smoke test en producción)
       /────\
      /      \  Pruebas de integración (API, BD, servicios)
     /────────\
    /          \  Pruebas unitarias (motor, normalización, lógica pura)
   /────────────\
```

### 5.2. Pruebas unitarias

| Módulo | Herramienta | Cobertura objetivo |
|---|---|---|
| `core/estimation_engine.py` | pytest | ≥ 80 % |
| `core/synthetic_generator.py` | pytest | ≥ 80 % |
| `adapters/normalizer.py` (SMS) | pytest | ≥ 90 % |
| Componentes React (DayCard, DaySelector, DayDetail) | Vitest + RTL | Pruebas de comportamiento |

### 5.3. Pruebas de integración

| Prueba | Herramienta | Cuándo |
|---|---|---|
| Conservación mensual para todos los meses 2022–2026 | pytest | Fase 3 |
| Endpoint `GET /api/v1/forecast/cueva-lechuzas` completo | pytest + httpx | Fase 6 |
| Respuesta degradada cuando SMS falla | pytest + mock | Fase 6 |
| Caché del SMS (dos llamadas = una request HTTP) | pytest + mock | Fase 5 |
| Persistencia de predicciones en BD | pytest + BD de test | Fase 6 |

### 5.4. Prueba de humo (smoke test)

Verifica que todos los componentes desplegados responden correctamente:

```python
# scripts/smoke_test.py — checks esperados
GET /health                        → 200, status: ok       (STP)
GET /health                        → 200, status: ok       (SMS interno)
GET /api/v1/destinations           → 200, destinations: [cueva-lechuzas]
GET /api/v1/forecast/cueva-lechuzas → 200, days: 7 elementos
GET /api/v1/health/full            → 200, database: ok, weather_service: ok | degraded
```

### 5.5. Casos de prueba obligatorios del motor

Los casos CP-01 al CP-10 definidos en el `03` deben existir como pruebas automatizadas (`pytest`) antes de que la Fase 4 se considere terminada.

---

## 6. Criterios globales de terminado del MVP

El MVP se considera completo cuando:

1. Las Fases 1–9 han sido completadas y verificadas.
2. La prueba de humo pasa en el entorno de producción.
3. El dashboard es accesible desde internet mediante URL pública.
4. Los casos CP-01 a CP-10 pasan como pruebas automatizadas.
5. La conservación mensual es validada para todos los meses del periodo.
6. No existen secretos en el repositorio.
7. El `README.md` incluye instrucciones de ejecución local y la URL pública.
8. El historial de commits refleja el avance incremental por fases.

---

## 7. Evidencias necesarias para el video académico

Para cumplir con el entregable del curso el video deberá mostrar:

| Evidencia | Dónde ocurre |
|---|---|
| Arquitectura de microservicios funcionando | `docker-compose ps` + endpoints de salud |
| Datos históricos en la base de datos | Consulta SQL en PostgreSQL |
| Generación sintética reproducible | Ejecución del script + validación de suma |
| Consumo de la API meteorológica | Log del SMS mostrando llamada a Open-Meteo |
| Dashboard web con los 7 días | Navegador en la URL pública |
| Selección de tarjetas y actualización del detalle | Interacción en el dashboard |
| Mejor opción identificada | Tarjeta con etiqueta visible |
| Estado degradado (si se puede simular) | SMS desconectado + dashboard con gris |
| Advertencia metodológica | Sección visible en el dashboard |
| URL pública accesible | Navegador sin acceso local |

---

## 8. Guion de demostración para el usuario

```
1. Abrir la URL pública en el navegador.
2. Señalar el destino: "Cueva de las Lechuzas, Parque Nacional Tingo María".
3. Mostrar las 7 tarjetas y explicar el código de color.
4. Señalar la tarjeta marcada como "Mejor opción".
5. Hacer clic en dos tarjetas diferentes y mostrar cómo cambia el panel detalle.
6. Leer en voz alta la recomendación textual y los factores.
7. Mostrar el resumen meteorológico del día seleccionado.
8. Señalar la advertencia metodológica y los enlaces oficiales.
9. Cambiar a vista móvil en DevTools y mostrar el diseño responsivo.
10. Cerrar con: "El sistema estima, no garantiza; el visitante verifica en los canales oficiales."
```

---

## 9. Procedimiento de eliminación de recursos

Para evitar costos o uso innecesario después de la demostración:

```bash
# En la instancia EC2
docker-compose down -v      # detiene contenedores y elimina volúmenes locales

# En AWS Console
# 1. Terminar la instancia de Compute (o detenerla para conservar datos)
# 2. Revisar volúmenes EBS, snapshots e IPs públicas que sigan generando cargos
# 3. Eliminar reglas de seguridad abiertas (puertos 80/443)

# En AWS Amplify Hosting
# 1. Eliminar el proyecto o despublicar el despliegue activo
```

> Este procedimiento debe ejecutarse después de la calificación para evitar uso de recursos indefinido.

## 10. Ejecución integral autorizada (2026-10-06)

El usuario autoriza implementar todas las fases y completar las decisiones pendientes.
Se mantienen SDD breves y validaciones por fase. Una verificación externa no ejecutable
se registra como pendiente sin afirmar que pasó y no impide construir las otras capas.
La ausencia de Docker en el equipo no autoriza sustituir PostgreSQL por SQLite.
La fase 9 prepara PostgreSQL en la VM según docs/04 §11; toda referencia anterior a
otros servicios de base de datos queda sustituida. El despliegue público requiere cuentas y DNS.
Los commits usan la convención española de AGENTS.md; se sustituye el mensaje inglés
de fase 1. Las pruebas del generador y CP-09 también deben pasar antes de integrar STP.
El calendario se valida con fuentes oficiales; la publicación de eventos no documentados
queda excluida. Ver specs/SDD-001 a SDD-009 y docs/08-validacion-del-mvp.md.
