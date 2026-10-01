# Mapa de construibles y preparación para desarrollar el MVP con IA

**Versión:** 0.1  
**Estado:** Documento de planificación  
**Documentos relacionados:**

- `01-definicion-y-alcance-del-proyecto.md`
- `02-requisitos-del-sistema.md`

---

## 1. Propósito

Este documento identifica todos los elementos construibles del proyecto y establece qué decisiones deben cerrarse antes de solicitar a un agente de inteligencia artificial que implemente el primer MVP completo.

El objetivo no es exigir que todos los elementos se desarrollen simultáneamente. El mapa permite:

- Conocer el producto completo que debe entregarse.
- Diferenciar documentación, software, datos, infraestructura y evidencias.
- Identificar qué elementos bloquean el inicio del desarrollo.
- Dividir el trabajo en incrementos pequeños y verificables.
- Evitar que los agentes introduzcan decisiones técnicas o funcionales no aprobadas.
- Mantener trazabilidad entre alcance, requisitos, diseño, código y pruebas.

---

# 2. Lista completa de construibles

Los construibles se organizan en nueve grupos: documentación, repositorio, datos, backend, frontend, pruebas, infraestructura, operación y entregables académicos.

## 2.1. Documentación de producto y requisitos

### Ya disponibles

1. `01-definicion-y-alcance-del-proyecto.md`
   - Contexto del proyecto.
   - Problema y objetivos.
   - Alcance global.
   - Alcance del MVP.
   - Fuentes de información.
   - Funcionalidades incluidas y excluidas.
   - Limitaciones y decisiones cerradas.

2. `02-requisitos-del-sistema.md`
   - Actores.
   - Casos de uso.
   - Requisitos funcionales.
   - Requisitos de datos.
   - Requisitos de integración.
   - Requisitos de interfaz.
   - Requisitos no funcionales.
   - Reglas de negocio.
   - Criterios de aceptación.
   - Matriz de trazabilidad.

### Pendientes antes o durante la implementación

3. `03-especificacion-motor-estimacion.md`
   - Preparación de datos mensuales.
   - Generación diaria sintética.
   - Conservación de totales mensuales.
   - Factores de calendario.
   - Variables meteorológicas.
   - Puntuación de afluencia.
   - Puntuación de conveniencia.
   - Selección de la mejor opción.
   - Ejemplos matemáticos.
   - Casos de prueba del motor.

4. `04-arquitectura-y-modelo-de-datos.md`
   - Contexto del sistema.
   - Componentes y microservicios.
   - Responsabilidades.
   - Comunicación.
   - Propiedad de datos.
   - Diagrama de arquitectura.
   - Modelo de datos.
   - Diagrama entidad-relación.
   - Decisiones arquitectónicas.

5. `05-contratos-api-y-diseno-interfaz.md`
   - Endpoints públicos e internos.
   - Solicitudes y respuestas.
   - Enumeraciones y errores.
   - Zona horaria y formatos de fecha.
   - Wireframe de escritorio.
   - Wireframe móvil.
   - Estados de carga, error y datos incompletos.
   - Reglas visuales de las siete tarjetas.

6. `06-plan-implementacion-pruebas-y-despliegue.md`
   - Fases de implementación.
   - Dependencias entre fases.
   - Estrategia de pruebas.
   - Criterios de terminado.
   - Estrategia de despliegue en AWS.
   - Evidencias necesarias para el video.

7. `AGENTS.md`
   - Fuentes de verdad del repositorio.
   - Orden de lectura de documentos.
   - Convenciones de desarrollo.
   - Límites arquitectónicos.
   - Comandos de validación.
   - Reglas para modificar código y documentación.
   - Definición de terminado para agentes.

8. Registros de decisiones arquitectónicas, si fueran necesarios:

```text
docs/adr/
├── ADR-001-seleccion-stack.md
├── ADR-002-limites-microservicios.md
├── ADR-003-persistencia.md
└── ADR-004-despliegue-aws.md
```

Estos registros serán breves y solo se crearán para decisiones con alternativas relevantes.

---

## 2.2. Especificaciones ejecutables para agentes

