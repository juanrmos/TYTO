# Arquitectura y modelo de datos

## Aplicación web para la estimación de afluencia turística en la Cueva de las Lechuzas

**Versión:** 0.1  
**Estado:** Aprobado  
**Documentos relacionados:**

- `01-definicion-y-alcance-del-proyecto.md`
- `02-requisitos-del-sistema.md`
- `03-especificacion-motor-estimacion.md`

---

## 1. Propósito

Este documento define la arquitectura de microservicios, el stack tecnológico, el modelo de datos y las decisiones de despliegue del MVP. Los agentes de desarrollo deberán respetar estos límites sin añadir servicios, tecnologías ni dependencias no aprobadas aquí.

---

## 2. Decisiones tecnológicas aprobadas

| Capa | Tecnología | Versión mínima |
|---|---|---|
| Backend — Servicios | Python 3.12 + FastAPI | FastAPI ≥ 0.111 |
| Frontend | React 18 + Vite 5 | Node ≥ 20 LTS |
| Base de datos | PostgreSQL 16 | — |
| Contenedores | Docker + Docker Compose (desarrollo local) | Docker ≥ 26 |
| API meteorológica | Open-Meteo (sin clave de API, gratuita) | — |
| ORM | SQLAlchemy 2 + Alembic (migraciones) | — |
| Validación | Pydantic v2 (integrado en FastAPI) | — |
| HTTP cliente | `httpx` (asíncrono) | ≥ 0.27 |

### 2.1. Justificación del stack

- **Python + FastAPI**: el motor de estimación, la normalización y los scripts de datos ya utilizan Python. Mantener un solo lenguaje en el backend elimina un cambio de contexto innecesario y facilita compartir lógica matemática entre scripts y servicios.
- **React + Vite**: produce un bundle estático que puede desplegarse en cualquier CDN o almacenamiento de objetos sin servidor de aplicación.
- **PostgreSQL**: modelo relacional adecuado para datos históricos, predicciones trazables y relaciones entre entidades turísticas. Soporta migraciones incrementales con Alembic.

---

## 3. Arquitectura de microservicios

### 3.1. Servicios del MVP

El MVP se compone de **dos microservicios** y **una aplicación frontend estática**:

```
┌─────────────────────────────────────────────────────────┐
│                      Internet                           │
└─────────────┬───────────────────────────┬───────────────┘
              │                           │
              ▼                           ▼
   ┌──────────────────┐        ┌──────────────────────┐
   │  Frontend        │        │  Servicio de          │
   │  React + Vite    │──────▶ │  Predicción (STP)     │
   │  (estático)      │  HTTP  │  Python + FastAPI     │
   └──────────────────┘        └────────┬─────────────┘
                                        │ HTTP interno
                                        ▼
                               ┌──────────────────────┐
                               │  Servicio             │
                               │  Meteorológico (SMS)  │
                               │  Python + FastAPI     │
                               └────────┬─────────────┘
                                        │ HTTPS
                                        ▼
                               ┌──────────────────────┐
                               │  Open-Meteo API       │
                               │  (externa, gratuita)  │
                               └──────────────────────┘
                                        
   ┌──────────────────────────────────────────────────┐
   │  PostgreSQL (base de datos compartida del MVP)   │
   │  Accedida por STP únicamente                     │
   └──────────────────────────────────────────────────┘
```

### 3.2. Servicio de Predicción Turística (STP)

**Responsabilidades:**

- Exponer la API pública consumida por el frontend.
- Ejecutar el motor de estimación de afluencia y conveniencia.
- Consultar y persistir registros mensuales oficiales.
- Gestionar datos diarios sintéticos.
- Llamar al SMS para obtener el pronóstico meteorológico normalizado.
- Calcular la puntuación de conveniencia combinando afluencia + clima.
- Seleccionar la mejor opción semanal.
- Generar plantillas textuales de recomendación.
- Persistir predicciones con trazabilidad.

**No es responsable de:**

- Llamar directamente a Open-Meteo.
- Interpretar los campos específicos de Open-Meteo.
- Gestionar usuarios ni autenticación.

**Puerto local por defecto:** `8000`

### 3.3. Servicio Meteorológico (SMS)

