# SDD-002 — importacion-datos-oficiales

Estado: en implementación. Autorización: solicitud integral del usuario, 2026-10-06.

## Objetivo y alcance

Modelos, Alembic, seed e importación idempotente del CSV existente. Entregables y archivos: docs/06, fase 2; estructura: docs/04 §7.
Requisitos: docs/02; interfaces: docs/05 incluida §9; fórmulas: docs/03 incluida §16.

## Diseño y casos límite

Aplicar las precisiones normativas 0.2, preservar límites STP/SMS/frontend y distinguir
datos ausentes de cero. Sin SQLite, secretos versionados, autenticación ni historial público.
Casos: errores de proveedor, datos incompletos, fechas Lima, reejecución y entradas inválidas
según corresponda a esta fase. Dependencias: fases anteriores según docs/06 §4.

## Aceptación

- [ ] Entregables de fase 2 presentes.
- [ ] 56 meses, estados, duplicados y restricciones PostgreSQL.
- [ ] Linters y pruebas aplicables pasan.
- [ ] Evidencia y limitaciones registradas en docs/08-validacion-del-mvp.md.

La publicación externa depende de cuentas autorizadas y no se declara comprobada sin URL.
