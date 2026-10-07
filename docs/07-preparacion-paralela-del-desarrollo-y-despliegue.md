# Preparación en paralelo al desarrollo de Tyto

**Fecha:** 2026-10-06  
**Estado:** AWS aprobado; preparación de accesos pendiente  
**Objetivo:** Preparar los recursos, accesos y acuerdos necesarios mientras se desarrolla el MVP.

Este documento complementa `docs/00`–`docs/06` y `AGENTS.md`. No modifica las fórmulas, los contratos ni la arquitectura aprobada. Las propuestas indicadas aquí deben resolverse y reflejarse en los documentos correspondientes antes de implementar la parte afectada.

## 1. Qué puedes preparar desde ahora

Las tareas de esta lista pueden hacerse mientras se prepara o construye el código. No necesitas esperar a tener el backend ni el frontend terminados.

| Prioridad | Tarea | Resultado que debes tener |
|---|---|---|
| 1 | Preparar la cuenta AWS del curso | AWS aprobado por el usuario |
| 2 | Preparar el equipo local | Git, Docker con Compose, Python y Node disponibles |
| 3 | Preparar GitHub | Repositorio, visibilidad elegida y acceso desde tu equipo |
| 4 | Preparar la cuenta de nube elegida | Cuenta accesible, región y presupuesto definidos |
| 5 | Preparar Amplify si se elige esa alternativa | Cuenta y acceso al repositorio para desplegar el frontend |
| 6 | Resolver el nombre público de la API | Dominio o subdominio con control de DNS |
| 7 | Confirmar la procedencia de los datos | Fuente, fecha de descarga y correspondencia con el destino |
| 8 | Reunir fuentes oficiales del calendario | Feriados y excepciones de 2022–2026 con referencias |
| 9 | Organizar las evidencias académicas | Requisitos del video, fecha de entrega y forma de demostrar el sistema |

## 2. Plataforma aprobada

El usuario aprobó centralizar Tyto en AWS: EC2 para STP, SMS y PostgreSQL; Amplify Hosting para el frontend. Se descartan los anexos anteriores de otros proveedores. Región, presupuesto y acceso a la cuenta siguen pendientes.

## 3. Equipo local

- [ ] Git instalado y configurado con tu identidad de autor.
- [ ] Docker Desktop operativo, con contenedores Linux y Docker Compose.
- [ ] Python 3.12 disponible.
- [ ] Node.js compatible con el stack de React 18 + Vite 5 definido en `docs/04`.
- [ ] Puertos locales 8000 y 8001 disponibles para STP y SMS; el puerto del frontend y el de PostgreSQL se definirán en Compose.
- [ ] Espacio disponible para imágenes, contenedores y volúmenes de base de datos.

Comprobaciones desde PowerShell:

```powershell
git --version
docker version
docker compose version
python --version
node --version
npm --version
```

`docker version` debe poder comunicarse con el motor, además de mostrar la versión del cliente. No es necesario instalar PostgreSQL directamente en Windows: el entorno previsto utiliza contenedores.

**Resultado esperado:** el equipo puede compilar el frontend y ejecutar STP, SMS y PostgreSQL con Compose. Estos comandos comprueban herramientas; no sustituyen las pruebas del sistema.

## 4. GitHub

- [ ] Tener acceso a tu cuenta de GitHub.
- [ ] Crear o identificar el repositorio de Tyto.
- [ ] Confirmar si el curso exige un repositorio público.
- [ ] Comprobar que puedes hacer push desde tu equipo usando un método autorizado.
- [ ] Anotar la URL del repositorio y la rama que se usará para producción.
- [ ] Si se usa AWS Amplify Hosting, autorizar su acceso únicamente al repositorio necesario.

El repositorio contendrá código, documentación, plantillas de configuración y fuentes de datos autorizadas. Los archivos con secretos reales deben excluirse mediante `.gitignore` antes de publicar.

**Bloquea:** sincronizar el código con GitHub y configurar despliegues conectados al repositorio. No bloquea el desarrollo local.