**Responsabilidades:**

- Llamar a la API de Open-Meteo con las coordenadas del destino.
- Transformar la respuesta a los nombres internos definidos en el `03` (`lluvia_mm`, `prob_lluvia_pct`, etc.).
- Almacenar en caché la respuesta durante el tiempo de vigencia configurado.
- Exponer un endpoint interno que devuelva el pronóstico normalizado de los próximos N días.
- Manejar errores del proveedor y devolver una respuesta degradada controlada.

**No es responsable de:**

- Calcular afluencia ni conveniencia.
- Acceder a la base de datos.
- Ser accesible desde el exterior (es un servicio interno).

**Puerto local por defecto:** `8001`

**Caché del pronóstico:**

- Vigencia: **3 horas** (configurable por variable de entorno `WEATHER_CACHE_TTL_SECONDS`).
- Implementación MVP: caché en memoria del proceso (dict con timestamp). Para producción se puede migrar a Redis sin cambiar el contrato.
- Si el caché está vigente, no se llama a Open-Meteo.

### 3.4. Frontend (FE)

**Responsabilidades:**

- Renderizar el dashboard de los siete días.
- Consumir únicamente la API pública del STP.
- Manejar estados de carga, error y datos incompletos.
- No contener lógica de negocio del motor.

**No accede directamente al SMS ni a la base de datos.**

---

## 4. Comunicación entre servicios

| Origen | Destino | Protocolo | Tipo |
|---|---|---|---|
| Frontend | STP `/api/v1/forecast/{destination_id}` | HTTP/HTTPS | Pública |
| STP | SMS `/internal/weather` | HTTP | Interna (red privada) |
| SMS | Open-Meteo | HTTPS | Externa |
| STP | PostgreSQL | TCP (SQLAlchemy) | Interna |

### 4.1. Reglas de comunicación

1. El frontend nunca llama al SMS directamente.
2. El SMS nunca llama al STP.
3. La base de datos solo es accesible desde el STP.
4. Los contratos de comunicación se definen en `05-contratos-api-y-diseno-interfaz.md`.

---

## 5. Modelo de datos

### 5.1. Entidad: `tourist_destinations`

Representa un destino turístico. El MVP registra uno solo (Cueva de las Lechuzas), pero la tabla está diseñada para múltiples destinos.

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `UUID` | PK, default gen | Identificador único |
| `slug` | `VARCHAR(100)` | UNIQUE, NOT NULL | Identificador legible (`cueva-lechuzas`) |
| `name` | `VARCHAR(200)` | NOT NULL | Nombre completo del destino |
| `latitude` | `NUMERIC(9,6)` | NOT NULL | Coordenada para Open-Meteo |
| `longitude` | `NUMERIC(9,6)` | NOT NULL | Coordenada para Open-Meteo |
| `timezone` | `VARCHAR(50)` | NOT NULL | p.ej. `America/Lima` |
| `official_url` | `TEXT` | NULLABLE | URL de SERNANP |
| `tickets_url` | `TEXT` | NULLABLE | URL de compra de entradas |
| `directions_url` | `TEXT` | NULLABLE | URL de cómo llegar |
| `is_active` | `BOOLEAN` | DEFAULT TRUE | Controla visibilidad en el MVP |
| `created_at` | `TIMESTAMPTZ` | DEFAULT NOW() | Auditoría |

**Índices:** `slug` (UNIQUE).

---

### 5.2. Entidad: `monthly_visitor_records`

Almacena los registros mensuales oficiales importados de MINCETUR.

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `UUID` | PK | — |
| `destination_id` | `UUID` | FK → `tourist_destinations` | — |
| `year` | `SMALLINT` | NOT NULL | Año del registro |
| `month` | `SMALLINT` | NOT NULL, CHECK 1–12 | Mes del registro |
| `total_visitors` | `INTEGER` | NOT NULL, CHECK ≥ 0 | Total mensual oficial |
| `national_visitors` | `INTEGER` | NULLABLE | Visitantes nacionales |
| `foreign_visitors` | `INTEGER` | NULLABLE | Visitantes extranjeros |
| `availability_status` | `VARCHAR(30)` | NOT NULL | `AVAILABLE`, `NOT_YET_AVAILABLE`, `INCOMPLETE`, `ZERO_REPORTED` |
| `source_reference` | `VARCHAR(200)` | NOT NULL | Identificación de la fuente (MINCETUR) |
| `imported_at` | `TIMESTAMPTZ` | DEFAULT NOW() | Fecha de importación |

