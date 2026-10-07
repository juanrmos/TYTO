# AGENTS.md — Instrucciones para agentes de desarrollo

**Proyecto:** Tyto — Estimación de afluencia turística, Cueva de las Lechuzas  
**Versión:** 0.1  
**Última actualización:** 2026-10-06

---

## 1. Propósito de este archivo

Este archivo define las reglas de trabajo para cualquier agente de inteligencia artificial que implemente, modifique o pruebe código en este repositorio. Deberás leer este archivo completo antes de realizar cualquier acción.

Si una instrucción de este archivo contradice una instrucción de un documento de `docs/`, prevalece el documento de `docs/` y deberás reportar la contradicción antes de continuar.

---

## 2. Orden obligatorio de lectura

Antes de comenzar cualquier tarea, lee los documentos en este orden:

1. `AGENTS.md` (este archivo) — reglas generales y convenciones.
2. `docs/01-definicion-y-alcance-del-proyecto.md` — contexto y alcance del MVP.
3. `docs/02-requisitos-del-sistema.md` — qué debe hacer el sistema y bajo qué condiciones.
4. `docs/03-especificacion-motor-estimacion.md` — fórmulas, factores, umbrales y plantillas del motor.
5. `docs/04-arquitectura-y-modelo-de-datos.md` — stack, microservicios, modelo de datos y despliegue.
6. `docs/05-contratos-api-y-diseno-interfaz.md` — contratos API y diseño de la interfaz.
7. `docs/06-plan-implementacion-pruebas-y-despliegue.md` — fases, pruebas y criterios de terminado.
8. El SDD del incremento activo en `specs/SDD-00X-*.md`.

No inicies implementación sin haber leído los documentos relevantes al incremento activo.

---

## 3. Jerarquía de fuentes de verdad

| Prioridad | Documento | Qué define |
|---|---|---|
| 1 | `docs/03-especificacion-motor-estimacion.md` | Toda la lógica de cálculo |
| 2 | `docs/05-contratos-api-y-diseno-interfaz.md` | Nombres de campos, rutas y estructuras de respuesta |
| 3 | `docs/04-arquitectura-y-modelo-de-datos.md` | Stack, estructura de carpetas y modelo de datos |
| 4 | `docs/02-requisitos-del-sistema.md` | Comportamiento esperado del sistema |
| 5 | `specs/SDD-00X-*.md` (incremento activo) | Alcance y entregables de la tarea actual |
| 6 | `AGENTS.md` | Convenciones de código y proceso |

Si hay contradicción entre dos niveles, el nivel más alto prevalece. Reporta siempre la contradicción antes de elegir.

---

## 4. Límites estrictos — lo que NO puedes hacer

### 4.1. Límites funcionales

- **No agregar funcionalidades** no listadas en `docs/01` sección 18 ni en el SDD activo.
- **No modificar fórmulas, umbrales ni factores** del motor sin actualizar `docs/03` primero.
- **No cambiar nombres de campos** de la API sin actualizar `docs/05` primero.
- **No implementar autenticación, roles ni panel administrativo**. El MVP no los requiere.
- **No mostrar datos históricos** al usuario. Los datos históricos son insumo interno del motor.
- **No generar texto libre** en tiempo de ejecución para las recomendaciones. Solo plantillas definidas en `docs/03` sección 10.

### 4.2. Límites arquitectónicos

- **No añadir microservicios** adicionales a los dos aprobados (STP y SMS).
- **El frontend no llama directamente** a Open-Meteo ni al SMS.
- **El SMS no accede** a la base de datos PostgreSQL.
- **El motor de estimación** vive exclusivamente en `services/prediction/app/core/`.
- **No usar SQLite** en producción ni en pruebas de integración (solo PostgreSQL de test).
- **No hardcodear credenciales** en código, Dockerfiles ni archivos de configuración.
- **No añadir dependencias** no listadas en `requirements.txt` o `package.json` sin justificación explícita en el commit.

### 4.3. Límites de calidad

- **No omitir pruebas**. Cada módulo nuevo debe tener pruebas antes de que el incremento se considere terminado.
- **No dejar el linter en rojo**. Cada commit debe pasar `ruff check .` (Python) y `eslint .` (JS) sin errores.
- **No mezclar responsabilidades** entre capas (la lógica del motor no puede estar en los routers de FastAPI).