Se crearán progresivamente, no todas antes de comenzar:

```text
specs/
├── SDD-001-preparacion-repositorio.md
├── SDD-002-importacion-datos-oficiales.md
├── SDD-003-generacion-diaria-sintetica.md
├── SDD-004-motor-estimacion.md
├── SDD-005-integracion-meteorologica.md
├── SDD-006-api-semanal.md
├── SDD-007-dashboard-web.md
├── SDD-008-integracion-y-pruebas.md
└── SDD-009-despliegue-aws.md
```

Cada SDD deberá contener:

- Objetivo.
- Requisitos relacionados.
- Alcance del incremento.
- Diseño propuesto.
- Archivos afectados.
- Interfaces.
- Casos límite.
- Pruebas requeridas.
- Criterios de aceptación.
- Elementos fuera de alcance.

Las skills se crearán después de identificar procedimientos repetitivos reales. Posibles skills futuras:

```text
importar-datos-oficiales
regenerar-dataset-diario
validar-conservacion-mensual
ejecutar-pruebas-del-motor
desplegar-entorno-aws
```

---

## 2.3. Estructura y configuración del repositorio

1. Repositorio GitHub.
2. Estructura de monorepo.
3. Archivo `README.md`.
4. Archivo `LICENSE`, si corresponde.
5. Archivo `.gitignore`.
6. Archivos `.editorconfig` y de formato.
7. Plantilla de variables de entorno `.env.example`.
8. Configuración de linters y formateadores.
9. Configuración de pruebas.
10. Configuración de compilación.
11. Archivos Docker de los componentes desplegables.
12. Archivo de composición local para desarrollo.
13. Workflows de integración y despliegue continuo.
14. Plantillas de incidencias o tareas, si se consideran útiles.
15. Convenciones de ramas y commits documentadas.

Estructura conceptual:

```text
project-root/
├── apps/
├── services/
├── packages/
├── data/
├── scripts/
├── infrastructure/
├── docs/
├── specs/
├── tests/
├── .github/
├── AGENTS.md
├── README.md
└── .env.example
```

La estructura definitiva dependerá de la arquitectura y las tecnologías seleccionadas.

---

## 2.4. Construibles de datos

### Datos de entrada

1. Copia controlada del archivo oficial original.
2. Archivo filtrado para el Parque Nacional de Tingo María y la Cueva de las Lechuzas.
3. Registros mensuales normalizados desde enero de 2022 hasta agosto de 2026.
4. Metadatos de la fuente y fecha de recuperación.
5. Calendario turístico local.
6. Configuración de reglas del motor.
7. Coordenadas y datos básicos del destino.
8. Enlaces oficiales del destino.

### Procesos de datos

9. Script de inspección del CSV oficial.
10. Script de limpieza y normalización.
11. Script de validación de columnas y tipos.
12. Script de detección de duplicados y valores ausentes.
13. Script de importación a la base de datos.
14. Script de generación diaria sintética.
15. Script de validación de conservación mensual.
16. Script de regeneración controlada cuando cambien las reglas.
17. Reporte de calidad de los datos procesados.

### Datos derivados

18. Dataset mensual normalizado.
19. Dataset diario sintético reproducible.
20. Registro de versión del generador.
21. Registro de parámetros utilizados.
22. Evidencia de que la suma diaria coincide con cada total mensual.
23. Datos semilla para desarrollo y pruebas.
24. Fixtures para pruebas automatizadas.

---

## 2.5. Construibles del backend y microservicios

La división definitiva se decidirá en la arquitectura. Funcionalmente deben existir los siguientes componentes, aunque no todos tienen que convertirse en microservicios independientes:

1. Módulo o servicio de destinos turísticos.
2. Módulo de consulta de registros históricos.
3. Módulo de consulta de datos diarios sintéticos.
4. Motor de estimación de afluencia.
5. Motor de conveniencia de visita.
6. Selector de mejor opción semanal.
7. Generador de explicaciones mediante plantillas.
8. Adaptador del calendario turístico local.
9. Cliente o adaptador de la API meteorológica.
10. Normalizador de códigos y variables meteorológicas.
11. Mecanismo de reutilización temporal del pronóstico.
12. API pública para el dashboard semanal.
13. API o mecanismo interno entre servicios.
14. Persistencia de registros mensuales.
15. Persistencia de datos sintéticos.
16. Persistencia o caché de instantáneas meteorológicas.
17. Persistencia de predicciones, si la arquitectura lo requiere.
18. Validaciones de entrada y salida.
19. Manejo de errores.
20. Registro de eventos y fallos.
21. Endpoints de salud.
22. Documentación OpenAPI o equivalente.

### Operación principal esperada

La API principal deberá proporcionar, en una sola respuesta coherente:

- Datos básicos del destino.
- Fecha y hora de generación.
- Los siete días evaluados.
- Afluencia y nivel de cada día.
- Conveniencia y recomendación de cada día.
- Resumen meteorológico.
- Factores principales.
- Mejor opción o mejor alternativa.
- Advertencias necesarias.
- Enlaces oficiales.

---

## 2.6. Construibles del frontend

1. Aplicación web pública.
2. Página principal o dashboard de decisión.
3. Encabezado del destino.
4. Panel del día seleccionado.
5. Tarjeta de puntuación de afluencia.
6. Tarjeta de conveniencia.
7. Resumen meteorológico.
8. Recomendación textual.
9. Lista de factores principales.
10. Selector de siete días.
11. Tarjetas con codificación verde, ámbar y roja.
12. Etiqueta de mejor opción.
13. Estado de mejor alternativa cuando ningún día sea recomendable.
14. Enlaces oficiales.
15. Advertencia metodológica.
16. Estado de carga.
17. Estado de error meteorológico.
18. Estado de datos incompletos.
19. Estado sin recomendación completa.
20. Diseño adaptable a escritorio.
21. Diseño adaptable a teléfonos móviles.
22. Accesibilidad básica de colores, textos y controles.
23. Cliente de la API del backend.
24. Manejo de configuración por entorno.
25. Iconografía y elementos visuales necesarios.
26. Metadatos básicos de la aplicación web.

El MVP no requiere:

- Inicio de sesión.
- Página de perfil.
- Panel administrativo.
- Sección histórica.
- Calendario abierto para fechas futuras.
- Procesamiento de pagos.

---

## 2.7. Construibles de pruebas y calidad

### Pruebas de datos

1. Validación del esquema del archivo oficial.
2. Detección de duplicados.
3. Tratamiento de datos ausentes.
4. Diferenciación entre cero y dato no publicado.
5. Verificación del periodo desde 2022.

### Pruebas del generador sintético

6. Reproducibilidad.
7. Conservación mensual.
8. Ajustes de redondeo.
9. Meses de 28, 29, 30 y 31 días.
10. Fines de semana.
11. Feriados y periodos especiales.

### Pruebas del motor

12. Afluencia baja, media y alta.
13. Conveniencia recomendada, con precaución y no recomendada.
14. Independencia entre afluencia y conveniencia.
15. Clima favorable con alta afluencia.
16. Baja afluencia con clima adverso.
17. Selección de la mejor opción.
18. Semana completamente desfavorable.
19. Desempate por menor afluencia.
20. Desempate por fecha más cercana.
21. Generación de explicaciones coherentes.

### Pruebas de integración

22. Transformación de la respuesta meteorológica.
23. Respuesta semanal completa.
24. Manejo de pronóstico incompleto.
25. Manejo de error del proveedor.
26. Persistencia y lectura de datos.
27. Contratos entre servicios.

### Pruebas del frontend

28. Selección inicial de hoy.
29. Cambio entre tarjetas.
30. Colores y categorías textuales.
31. Etiqueta de mejor opción.
32. Mejor alternativa desfavorable.
33. Renderizado de enlaces oficiales.
34. Diseño en escritorio.
35. Diseño en móvil.
36. Accesibilidad básica.

### Calidad general

37. Linting.
38. Formato.
39. Comprobación de tipos.
40. Pruebas unitarias.
41. Pruebas de integración.
42. Prueba de humo en el entorno desplegado.
43. Reporte de cobertura, si resulta viable.