## 5. Preparación de AWS

- [ ] Cuenta AWS y permisos EC2/Amplify disponibles.
- [ ] Región, presupuesto y tiempo de publicación definidos.
- [ ] Repositorio y rama conectados a Amplify; raíz apps/dashboard.
- [ ] Instancia Linux con Docker Compose y volumen PostgreSQL persistente.
- [ ] Dominio HTTPS de API y CORS configurados.
- [ ] Respaldos fuera de EC2 y restauración comprobada.

Procedimiento y variables: infrastructure/README.md. La existencia de archivos no implica un despliegue verificado.

## 7. Dominio, HTTPS y acceso de red

- [ ] Identificar un dominio o subdominio para la API y quién puede modificar sus registros DNS.
- [ ] Si no tienes dominio, resolver una alternativa de URL HTTPS antes de configurar la publicación del backend.
- [ ] Cuando exista la VM, apuntar el registro DNS de la API a su dirección pública.
- [ ] Preparar el certificado TLS y su renovación.
- [ ] Configurar el origen exacto del frontend en CORS.

Para la plataforma AWS, la exposición prevista es:

```text
Navegador → AWS Amplify Hosting
Navegador → HTTPS → Nginx → STP
                            ├── SMS → Open-Meteo
                            └── PostgreSQL
```

Nginx expondrá la API pública por HTTPS. SMS y PostgreSQL permanecerán en la red privada de Docker. El acceso SSH se restringirá a los administradores autorizados. Las reglas deberán configurarse tanto en AWS como en el firewall del sistema operativo.

**Bloquea:** la conexión pública del frontend con la API y la validación del certificado. No bloquea las pruebas locales.

## 8. Datos y calendario

### Datos mensuales ya disponibles

La carpeta contiene:

- `data/raw/Tabla_data.csv`.
- `data/processed/visitas_mensuales_modelo.csv` con 56 registros, desde enero de 2022 hasta agosto de 2026.
- `data/processed/visitas_mensuales_completas.csv`.
- `data/reports/calidad_datos_mensuales.json`.
- El script de normalización y sus pruebas en `scripts/`.

La existencia del CSV y del reporte permite preparar la importación; no sustituye confirmar su procedencia oficial.

- [ ] Registrar la URL o identificación de la publicación de MINCETUR y la fecha de descarga.
- [ ] Confirmar que el archivo corresponde al sector Cueva de las Lechuzas.
- [ ] Conservar el archivo original sin modificarlo.
- [ ] Confirmar permiso de redistribución o requisitos de atribución para el repositorio público.

### Calendario turístico

- [ ] Reunir referencias oficiales de feriados nacionales de cada año, 2022–2026.
- [ ] Diferenciar feriados de días no laborables y puentes oficiales.
- [ ] Reunir periodos especiales y eventos locales solo cuando exista una referencia verificable.
- [ ] Confirmar el tratamiento de feriados largos según `docs/03`, sección 4.4.
- [ ] Verificar los enlaces oficiales de información, entradas y cómo llegar del destino.

El archivo `data/calendar/peru_tourist_calendar.json` ya existe; falta cerrar la revisión de sus fuentes. Las excepciones y sus referencias deben quedar versionadas. No se necesita una API externa de calendario.

## 9. Decisiones técnicas que deben cerrarse durante la preparación

Estas tareas corresponden a la revisión de especificaciones. Puedes resolverlas con apoyo del agente; no necesitas programar sus soluciones manualmente.

