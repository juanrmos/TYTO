# Validación del MVP

Este documento registra la validación ejecutada sobre la implementación actual y separa los controles locales de los pasos que dependen de infraestructura externa.

## Controles ejecutados

| Área | Comando | Resultado |
|---|---|---|
| STP e integración PostgreSQL | Compose de validación, pytest | 59 pruebas aprobadas; cobertura de core 100 % |
| SMS | Compose de validación, pytest | 14 pruebas aprobadas con Python 3.12 |
| Python | `.venv\Scripts\python.exe -m ruff check services scripts` | Sin errores |
| Formato Python | `.venv\Scripts\python.exe -m ruff format --check services scripts` | Sin cambios pendientes |
| Dashboard | `npm.cmd run lint` | Sin errores |
| Dashboard | `npm.cmd test` | 9 pruebas aprobadas |
| Dashboard | `npm.cmd run build` | Build de producción generado |
| Base de datos | `alembic upgrade head` + `scripts/bootstrap_data.py` | 56 meses y 1704 días cargados |

El smoke test completo pasó dentro de Docker: salud STP, destinos, siete días, mejor opción, salud extendida y SMS. La API pública local respondió con siete días de meteorología obtenida realmente de Open-Meteo. El dashboard respondió HTTP 200 en `http://localhost:8080`.

Playwright pasó contra la API real: siete tarjetas, selección por teclado, detalle, tamaño táctil y ausencia de desbordamiento de página a 375 px. Se inspeccionaron las capturas de escritorio y móvil en `apps/dashboard/test-results/` (archivos ignorados por Git).

## Criterios verificados

- Las fórmulas viven en `services/prediction/app/core` y no acceden a red ni base de datos.
- El dashboard llama solamente al STP.
- SMS no contiene acceso a PostgreSQL.
- Los nombres y estructuras de la API siguen los contratos de `docs/05`.
- No se incluyeron autenticación, roles, panel administrativo, predicción horaria ni datos históricos visibles.
- Las credenciales se resuelven desde entorno y no están versionadas.

## Pendiente externo

### Avance de despliegue EC2

Se conectó por SSH a la instancia del usuario en us-east-2, con IPv4 pública
18.189.194.199. Memoria observada: 3,7 GiB; volumen EBS 20 GiB, raíz ext4 ampliada.
Se instaló Docker Engine 29.8.2 y Compose 5.6.0 desde el repositorio oficial.
El código se transfirió mediante un archivo que excluye secretos y artefactos locales;
no es todavía una publicación Git ni un despliegue automático desde GitHub.
Se generó `.env.production` solo en EC2 con contraseña aleatoria y permisos restringidos.
Se aplicaron migraciones y carga inicial, y se levantaron DB, STP, SMS y Nginx HTTP.
La comprobación pública de `/health` respondió con status ok. No se ejecutaron suites
ni pruebas de carga o persistencia, siguiendo la instrucción posterior del usuario.
CloudFront está configurado en `https://d2ewwblip32s8m.cloudfront.net` y `/health`
respondió con `status=ok`, `service=stp`, `version=1.0.0` mediante HTTPS.
El origen utiliza HTTP 80, la caché está desactivada y WAF no está habilitado.
El origen CORS definitivo y el dashboard Amplify siguen pendientes.

### Actualización de entorno y plataforma (2026-10-06)

- Docker Desktop instalado mediante winget; Docker CLI 29.8.2 y Compose v5.5.1 comprobados.
- Las configuraciones Compose local y de producción pasan `config --quiet`.
- El usuario completó WSL y Docker Desktop está operativo. `compose up -d --build` construyó y levantó STP, SMS, PostgreSQL y dashboard; init terminó correctamente.
- `docker-compose.validation.yml` usa una base PostgreSQL efímera aislada, aplica migraciones, importa datos y ejecuta Ruff y pruebas. La integración verifica persistencia de 14 predicciones y un snapshot tras consultas normal y degradada, así como errores 400/404/422. Pasó sin SQLite.
- Prettier pasó en la validación previa. `.github/workflows/validate.yml` se configura con ejecución manual para respetar la decisión de no realizar nuevas pruebas sin planificación. La auditoría completa de requisitos y los criterios restantes de los SDD siguen pendientes.
- La plataforma aprobada es AWS EC2 + CloudFront + Amplify Hosting. `amplify.yml` está preparado; EC2 y la URL HTTPS de la API están operativos según las comprobaciones anteriores.

Quedan pendientes la publicación del frontend en Amplify y su origen CORS en STP.
La modalidad actual sin dominio propio usa `infrastructure/compose.http.yml`;
los scripts `deploy.sh` y `backup.sh` corresponden a la modalidad TLS con dominio propio.
