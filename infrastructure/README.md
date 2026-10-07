# Despliegue de Tyto en AWS

Plataforma aprobada: EC2 para STP, SMS, PostgreSQL 16 y Nginx; CloudFront para HTTPS de la API; Amplify Hosting para React/Vite. EC2 y `/health` por CloudFront están comprobados; Amplify y CORS definitivo siguen pendientes.

## Preparación

1. Elegir región y presupuesto; verificar permisos de EC2 y Amplify en la cuenta del curso. No se presupone gratuidad.
2. Crear una instancia Linux con Docker Engine y el plugin Compose. Dimensionar memoria según el consumo medido de los contenedores y del build.
3. Configurar el Security Group: HTTPS 443 y HTTP 80 públicos; SSH 22 solo desde la IP del operador. No abrir 5432, 8000 ni 8001.
4. Configurar DNS para `api.tu-dominio`, apuntando a la dirección pública estable de EC2.
5. Instalar un certificado TLS válido en `/etc/letsencrypt/live/api.tu-dominio/` y configurar renovación. El proxy necesita el certificado antes del primer arranque. Si se usa emisión standalone, el puerto 80 debe estar libre durante la emisión y renovación; después se debe recargar Nginx.
6. Clonar el repositorio en EC2. Copiar `infrastructure/.env.production.example` a `.env.production`, asignar una contraseña aleatoria y restringir permisos con `chmod 600 .env.production`. Completar dominio, origen del frontend y ruta TLS.

## Backend

Desde la raíz del repositorio, con certificados ya instalados:

```bash
docker compose --env-file .env.production -f infrastructure/compose.production.yml config --quiet
docker compose --env-file .env.production -f infrastructure/compose.production.yml build stp sms init
docker compose --env-file .env.production -f infrastructure/compose.production.yml up -d --wait db sms
docker compose --env-file .env.production -f infrastructure/compose.production.yml run --rm init
docker compose --env-file .env.production -f infrastructure/compose.production.yml up -d --wait stp proxy
docker compose --env-file .env.production -f infrastructure/compose.production.yml exec -T stp python /app/scripts/smoke_test.py --base-url http://stp:8000 --sms-url http://sms:8001
```

Para actualizar una versión publicada en Git, ejecutar `bash infrastructure/deploy.sh <tag-o-commit>`. El script respalda la base existente, reconstruye las imágenes y ejecuta migraciones y smoke interno. Validar también la API pública desde otro equipo.

## Frontend

### Si no hay dominio propio

Usar `compose.http.yml` en lugar de `compose.production.yml` para la API. El proxy
escucha en 80 y no requiere certificados. Los mismos comandos de build, init y arranque
se aplican cambiando el archivo Compose. La contraseña se genera en EC2 y se conserva
solo en `.env.production`. `CORS_ORIGINS=[]` es válido hasta conocer el origen Amplify.

En CloudFront crear una distribución para la API:

- Origin: DNS público de EC2 (sin `http://` ni rutas).
- Protocolo hacia el origen: HTTP only, puerto 80.
- Viewer protocol policy: Redirect HTTP to HTTPS.
- Métodos configurados: GET, HEAD, OPTIONS, PUT, POST, PATCH y DELETE. El MVP solo expone las operaciones definidas en sus contratos; permitir métodos en CloudFront no añade endpoints ni autorización.
- Cache policy: Managed-CachingDisabled.
- Origin request policy: Managed-AllViewerExceptHostHeader (reenvía Origin y parámetros).
- Sin dominio alternativo; usar el certificado y dominio `*.cloudfront.net` de AWS.
- Revisar el plan y cargos que presente la cuenta antes de crear la distribución.

Dominio actual comprobado: `https://d2ewwblip32s8m.cloudfront.net`. Utilizarlo como
`VITE_API_BASE_URL` en Amplify. Configurar en STP el origen exacto de Amplify y recrear
el servicio. El segmento CloudFront→EC2 sigue usando HTTP; un dominio propio permitirá
habilitar TLS al origen más adelante. Si cambia la IP pública de EC2 al detener/iniciar,
actualizar el origen CloudFront al nuevo DNS público.

Para esta modalidad, al ejecutar backup o deploy usar siempre el archivo HTTP;
los scripts existentes están dirigidos a la modalidad de dominio propio/TLS.

En Amplify Hosting, conectar el repositorio y la rama de despliegue como monorepo:

- `AMPLIFY_MONOREPO_APP_ROOT=apps/dashboard`.
- `VITE_API_BASE_URL=https://d2ewwblip32s8m.cloudfront.net`.
- Utilizar `amplify.yml` de la raíz: Node 22, `npm ci`, `npm run build`, artefactos `dist`.
- Copiar el origen HTTPS asignado por Amplify a `CORS_ORIGINS` en `.env.production` como lista JSON y recrear STP.
- Las variables VITE son públicas. Una modificación de URL requiere recompilar.

Verificar la carga de siete días desde la API real, selección del día, estado degradado, CORS y ausencia de contenido HTTP en la página HTTPS.

Referencia: [configuración de monorepos en Amplify](https://docs.aws.amazon.com/amplify/latest/userguide/monorepo-configuration.html).

## Respaldo y cierre

`bash infrastructure/backup.sh` genera un dump local. Antes de publicar, programar su ejecución, conservar una copia fuera de la instancia (por ejemplo, S3 privado con acceso IAM restringido) y probar la restauración en una base de pruebas. Un dump en la misma VM no protege frente a pérdida de la instancia.

Después de la demostración, conservar los datos necesarios y retirar los recursos que ya no se utilicen: EC2, volúmenes EBS, direcciones públicas, snapshots y aplicación Amplify. Revisar la consola de facturación; detener EC2 no elimina los demás recursos.