**Índices:** UNIQUE (`destination_id`, `year`, `month`, `source_reference`).

---

### 5.3. Entidad: `synthetic_generator_versions`

Registra las versiones del generador sintético para trazabilidad.

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `UUID` | PK | — |
| `version_code` | `VARCHAR(20)` | UNIQUE, NOT NULL | p.ej. `SG-1.0` |
| `p95_global` | `NUMERIC(12,4)` | NOT NULL | Percentil 95 global calculado |
| `parameters_json` | `JSONB` | NOT NULL | Factores, semilla y configuración |
| `generated_at` | `TIMESTAMPTZ` | DEFAULT NOW() | — |
| `record_count` | `INTEGER` | NOT NULL | Total de registros diarios generados |

---

### 5.4. Entidad: `synthetic_daily_records`

Almacena la distribución diaria sintética generada.

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `UUID` | PK | — |
| `destination_id` | `UUID` | FK → `tourist_destinations` | — |
| `generator_version_id` | `UUID` | FK → `synthetic_generator_versions` | — |
| `date` | `DATE` | NOT NULL | Fecha del registro |
| `estimated_visitors` | `INTEGER` | NOT NULL, CHECK ≥ 0 | Visitantes diarios sintéticos |
| `day_weight` | `NUMERIC(8,6)` | NOT NULL | Peso final usado en el cálculo |
| `factors_json` | `JSONB` | NOT NULL | `{factor_semana, factor_tipo_fecha, factor_temporada, variacion}` |
| `is_synthetic` | `BOOLEAN` | DEFAULT TRUE | Siempre TRUE en esta tabla |

**Índices:** UNIQUE (`destination_id`, `generator_version_id`, `date`). Índice en `date`.

---

### 5.5. Entidad: `estimation_engine_versions`

Registra las versiones del motor de estimación.

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `UUID` | PK | — |
| `version_code` | `VARCHAR(20)` | UNIQUE, NOT NULL | p.ej. `ME-1.0` |
| `thresholds_json` | `JSONB` | NOT NULL | Umbrales de afluencia, conveniencia y condición mínima |
| `weights_json` | `JSONB` | NOT NULL | Penalizaciones meteorológicas y bonus |
| `created_at` | `TIMESTAMPTZ` | DEFAULT NOW() | — |

---

### 5.6. Entidad: `weather_snapshots`

Almacena las instantáneas meteorológicas obtenidas de Open-Meteo.

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `UUID` | PK | — |
| `destination_id` | `UUID` | FK → `tourist_destinations` | — |
| `fetched_at` | `TIMESTAMPTZ` | NOT NULL | Momento de la consulta a Open-Meteo |
| `valid_until` | `TIMESTAMPTZ` | NOT NULL | Caché hasta este momento |
| `provider` | `VARCHAR(50)` | DEFAULT `open-meteo` | — |
| `raw_response_json` | `JSONB` | NOT NULL | Respuesta original (para auditoría) |
| `normalized_json` | `JSONB` | NOT NULL | Variables internas ya transformadas |
| `horizon_days` | `SMALLINT` | NOT NULL | Días cubiertos en la respuesta |

**Índices:** en `destination_id`, `fetched_at`.

---

### 5.7. Entidad: `daily_predictions`

Almacena cada predicción generada para una fecha y destino.