| Documento | Punto pendiente | Por qué importa |
|---|---|---|
| `03`, §4.5 | El factor de temporada constante se cancela al normalizar dentro de un mes | Debe aclararse su efecto real antes de atribuirle influencia en la distribución |
| `03`, §4.6 | Parámetros exactos de Lehmer y representación de la semilla | Permiten reproducir el mismo resultado entre implementaciones |
| `03`, §4.8 | Redondeo, desempate por peso y corrección para totales pequeños | Debe conservarse el total sin generar visitantes negativos |
| `03`, §5 | Método del percentil 95 y comportamiento si vale cero | Evita diferencias de cálculo y división entre cero |
| `03`, §7.4 | Rangos UV con valores decimales | Valores como 6.5 y 9.5 no quedan cubiertos por la tabla actual |
| `03`, §9 | Empates con diferencia de hasta un punto y puntuaciones nulas | La selección semanal necesita una regla inequívoca |
| `03`, CP-03 y CP-04 | Completar las variables de entrada | Los resultados esperados no se deducen de los datos parciales actuales |
| `04` y `05` | Persistencia de la respuesta meteorológica original | La BD la exige, pero el contrato SMS→STP no la transmite |
| `05`, API pública y detalle visual | Sensación térmica y horas de lluvia | El diseño las muestra, pero faltan en la respuesta pública |
| `03` y `05` | Ausencia de historial en parte o toda la semana | Falta cerrar cuándo responder degradado, cómo elegir un día y cuándo devolver 503 |
| `00`, `06` y `AGENTS.md` | SDD y seguimiento incremental | Las reglas actuales requieren especificaciones por incremento |

Cualquier cambio de fórmulas debe actualizar primero `docs/03`; cualquier cambio de contrato, `docs/05`. No se resolverán estas diferencias solo en el código.

## 10. Configuración que preparará el desarrollo

Cuando se autorice la implementación, el trabajo de configuración incluirá:

- Plantillas `.env.example`, sin secretos reales.
- Dockerfiles de STP, SMS y frontend.
- Compose local y Compose de pruebas con PostgreSQL aislado.
- Configuración de producción para la plataforma elegida.
- Variables documentadas para conexión a BD, URL interna del SMS, TTL de caché, logs, URL pública de API y orígenes CORS.
- Migraciones Alembic y procedimiento de carga inicial de datos.
- Configuración de Nginx y TLS si se utiliza la instancia EC2.
- Procedimiento de respaldo, restauración y actualización por una versión identificable del código.
- `infrastructure/README.md`, script de despliegue y comprobaciones de salud.

La cuenta de nube, el acceso autorizado, DNS y los secretos deben estar disponibles para ejecutar el despliegue. La preparación de archivos no implica que la infraestructura ya exista ni que la publicación esté verificada.

## 11. Información que puedes entregar para continuar

Completa esta ficha con información no sensible:

```text
Plataforma admitida por el curso:
Referencia o confirmación del profesor:
Fecha de entrega:
Tiempo que debe permanecer publicada la aplicación:
Presupuesto máximo:
URL del repositorio GitHub:
Visibilidad requerida del repositorio:
Rama prevista para producción:
Cuenta de nube preparada: sí / no
Región elegida:
VM disponible y arquitectura, si aplica:
Amplify preparado, si aplica: sí / no
Dominio o subdominio para la API:
Acceso a DNS: sí / no
Fuente y fecha de descarga del CSV:
Referencias disponibles para el calendario:
Decisión pendiente sobre la BD:
Limitaciones del equipo o permisos del laboratorio:
```

**No incluyas contraseñas, claves SSH privadas, tokens ni cadenas de conexión con secretos en esta ficha, el chat o el repositorio.** Los valores reales se configurarán en el entorno correspondiente mediante un mecanismo autorizado.

## 12. Cuándo estará lista la preparación

- [ ] Plataforma académica y presupuesto confirmados.
- [ ] Equipo local operativo.
- [ ] Repositorio y acceso a GitHub preparados.
- [ ] Procedencia de datos confirmada y fuentes de calendario reunidas.
- [ ] Contradicciones de documentación resueltas para la fase que se vaya a implementar.
- [ ] Cuenta, capacidad de nube y base de datos decididas antes del despliegue.
- [ ] URL HTTPS de API y origen del frontend definidos antes de la publicación.
- [ ] Secretos disponibles fuera del repositorio.

El desarrollo puede avanzar por fases mientras se prepara la infraestructura. El MVP solo se considerará desplegado después de verificar la API pública, el dashboard y la prueba de humo en el entorno final, según `docs/06`.