---

## 5. Convenciones de código

### 5.1. Python (STP y SMS)

| Convención | Valor |
|---|---|
| Linter | `ruff` con configuración del proyecto |
| Formato | `ruff format` (compatible con Black) |
| Tipos | Anotaciones de tipo obligatorias en funciones públicas |
| Docstrings | Google style, en funciones públicas de `core/` |
| Imports | Agrupados: stdlib → third-party → local |
| Nombres de variables | `snake_case` |
| Nombres de clases | `PascalCase` |
| Constantes | `UPPER_SNAKE_CASE` |
| Archivos de prueba | `test_*.py` en directorio `tests/` del servicio |
| Framework de pruebas | `pytest` con fixtures en `conftest.py` |

**Reglas específicas del motor:**

- Las funciones en `core/estimation_engine.py` son puras: sin efectos secundarios, sin acceso a BD ni red.
- Las funciones en `core/synthetic_generator.py` son puras salvo la lectura del calendario.
- Los schemas Pydantic van en `schemas/`, no en los routers.

### 5.2. JavaScript / React (Frontend)

| Convención | Valor |
|---|---|
| Linter | ESLint con `eslint-plugin-react` |
| Formato | Prettier |
| Componentes | Functional components con hooks |
| Nombres de componentes | `PascalCase` |
| Nombres de hooks | `use` + `PascalCase` (p.ej. `useForecast`) |
| Nombres de archivos | `PascalCase.jsx` para componentes, `camelCase.js` para utilidades |
| Estilos | CSS Modules o CSS variables globales (sin Tailwind) |
| Estado global | Solo si es imprescindible; preferir props y context |
| Framework de pruebas | Vitest + React Testing Library |

**Reglas específicas del frontend:**

- El cliente HTTP está en `src/api/` y es el único lugar que conoce la URL del STP.
- Los componentes no contienen lógica de negocio del motor.
- Los textos visibles usan las cadenas definidas en `docs/05` sección 7.7 exactamente.

### 5.3. SQL y migraciones

- Todas las migraciones van en `services/prediction/alembic/versions/`.
- Cada migración tiene un mensaje descriptivo: `alembic revision -m "add daily_predictions table"`.
- No se modifican migraciones ya aplicadas; se crean nuevas.
- Los nombres de tablas son `snake_case` plural.
- Los nombres de columnas son `snake_case`.

---

## 6. Convenciones de commits

Formato: `tipo(alcance): descripción breve en español`

| Tipo | Cuándo usarlo |
|---|---|
| `feat` | Nueva funcionalidad |
| `fix` | Corrección de error |
| `test` | Añadir o corregir pruebas |
| `chore` | Configuración, dependencias, estructura |
| `docs` | Cambios solo en documentación |
| `refactor` | Refactorización sin cambio de comportamiento |
| `style` | Cambios de formato sin cambio de lógica |
| `migrate` | Nueva migración de base de datos |

**Ejemplos:**

```
feat(motor): implementar compute_convenience_score con penalizaciones meteorológicas
test(motor): agregar casos de prueba CP-01 a CP-07
chore(stp): configurar Dockerfile y requirements.txt iniciales
migrate(bd): agregar tabla daily_predictions
fix(sms): corregir manejo de timeout en cliente Open-Meteo
```

---

## 7. Comandos de validación

Ejecuta estos comandos para verificar que el trabajo está en orden antes de finalizar cada incremento:

### 7.1. Backend (Python)

```bash
# Desde la raíz del servicio (services/prediction/ o services/weather/)
ruff check .                          # linting
ruff format --check .                 # formato
pytest tests/ -v                      # pruebas unitarias e integración
pytest tests/ --cov=app/core --cov-report=term-missing  # cobertura
```

### 7.2. Frontend (JavaScript)

```bash
# Desde apps/dashboard/
eslint src/                           # linting
npx prettier --check src/            # formato
npx vitest run                        # pruebas de componentes
npx vite build                        # build de producción sin errores
```

### 7.3. Sistema completo (local)

```bash
# Desde la raíz del repositorio
docker-compose up -d
python scripts/smoke_test.py          # verifica todos los endpoints de salud
docker-compose down
```

### 7.4. Migración de base de datos