| Columna | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | `UUID` | PK | — |
| `destination_id` | `UUID` | FK → `tourist_destinations` | — |
| `engine_version_id` | `UUID` | FK → `estimation_engine_versions` | — |
| `generator_version_id` | `UUID` | FK → `synthetic_generator_versions` | — |
| `weather_snapshot_id` | `UUID` | FK → `weather_snapshots`, NULLABLE | Nulo si no hubo pronóstico |
| `prediction_date` | `DATE` | NOT NULL | Fecha evaluada |
| `generated_at` | `TIMESTAMPTZ` | DEFAULT NOW() | Momento de generación |
| `ref_mensual` | `INTEGER` | NULLABLE | Referencia mensual usada |
| `estimated_visitors_day` | `INTEGER` | NULLABLE | Visitantes diarios sintéticos |
| `score_afluencia` | `SMALLINT` | NULLABLE, CHECK 0–100 | Puntuación de afluencia |
| `nivel_afluencia` | `VARCHAR(10)` | NULLABLE | `BAJA`, `MEDIA`, `ALTA` |
| `score_conveniencia` | `SMALLINT` | NULLABLE, CHECK 0–100 | Puntuación de conveniencia |
| `categoria_recomendacion` | `VARCHAR(30)` | NULLABLE | `RECOMENDADO`, `PRECAUCION`, `NO_RECOMENDADO`, `SIN_DATOS` |
| `is_best_option` | `BOOLEAN` | DEFAULT FALSE | Marca la mejor opción de la semana |
| `best_option_label` | `VARCHAR(40)` | NULLABLE | `MEJOR_OPCION`, `MEJOR_ALTERNATIVA`, `MENOR_AFLUENCIA` |
| `recommendation_template_key` | `VARCHAR(60)` | NULLABLE | Clave de la plantilla textual usada |
| `active_factors_json` | `JSONB` | NULLABLE | Lista de factores activos del motor |
| `is_degraded` | `BOOLEAN` | DEFAULT FALSE | TRUE si faltaron datos para cálculo completo |
| `degraded_reason` | `VARCHAR(100)` | NULLABLE | Motivo del estado degradado |

**Índices:** en (`destination_id`, `prediction_date`). UNIQUE recomendado en (`destination_id`, `prediction_date`, `engine_version_id`).

---

### 5.8. Diagrama entidad-relación (simplificado)

```
tourist_destinations
        │
        ├──< monthly_visitor_records
        ├──< synthetic_daily_records >──── synthetic_generator_versions
        ├──< weather_snapshots
        └──< daily_predictions >────────── estimation_engine_versions
                        │
                        ├── synthetic_generator_versions
                        └── weather_snapshots (nullable)
```

---

## 6. Calendario turístico local

El calendario no se almacena en la base de datos principal. Se gestiona como un archivo de configuración versionado en el repositorio:

```
data/
└── calendar/
    └── peru_tourist_calendar.json
```

Formato de cada entrada:

```json
{
  "date": "2026-04-02",
  "name": "Jueves Santo",
  "type": "FERIADO_AISLADO",
  "is_long_weekend": false,
  "reference": "Decreto Supremo N° 003-2024-PCM"
}
```

Tipos reconocidos: `FERIADO_LARGO`, `FERIADO_AISLADO`, `PUENTE`, `PERIODO_ESPECIAL`.

El STP carga este archivo al iniciar. Si cambia, se requiere reiniciar el servicio (o un endpoint de recarga en futuras versiones).

---

## 7. Estructura del monorepo

```
tyto/                              ← raíz del monorepo
├── services/
│   ├── prediction/                ← Servicio de Predicción Turística (STP)
│   │   ├── app/
│   │   │   ├── api/               ← routers FastAPI
│   │   │   ├── core/              ← motor de estimación, lógica de negocio
│   │   │   ├── db/                ← modelos SQLAlchemy, sesiones
│   │   │   ├── schemas/           ← Pydantic schemas (request/response)
│   │   │   └── main.py
│   │   ├── tests/
│   │   ├── alembic/               ← migraciones
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── weather/                   ← Servicio Meteorológico (SMS)
│       ├── app/
│       │   ├── api/
│       │   ├── adapters/          ← cliente Open-Meteo + normalización
│       │   ├── cache/             ← lógica de caché en memoria
│       │   └── main.py
│       ├── tests/
│       ├── Dockerfile
│       └── requirements.txt
├── apps/
│   └── dashboard/                 ← Frontend React + Vite
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── hooks/
│       │   ├── api/               ← cliente HTTP hacia STP
│       │   └── main.jsx
│       ├── public/
│       ├── Dockerfile
│       ├── vite.config.js
│       └── package.json
├── data/
│   ├── raw/                       ← CSV oficial MINCETUR (sin modificar)
│   ├── processed/                 ← datasets normalizados
│   ├── calendar/                  ← calendario turístico local
│   └── reports/                   ← reportes de calidad
├── scripts/                       ← scripts de importación y generación
├── docs/                          ← documentación del proyecto
├── specs/                         ← SDD incrementales
├── tests/                         ← pruebas de integración entre servicios
├── infrastructure/                ← IaC y configuración de despliegue
├── docker-compose.yml             ← entorno local completo
├── docker-compose.test.yml        ← entorno de pruebas
├── .env.example
├── AGENTS.md
└── README.md
```

