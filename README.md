# Tyto

API de demostración: `https://d2ewwblip32s8m.cloudfront.net`.
Salud pública comprobada en `/health`. CloudFront conecta por HTTP a EC2
en us-east-2 (`18.189.194.199`); el frontend Amplify sigue pendiente.
La IP automática de EC2 puede cambiar al iniciar desde estado detenido;
actualizar entonces el origen CloudFront al nuevo DNS público.

MVP para estimar la afluencia diaria a la Cueva de las Lechuzas. El repositorio contiene dos servicios FastAPI, un dashboard React/Vite, PostgreSQL, migraciones Alembic, datos sintéticos reproducibles y la configuración para desplegar el conjunto en Amazon EC2 con el frontend en AWS Amplify Hosting.

## Estructura

- `services/prediction`: STP, motor de estimación, API pública, persistencia y migraciones.
- `services/weather`: SMS, cliente Open-Meteo, normalización y caché TTL.
- `apps/dashboard`: interfaz React que únicamente consume la API del STP.
- `data`: CSV fuente, calendario turístico y parámetros versionados del motor.
- `scripts`: importación, generación, bootstrap y smoke test.
- `infrastructure`: compose de producción, Nginx y scripts de despliegue/backup.
- `docs` y `specs`: alcance, contratos, decisiones y SDDs incrementales.

## Ejecución local

1. Copia `.env.example` a `.env` y completa los valores locales.
2. Levanta PostgreSQL y aplica las migraciones:

   ```powershell
   .venv\Scripts\alembic.exe -c services\prediction\alembic.ini upgrade head
   .venv\Scripts\python.exe scripts\bootstrap_data.py
   ```

3. Levanta SMS en `:8001` y STP en `:8000` con `PYTHONPATH` apuntando al servicio. También puedes usar `docker compose up -d` si Docker está instalado.
4. En Docker, SMS es privado. Comprueba el conjunto con `docker compose exec -T stp python /app/scripts/smoke_test.py --base-url http://stp:8000 --sms-url http://sms:8001`. Abre `http://localhost:8080` (origen autorizado por CORS).
5. Para el dashboard:

   ```powershell
   cd apps/dashboard
   npm install
   npm run dev
   ```

## Validación

Por decisión del usuario, las nuevas pruebas requieren planificación previa.
El workflow de GitHub se ejecuta manualmente desde Actions (`workflow_dispatch`).

Para ejecutar las pruebas de servicios, calidad e integración con PostgreSQL aislado: `docker compose -f docker-compose.validation.yml up --build --abort-on-container-exit --exit-code-from checks`. Usa la contraseña definida en tu `.env`; los datos de prueba son efímeros y no afectan al volumen local de Tyto.

Los comandos de validación y los resultados de la última ejecución están documentados en [docs/08-validacion-del-mvp.md](docs/08-validacion-del-mvp.md). El flujo de despliegue que requiere credenciales externas se describe en [docs/07-preparacion-paralela-del-desarrollo-y-despliegue.md](docs/07-preparacion-paralela-del-desarrollo-y-despliegue.md).

## Configuración

Las credenciales y URLs se leen desde variables de entorno. `.env` está excluido por `.gitignore`; `.env.example` contiene únicamente valores de referencia. La aplicación no incluye credenciales de producción ni intenta crear recursos en AWS sin una sesión configurada.