```bash
# Desde services/prediction/
alembic upgrade head                  # aplica migraciones pendientes
alembic current                       # verifica la versión actual
```

---

## 8. Procedimiento ante contradicciones o ambigüedades

Si encuentras una contradicción entre documentos o una ambigüedad que no puedes resolver con la jerarquía definida en la sección 3:

1. **Detén la implementación** de la parte afectada.
2. **Documenta la contradicción** claramente: qué dice documento A, qué dice documento B, en qué sección.
3. **Continúa** con las partes del incremento que no están afectadas por la contradicción.
4. **Reporta** la contradicción al finalizar el turno para que sea resuelta por el humano.

No inventes una solución ni elijas un documento arbitrariamente.

---

## 9. Definición de terminado (DoD) para agentes

Un incremento se considera **terminado** cuando:

- [ ] Todos los entregables del SDD correspondiente existen en el repositorio.
- [ ] Los criterios de terminado del SDD están verificados (puedes marcarlos uno a uno).
- [ ] Las pruebas del incremento pasan con `pytest` o `vitest run`.
- [ ] `ruff check .` pasa sin errores (Python).
- [ ] `eslint .` pasa sin errores (JavaScript, si aplica).
- [ ] No hay credenciales en el código ni en los archivos de configuración.
- [ ] El `docker-compose up` levanta los servicios afectados sin error.
- [ ] Los nombres de campos, rutas y estructuras de respuesta coinciden exactamente con `docs/05`.
- [ ] El código añadido no tiene responsabilidades mezcladas entre capas.
- [ ] Los commits del incremento tienen mensajes descriptivos según la convención de la sección 6.

---

## 10. Restricciones del MVP — lista de recordatorio

El agente debe recordar estas restricciones en todo momento:

- El sistema **no tiene** inicio de sesión, roles ni usuarios.
- El sistema **no tiene** panel administrativo.
- El sistema **no muestra** datos históricos al visitante.
- El sistema **no genera** texto libre de recomendaciones (solo plantillas).
- El sistema **no llama** a APIs de tráfico, mapas, autenticación ni entradas.
- El sistema **solo tiene** un destino en el MVP: `cueva-lechuzas`.
- El sistema **no predice** por horas, solo por días.
- El sistema **no usa** machine learning complejo.
- El frontend **no accede** a Open-Meteo directamente.
- El SMS **no accede** a la base de datos.

---

## 11. Estructura de carpetas de referencia rápida

```
tyto/
├── services/
│   ├── prediction/app/
│   │   ├── api/          ← routers FastAPI (solo enrutamiento, sin lógica)
│   │   ├── core/         ← motor y generador (lógica pura, sin red ni BD)
│   │   ├── db/           ← modelos SQLAlchemy y sesiones
│   │   └── schemas/      ← Pydantic schemas de request/response
│   └── weather/app/
│       ├── api/          ← router /internal/weather y /health
│       ├── adapters/     ← cliente Open-Meteo y normalizador
│       └── cache/        ← caché en memoria con TTL
├── apps/dashboard/src/
│   ├── api/              ← cliente HTTP hacia el STP (único punto de contacto)
│   ├── components/       ← DayCard, DaySelector, DayDetail, etc.
│   ├── hooks/            ← useForecast y otros hooks
│   └── pages/            ← página principal del dashboard
├── data/
│   ├── raw/              ← CSV oficial MINCETUR (nunca modificar)
│   ├── processed/        ← datasets normalizados
│   └── calendar/         ← peru_tourist_calendar.json
├── scripts/              ← import_monthly_data.py, generate_synthetic_data.py, smoke_test.py
├── specs/                ← SDD incrementales (SDD-001 a SDD-009)
├── docs/                 ← documentación del proyecto (01 a 06)
└── tests/                ← pruebas de integración entre servicios
```

---

## 12. Contacto con el humano

El agente debe solicitar intervención humana cuando:

- Encuentra una contradicción entre documentos (sección 8).
- El SDD activo no cubre un caso de borde relevante para la implementación.
- Una dependencia externa (Open-Meteo, AWS) tiene un comportamiento inesperado que requiere una decisión de diseño.
- El criterio de terminado de un entregable no puede verificarse con los comandos definidos.
- Se requiere acceso a credenciales, configuración de infraestructura o datos reales no disponibles en el repositorio.