---

## 8. Despliegue

### 8.1. Plataforma aprobada

Todo el alojamiento de Tyto se realizará en AWS, por decisión explícita del usuario.
Amazon EC2 ejecuta STP, SMS, PostgreSQL 16 y Nginx mediante Docker Compose.
AWS Amplify Hosting publica el bundle React/Vite. El tamaño de EC2 se elegirá
según memoria y carga medidas; no se garantiza gratuidad ni capacidad de t3.micro.
Se revisarán cuotas, créditos y precios de la cuenta antes de crear recursos.

### 8.2. Topología

```text
Navegador → AWS Amplify Hosting (frontend HTTPS)
          → API HTTPS → Nginx en EC2 → STP
                                     ├── SMS → Open-Meteo
                                     └── PostgreSQL 16 (volumen persistente)
```

Solo Nginx publica 80/443. STP, SMS y PostgreSQL usan redes privadas Docker.
SSH se restringe a la IP del operador. Esta VM es un punto único de fallo del MVP;
se requieren respaldos y prueba de restauración antes de la demostración.

### 8.3. Configuración

- EC2: `infrastructure/.env.production.example` se copia a `.env.production` con
  contraseña aleatoria, `API_DOMAIN`, `TLS_CERT_DIR` y `CORS_ORIGINS` del frontend.
- Amplify: raíz `apps/dashboard`, `npm ci`, `npm run build`, salida `dist`.
  `VITE_API_BASE_URL=https://api.tu-dominio` se configura antes del build.
- `amplify.yml` define el build del monorepo. Las variables VITE son públicas;
  no contienen secretos. No se versionan archivos de credenciales.
- Los certificados TLS deben existir antes de iniciar el proxy y renovarse.

---

## 9. Decisiones arquitectónicas registradas

### ADR-001. Stack Python + FastAPI para el backend

**Decisión:** Python 3.12 + FastAPI para ambos microservicios.  
**Motivo:** La lógica del motor y los scripts de datos ya están en Python. FastAPI es asíncrono, autodocumentado con OpenAPI y tiene soporte nativo de Pydantic v2.  
**Alternativas descartadas:** Node.js (cambio de lenguaje innecesario), Java (excesivo para MVP académico).

### ADR-002. Dos microservicios con responsabilidades claras

**Decisión:** STP y SMS como dos servicios independientes.  
**Motivo:** El SMS aísla la dependencia de Open-Meteo. Si el proveedor cambia, solo se modifica el SMS sin tocar el motor de estimación. Dos servicios cumplen el requisito académico de microservicios con responsabilidades justificables.  
**Alternativas descartadas:** Tres servicios (datos históricos separado) — innecesario, los datos históricos son propiedad natural del STP.

### ADR-003. PostgreSQL como base de datos

**Decisión:** PostgreSQL 16 con SQLAlchemy 2 + Alembic.  
**Motivo:** Modelo relacional adecuado para datos históricos, predicciones y trazabilidad. Alembic permite migraciones incrementales sin perder datos.  
**Alternativas descartadas:** DynamoDB (modelado más complejo para relaciones), SQLite (no apto para producción).

### ADR-004. AWS EC2 como plataforma de despliegue

**Decisión:** Amazon EC2 + AWS Amplify Hosting.
**Motivo:** Centralizar el MVP en AWS y conservar los contenedores existentes.
PostgreSQL se ejecuta en EC2 con volumen persistente; RDS queda fuera del MVP.
La cuenta, región y presupuesto deben verificarse antes de provisionar.

### ADR-005. Caché en memoria para el pronóstico meteorológico