---

## 2.8. Construibles de infraestructura y operación

1. Cuenta o entorno de AWS configurado.
2. Región de despliegue seleccionada.
3. Registro de imágenes de contenedor.
4. Servicio de ejecución de los microservicios.
5. Alojamiento del frontend.
6. Distribución pública del frontend.
7. Base de datos administrada o alternativa justificada.
8. Configuración de red.
9. Reglas de acceso.
10. Variables de entorno.
11. Gestión de secretos.
12. Centralización de logs.
13. Métricas básicas.
14. Alarmas mínimas, si el tiempo lo permite.
15. Endpoints de salud.
16. Pipeline de integración continua.
17. Pipeline de despliegue.
18. Infraestructura como código o procedimiento reproducible.
19. Procedimiento de creación del entorno.
20. Procedimiento de actualización.
21. Procedimiento de eliminación para evitar costos innecesarios.
22. Presupuesto o límites de costo.
23. URL pública del sistema.
24. Evidencia del despliegue operativo.

No se requiere Kubernetes para el MVP, salvo que posteriormente exista una justificación fuerte.

---

## 2.9. Construibles de entrega académica

1. Repositorio GitHub organizado.
2. Código fuente.
3. Historial de commits.
4. README con instrucciones de ejecución.
5. Documentación del proyecto.
6. Aplicación desplegada en AWS.
7. URL de demostración.
8. Diagrama de arquitectura.
9. Diagrama del flujo principal.
10. Diagrama de datos.
11. Evidencia del uso de base de datos.
12. Evidencia del consumo de la API meteorológica.
13. Evidencia de la arquitectura de microservicios.
14. Video del proceso de construcción.
15. Video o sección del video orientada al usuario.
16. Guion del video.
17. Datos o ejemplos preparados para la demostración.
18. Lista de limitaciones metodológicas.
19. Referencias a las fuentes oficiales.
20. Instrucciones para reproducir la demostración.

---

# 3. Qué falta definir antes de producir el MVP completo con IA

## 3.1. Motor académico de estimación

Es la principal incertidumbre funcional pendiente. Deben definirse los siguientes puntos.

### Referencia mensual

- Cómo combinar el mismo mes de diferentes años.
- Si se utilizará promedio, mediana o ponderación temporal.
- Si los años recientes tendrán mayor peso.
- Cómo tratar meses incompletos o no disponibles.

### Distribución diaria sintética

- Peso de cada día de la semana.
- Incremento de fines de semana.
- Tratamiento de feriados.
- Tratamiento de periodos especiales.
- Variación sintética controlada.
- Semilla de reproducibilidad.
- Corrección de redondeos.
- Conservación exacta del total mensual.

### Puntuación de afluencia

- Transformación de la cantidad diaria sintética a una puntuación entre 0 y 100.
- Referencia histórica contra la que se compara cada fecha.
- Umbrales de afluencia baja, media y alta.

### Influencia meteorológica

- Variables concretas que se obtendrán del proveedor.
- Variables que modifican la afluencia.
- Variables que modifican únicamente la conveniencia.
- Tratamiento de lluvia, viento, temperatura, radiación u otras condiciones.

### Conveniencia de visita

- Fórmula o reglas de conveniencia.
- Influencia de la afluencia.
- Influencia del clima.
- Umbrales de recomendado, precaución y no recomendado.
- Condición mínima para considerar un día realmente recomendable.

### Mejor opción

- Método de selección.
- Tratamiento de semanas completamente desfavorables.
- Desempate por afluencia.
- Desempate por proximidad.
- Plantillas textuales de recomendación.

### Pruebas matemáticas mínimas

- Día laborable con clima favorable.
- Fin de semana con clima favorable.
- Feriado con lluvia intensa.
- Día de baja afluencia con tormenta.
- Semana sin días recomendables.
- Dos días con la misma conveniencia.

Estas decisiones deben quedar en `03-especificacion-motor-estimacion.md`.

---

## 3.2. Arquitectura y tecnologías

Deben aprobarse:

- Número de microservicios.
- Responsabilidad de cada servicio.
- Ubicación del motor de estimación.
- Servicio que consulta la API meteorológica.
- Propiedad de los datos.
- Comunicación entre servicios.
- Estrategia de persistencia.
- Lenguaje y framework del backend.
- Tecnología del frontend.
- Base de datos.
- Contenedores.
- Servicios de AWS.

Una propuesta inicial puede incluir dos microservicios:

1. Servicio de predicción turística.
2. Servicio meteorológico.

Sin embargo, la decisión deberá justificarse en `04-arquitectura-y-modelo-de-datos.md`. La arquitectura debe cumplir el requisito académico de microservicios sin crear servicios artificiales sin responsabilidades claras.

---

## 3.3. Preparación de los datos oficiales

Antes de desarrollar el procesamiento definitivo se necesita:

- Incorporar el CSV oficial al entorno de trabajo.
- Confirmar nombres y tipos de columnas.
- Filtrar el destino correcto.
- Normalizar meses y años.
- Extraer el periodo desde enero de 2022 hasta agosto de 2026.
- Revisar duplicados y valores ausentes.
- Decidir si nacionales y extranjeros se conservarán para trazabilidad aunque no aparezcan en el dashboard.
- Crear datos de prueba pequeños y controlados.

El agente podrá programar la transformación, pero no debe inventar la estructura del archivo ni simular datos oficiales que no fueron proporcionados.

---

## 3.4. Modelo de datos y contratos API

Después de cerrar el motor y la arquitectura se definirán:

- Entidades y tablas.
- Restricciones de unicidad.
- Estados de disponibilidad.
- Datos oficiales, sintéticos y meteorológicos.
- Versiones del generador y del motor.
- Persistencia de predicciones.
- Endpoint semanal para el dashboard.
- Formatos de solicitud y respuesta.
- Enumeraciones.
- Errores.
- Zona horaria.
- Fechas de actualización.

El frontend y el backend no deben desarrollarse en paralelo sin un contrato estable.

---

## 3.5. Wireframe y estados de interfaz

Se necesita acordar un diseño funcional mínimo para:

- Escritorio.
- Móvil.
- Carga inicial.
- Error meteorológico.
- Datos incompletos.
- Semana sin días recomendables.

El agente podrá decidir detalles de estilo, pero deberá respetar:

- El detalle del día seleccionado.
- Las siete tarjetas.
- La codificación por recomendación.
- La etiqueta de mejor opción.
- Los enlaces oficiales.
- La advertencia metodológica.

---

## 3.6. Despliegue en AWS

Antes de crear infraestructura definitiva deben decidirse:

- Alojamiento del frontend.
- Ejecución de microservicios.
- Registro de imágenes.
- Base de datos.
- Red y exposición pública.
- Secretos.
- Logs.
- Límites de costo.
- Integración y despliegue continuo.
- Procedimiento para eliminar recursos.

No debe generarse infraestructura compleja por defecto. La solución debe priorizar sencillez, costo controlado y capacidad de demostración.

---

## 3.7. Plan incremental para agentes

No se solicitará a un agente que construya todo en una única tarea. La implementación se dividirá en incrementos:

1. Preparación del repositorio.
2. Importación de datos oficiales.
3. Generación diaria sintética.
4. Motor de estimación.
5. Integración meteorológica.
6. API semanal.
7. Dashboard web.
8. Integración completa y pruebas.
9. Despliegue en AWS.
10. Preparación de la demostración.

Cada incremento tendrá un SDD y deberá superarse antes de iniciar el siguiente bloque dependiente.

---

## 3.8. Instrucciones del agente

Antes de otorgar autonomía al agente se creará `AGENTS.md` con:

- Orden de lectura de documentos.
- Jerarquía de fuentes de verdad.
- Convenciones.
- Comandos de instalación, validación y pruebas.
- Límites arquitectónicos.
- Restricciones del MVP.
- Regla de no agregar funcionalidades no aprobadas.
- Obligación de mantener documentación y pruebas.
- Procedimiento ante contradicciones.
- Definición de terminado.

Las skills se crearán únicamente cuando exista un procedimiento repetitivo que deba encapsularse.

---

# 4. Decisiones que requieren aprobación humana

La IA puede derivar rápidamente gran parte de los documentos y del código. Sin embargo, estas decisiones requieren aprobación explícita:

1. Fórmula y supuestos del motor de estimación.
2. Número y responsabilidad de los microservicios.
3. Tecnologías principales.
4. Estrategia de persistencia.
5. Servicios de AWS y costo aceptable.
6. Diseño visual general del dashboard.
7. Uso final de los datos oficiales proporcionados.

El agente no debe tomar silenciosamente estas decisiones durante la generación de código.

---

# 5. Documentos mínimos antes de comenzar el código

Antes de iniciar una implementación completa deben existir:

```text
01-definicion-y-alcance-del-proyecto.md
02-requisitos-del-sistema.md
03-especificacion-motor-estimacion.md
04-arquitectura-y-modelo-de-datos.md
05-contratos-api-y-diseno-interfaz.md
06-plan-implementacion-pruebas-y-despliegue.md
AGENTS.md
```

Los SDD se crearán progresivamente para cada incremento.

No todos los documentos deben ser extensos. Deben ser suficientes para impedir que el agente improvise decisiones importantes.

---

# 6. Qué puede producir rápidamente la IA

Cuando se hayan cerrado el motor y las decisiones tecnológicas, la IA podrá generar con rapidez:

- Diagramas Mermaid.
- Modelo de datos.
- Contratos API.
- Wireframes textuales.
- Plan de implementación.
- Estrategia de pruebas.
- Diseño de despliegue.
- `AGENTS.md`.
- SDD incrementales.
- Estructura del monorepo.
- Scripts de datos.
- Microservicios.
- Frontend.
- Pruebas.
- Contenedores.
- Workflows.
- Infraestructura.
- README.
- Guion de demostración.

La rapidez no elimina la necesidad de implementar por incrementos y validar cada entrega.

---

# 7. Mínimo real para iniciar el desarrollo responsable

Para comenzar de forma segura se necesita:

1. Cerrar la especificación del motor.
2. Aprobar la arquitectura y el stack.
3. Disponer del archivo oficial y su estructura real.
4. Definir el modelo de datos y el contrato semanal.
5. Aprobar el wireframe funcional.
6. Elegir el despliegue de AWS.
7. Crear el plan incremental y `AGENTS.md`.

Después de estas decisiones, el proyecto podrá pasar de documentación a código sin que el agente tenga que reinterpretar el producto.

---

# 8. Orden recomendado de trabajo

## Bloque 1. Fundamentos terminados

```text
01-definicion-y-alcance-del-proyecto.md
02-requisitos-del-sistema.md
```

## Bloque 2. Diseño previo al código

```text
03-especificacion-motor-estimacion.md
04-arquitectura-y-modelo-de-datos.md
05-contratos-api-y-diseno-interfaz.md
06-plan-implementacion-pruebas-y-despliegue.md
AGENTS.md
```

## Bloque 3. Implementación incremental

```text
SDD-001 Preparación del repositorio
SDD-002 Importación de datos
SDD-003 Generación sintética
SDD-004 Motor de estimación
SDD-005 Integración meteorológica
SDD-006 API semanal
SDD-007 Dashboard
SDD-008 Integración y pruebas
SDD-009 Despliegue
```

## Bloque 4. Entrega

```text
Aplicación desplegada
Repositorio GitHub
Documentación final
Video de construcción
Demostración para el usuario
```

---

# 9. Conclusión

El producto y sus requisitos ya están suficientemente delimitados. Las principales decisiones pendientes son la matemática del motor, la arquitectura, las tecnologías, la preparación de los datos, los contratos, el wireframe y el despliegue.

Una vez cerrados esos puntos, la IA podrá construir el MVP de manera rápida. La implementación deberá realizarse mediante incrementos pequeños, cada uno respaldado por un SDD, pruebas y criterios de aceptación. Esta estrategia permite aprovechar la velocidad de los agentes sin entregarles decisiones funcionales o técnicas que todavía no han sido aprobadas.