**Decisión:** Dict en memoria del proceso SMS con TTL de 3 horas.  
**Motivo:** Simplicidad para el MVP. Open-Meteo actualiza pronósticos cada pocas horas; 3 horas es un equilibrio entre frescura y número de llamadas externas.  
**Evolución futura:** Redis sin cambiar el contrato del SMS.

---

## 10. Límites arquitectónicos para agentes

Los siguientes límites no pueden modificarse sin actualizar este documento y obtener aprobación:

1. El frontend no llama a Open-Meteo directamente.
2. El SMS no accede a la base de datos PostgreSQL.
3. No se añadirán microservicios adicionales sin aprobación.
4. El motor de estimación vive exclusivamente en el STP (`services/prediction/app/core/`).
5. Las credenciales nunca se hardcodean en código ni en Dockerfiles.
6. Los contratos entre STP y SMS se definen en `05-contratos-api-y-diseno-interfaz.md` y no pueden cambiarse unilateralmente en el código.

## 11. Correcciones de arquitectura — versión 0.2 (2026-10-06)

### Despliegue sin dominio propio — decisión de sesión

El usuario dispone de una EC2 en us-east-2, ampliada a 4 GiB y 20 GiB de disco,
y confirmó que no tiene dominio propio. Se añade `infrastructure/compose.http.yml`
para Nginx HTTP en EC2 y una distribución CloudFront con el dominio HTTPS asignado
por AWS delante de la API. Amplify permanece como alojamiento del frontend.
El tramo CloudFront→EC2 será HTTP en esta modalidad; HTTPS al origen requiere
certificado y configuración posterior. No presentar esta modalidad como TLS extremo
a extremo. CloudFront debe desactivar caché del pronóstico y reenviar `Origin` para CORS.
El usuario acepta explícitamente SSH 22 desde 0.0.0.0/0 con autenticación por llave.
No se ejecutarán pruebas adicionales sin planificación acordada; las comprobaciones
de arranque y accesibilidad se realizan para completar el despliegue.

Sustituye las afirmaciones incompatibles de §§5 y 8. Autorización: solicitud del
usuario de completar las decisiones pendientes e implementar toda la aplicación.

- Plataforma aprobada: Amazon EC2 + AWS Amplify Hosting, según §8.
  Los anexos anteriores de otros proveedores quedan descartados.
- monthly_visitor_records.total_visitors permite NULL exclusivamente para estados
  NOT_YET_AVAILABLE e INCOMPLETE. AVAILABLE exige entero > 0 y ZERO_REPORTED exige 0.
- daily_predictions es append-only: eliminar la sugerencia UNIQUE por fecha/motor.
  Cada consulta conserva un snapshot y nuevas predicciones con generated_at.
- La orquestación con red/BD se ubica en app/services; core conserva funciones puras.
- Parámetros del motor en data/config/engine.json; calendario y CSV se montan
  en solo lectura. STP valida configuración y versiones al iniciar y al generar datos.
- Se usan asyncpg (driver), pydantic-settings (entorno), tzdata (zonas en Windows),
  uvicorn (ASGI), pytest/pytest-asyncio/pytest-cov, Ruff, ESLint, Prettier,
  Vitest/Testing Library/jsdom y Playwright para pruebas. Versiones en manifiestos.
- Nuevas variables: POSTGRES_USER/PASSWORD/DB, CORS_ORIGINS (lista JSON),
  DATA_DIR, WEATHER_TIMEOUT_SECONDS, OPEN_METEO_URL y TEST_DATABASE_URL.
  DATABASE_URL puede derivarse mediante SQLAlchemy URL de POSTGRES_* sin concatenar
  contraseñas. Producción falla si conserva el marcador de contraseña de ejemplo.
- SMS no recibe credenciales de BD. Cada servicio tiene su entorno mínimo.
  Cache key: coordenadas, days, timezone y fecha local; TTL 10800s. Acceso concurrente
  protegido; datos caducados no se reutilizan silenciosamente. Un worker SMS en MVP.
- El despliegue aplica migraciones e inicialización mediante un servicio one-shot;
  STP inicia después. Actualización con imágenes construidas, health checks y respaldo.
