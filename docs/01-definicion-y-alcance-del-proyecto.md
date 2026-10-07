# Especificación inicial del MVP

## Aplicación para la estimación de afluencia turística en la Cueva de las Lechuzas

**Estado del documento:** Borrador consolidado de alcance  
**Versión:** 0.1  
**Tipo de proyecto:** Aplicación web académica desplegada en la nube  
**Destino inicial:** Parque Nacional de Tingo María, sector Cueva de las Lechuzas  
**Documento de requisitos relacionado:** `02-requisitos-del-sistema.md`

---

## 1. Contexto del proyecto

El proyecto forma parte de una actividad académica de construcción de software para aplicaciones web. La solución deberá demostrar el uso de:

- Arquitectura de microservicios.
- Mediciones presentadas mediante un dashboard.
- Una API externa de información meteorológica.
- Persistencia en una base de datos.
- Despliegue en Amazon Web Services.
- Repositorio público o entregable en GitHub.
- Video del proceso de construcción.
- Video de demostración del funcionamiento para el usuario.

Aunque el trabajo tiene un alcance académico y un tiempo de desarrollo reducido, la aplicación deberá diseñarse con buenas prácticas para facilitar su mantenimiento, evolución y ampliación mediante agentes de inteligencia artificial apoyados en especificaciones, SDD y skills claramente definidos.

---

## 2. Nombre provisional

**TurismoPredict**

El nombre es provisional y podrá cambiar posteriormente sin afectar la definición funcional.

---

## 3. Problema

Los visitantes de la Cueva de las Lechuzas no cuentan con una herramienta que combine el comportamiento histórico de las visitas, el calendario y las condiciones meteorológicas para estimar el nivel de afluencia esperado durante los próximos días.

Actualmente, una persona puede consultar información general del lugar, condiciones meteorológicas o indicaciones de acceso en fuentes separadas. Sin embargo, esa información no se transforma automáticamente en una recomendación sencilla que responda:

> ¿Qué día de los próximos siete días sería más conveniente visitar la Cueva de las Lechuzas?

La aplicación buscará responder esa pregunta mediante una puntuación de afluencia y una puntuación independiente de conveniencia de visita.

---

## 4. Objetivo general

Desarrollar una aplicación web basada en una arquitectura de microservicios que estime la afluencia turística diaria de la Cueva de las Lechuzas durante los próximos siete días y recomiende el día más conveniente para realizar la visita, utilizando registros históricos mensuales oficiales, una distribución diaria sintética, información de calendario y datos meteorológicos reales.

---

## 5. Objetivos específicos

1. Procesar datos históricos mensuales de visitantes correspondientes al Parque Nacional de Tingo María, sector Cueva de las Lechuzas.
2. Construir una distribución diaria sintética que conserve los totales mensuales oficiales.
3. Estimar una puntuación diaria de afluencia turística entre 0 y 100.
4. Clasificar la afluencia estimada en categorías comprensibles para el usuario.
5. Consumir una API meteorológica para obtener el pronóstico de los próximos siete días.
6. Calcular una puntuación de conveniencia de visita independiente de la puntuación de afluencia.
7. Comparar los próximos siete días y recomendar el día más conveniente para visitar.
8. Mostrar las mediciones mediante un dashboard web.
9. Proporcionar enlaces hacia los canales oficiales de SERNANP para consultar horarios, entradas, cierres y restricciones actualizadas.
10. Implementar una solución desacoplada que permita incorporar posteriormente otros destinos, nuevas fuentes de datos o un modelo predictivo calibrado con datos diarios reales.

---

## 6. Alcance geográfico

El MVP trabajará exclusivamente con:

> Parque Nacional de Tingo María, sector Cueva de las Lechuzas, Huánuco, Perú.

La página oficial de SERNANP identifica a la Cueva de las Lechuzas como uno de los principales atractivos del Parque Nacional de Tingo María. El parque se encuentra en el distrito de Mariano Dámaso Beraún, provincia de Leoncio Prado, departamento de Huánuco.

El parque posee tres rutas turísticas principales:

- Cueva de las Lechuzas.
- Quinceañera.
- Tres de Mayo.

Aunque inicialmente se trabajará con un único destino, los componentes técnicos no deberán incluir lógica rígidamente dependiente del nombre de la Cueva de las Lechuzas. El destino deberá representarse como una entidad turística para permitir la incorporación de otros lugares en futuras versiones.

---

## 7. Usuario objetivo

El usuario principal será una persona interesada en visitar la Cueva de las Lechuzas.

El usuario no necesitará registrarse ni iniciar sesión. La aplicación deberá permitir consultar directamente:

- Afluencia estimada.
- Pronóstico meteorológico.
- Conveniencia de visita.
- Comparación de los próximos siete días.
- Mejor día recomendado.
- Enlaces oficiales relacionados con la visita.

> **Nota de alineación con `02-requisitos-del-sistema.md`:** La visualización de información histórica resumida fue descartada de la experiencia pública del MVP. Los datos históricos permanecen como insumo interno del motor. Ver sección 16.3 de este documento y el requisito RUI-04 del documento de requisitos.

---

## 8. Propuesta de valor

La aplicación ofrecerá dos resultados principales.

### 8.1. Estimación de afluencia

Responderá:

> ¿Qué nivel de afluencia turística se espera para cada uno de los próximos siete días?

**Ejemplo ilustrativo** *(los valores exactos son referencias de diseño; los umbrales definitivos se definen en `03-especificacion-motor-estimacion.md`)*:

```
Puntuación estimada de afluencia: 76/100
Nivel de afluencia: Alto
```

### 8.2. Recomendación del mejor día

Responderá:

> ¿Qué día ofrece la mejor combinación entre menor afluencia y condiciones meteorológicas favorables?

**Ejemplo ilustrativo** *(los valores exactos son referencias de diseño; los umbrales definitivos se definen en `03-especificacion-motor-estimacion.md`)*:

```
Mejor día recomendado: miércoles
Afluencia estimada: 31/100
Conveniencia de visita: 88/100
Clima: favorable
```

---

## 9. Horizonte y granularidad

### 9.1. Horizonte temporal

La aplicación evaluará los próximos siete días.

La elección es coherente con el horizonte predeterminado de siete días que ofrece Open-Meteo. El proveedor permite solicitar hasta dieciséis días, por lo que una ampliación futura no requeriría necesariamente cambiar de API meteorológica.

### 9.2. Granularidad

La predicción será diaria, no horaria.

No se estimará la afluencia por franjas horarias porque los registros oficiales disponibles se encuentran agregados mensualmente. Desagregar los valores hasta horas introduciría demasiadas suposiciones.

En el MVP, la expresión "mejor momento para visitar" significará:

> Mejor día dentro de los próximos siete días.

---

## 10. Fuentes de información

### 10.1. Datos históricos oficiales

Se utilizarán los registros mensuales publicados por MINCETUR correspondientes al Parque Nacional de Tingo María y la Cueva de las Lechuzas.

El conjunto oficial de visitantes a sitios turísticos del Perú contiene información desagregada por:

- Periodo de referencia.
- Departamento.
- Sitio turístico.
- Tipo de visitante.
- Visitantes nacionales.
- Visitantes extranjeros.

Los datos se encuentran disponibles para su descarga y reutilización mediante la Plataforma Nacional de Datos Abiertos. MINCETUR indica que estos conjuntos pueden ser utilizados por estudiantes, investigadores, empresas y entidades públicas.

**Periodo disponible:** Desde 2019 hasta agosto de 2026.

**Periodo utilizado por el motor:** Enero de 2022 a agosto de 2026.

| Periodo | Tratamiento |
|---|---|
| 2019–2021 | Almacenados como información histórica. No forman parte del patrón regular de estimación. |
| Enero 2022 – agosto 2026 | Base para construir patrones mensuales y la distribución diaria sintética. |

Se excluyen los años anteriores a 2022 para evitar que los efectos extraordinarios de cierres, restricciones y recuperación pospandémica alteren el patrón turístico reciente.

### 10.2. Datos meteorológicos

El MVP consumirá una única API externa de meteorología.

**Proveedor provisional:** Open-Meteo.

El servicio proporciona variables meteorológicas diarias, entre ellas:

- Temperatura máxima y mínima.
- Temperatura aparente.
- Código meteorológico.
- Precipitación acumulada.
- Probabilidad máxima de precipitación.
- Horas de precipitación.
- Velocidad máxima del viento.
- Índice UV.
- Duración de la luz solar.

La selección definitiva de variables se realizará durante la especificación del motor de estimación en `03-especificacion-motor-estimacion.md`.

### 10.3. Información de calendario

No se integrará una API externa de calendario.

El sistema calculará localmente:

- Día de la semana.
- Mes.
- Año.
- Número de días del mes.
- Condición de sábado o domingo.

Se mantendrá un calendario turístico local y versionado con:

- Feriados nacionales relevantes.
- Fines de semana largos.
- Periodos turísticos especiales.
- Eventos locales conocidos.
- Días no laborables extraordinarios.
- Excepciones que puedan afectar la demanda.
- Cierres conocidos, si se dispone de información oficial.

El calendario no almacenará todos los días del año. Solo guardará excepciones que no puedan deducirse directamente de la fecha.

---

## 11. Estrategia de datos sintéticos

Los datos oficiales disponibles son mensuales. La aplicación necesita producir estimaciones diarias. Por esta razón, se implementará una distribución diaria sintética condicionada.

### 11.1. Principio de conservación mensual

El total mensual oficial no será modificado. Se deberá cumplir:

```
Suma de visitantes diarios sintéticos del mes = Total mensual oficial
```

La síntesis solo distribuirá el total entre los días del mes.

### 11.2. Unidad sintética

Cada registro generado representará:

- Una fecha.
- Una cantidad diaria estimada.
- Los factores utilizados.
- La versión del generador.

### 11.3. Factores iniciales

La distribución tendrá en cuenta:

- Día de la semana.
- Fin de semana.
- Feriado.
- Fin de semana largo.
- Periodo turístico.
- Mes.
- Estacionalidad.
- Variación limitada y reproducible.

**Fórmula conceptual de referencia** *(los factores y valores exactos se definen en `03-especificacion-motor-estimacion.md`)*:

```
peso_diario =
    factor_día_semana
    × factor_tipo_fecha
    × factor_temporada
    × factor_periodo_especial

visitantes_día =
    total_mensual_oficial × peso_del_día / suma_de_pesos_del_mes
```

### 11.4. Transparencia

La aplicación y la documentación deberán aclarar:

> Los valores diarios son estimaciones académicas derivadas de registros mensuales oficiales mediante reglas documentadas. No representan conteos diarios oficiales.

---

## 12. Tratamiento de meses futuros y datos incompletos

No se deberán rellenar con cero los meses que todavía no hayan sido publicados.

El sistema deberá diferenciar entre:

| Estado | Descripción |
|---|---|
| `AVAILABLE` | Registro histórico disponible. |
| `NOT_YET_AVAILABLE` | Registro todavía no publicado. |
| `INCOMPLETE` | Periodo parcialmente disponible. |
| `ZERO_REPORTED` | Valor oficial igual a cero. |

Para predecir una fecha perteneciente a un mes sin datos oficiales del mismo año, se utilizarán los valores del mismo mes en años anteriores.

**Ejemplo ilustrativo:**

```
Predicción para octubre de 2026
→ utilizar octubre de 2022
→ utilizar octubre de 2023
→ utilizar octubre de 2024
→ utilizar octubre de 2025
```

> **Nota:** La forma exacta de combinar los meses anteriores se determinará en `03-especificacion-motor-estimacion.md`. Se podrá utilizar promedio, mediana, promedio ponderado o tendencia temporal.

> **Comportamiento degradado — pendiente de definición:** No está definido en el alcance de este entregable qué debe mostrar el sistema cuando un supuesto crítico falla (por ejemplo, pronóstico meteorológico no disponible o ausencia total de datos históricos de referencia para el mes evaluado). Este comportamiento deberá detallarse en un documento posterior de arquitectura o en `03-especificacion-motor-estimacion.md`.

---

## 13. Puntuación de afluencia

La aplicación producirá una puntuación entre 0 y 100.

**Ejemplo ilustrativo** *(los umbrales definitivos se definen en `03-especificacion-motor-estimacion.md`)*:

```
Afluencia estimada: 74/100
```

### 13.1. Significado

La puntuación representará el nivel relativo de afluencia esperada de una fecha comparado con patrones históricos equivalentes.

La puntuación **no** representará:

- Porcentaje real de ocupación.
- Porcentaje de capacidad utilizada.
- Número observado de personas.
- Probabilidad matemática exacta.
- Medición en tiempo real.

### 13.2. Clasificación de referencia

Los siguientes rangos son **valores de ejemplo para ilustrar la intención del sistema**. Los umbrales definitivos y su justificación se establecen en `03-especificacion-motor-estimacion.md`.

| Rango de referencia | Nivel |
|---|---|
| 0–33 | Afluencia baja |
| 34–66 | Afluencia media |
| 67–100 | Afluencia alta |

### 13.3. Conteo estimado

La puntuación será el resultado principal.

Opcionalmente, podrá mostrarse un rango secundario. El siguiente es un **ejemplo ilustrativo**:

```
Visitantes diarios estimados: 350–450
```

No se mostrará una cantidad exacta como si se tratara de una medición oficial.

---

## 14. Puntuación de conveniencia de visita

La conveniencia se calculará independientemente de la afluencia.

### 14.1. Justificación

Una afluencia baja no significa necesariamente que sea un buen día para visitar.

**Ejemplo A:**
```
Afluencia baja + Lluvia intensa = Poca concurrencia, pero visita no recomendada
```

**Ejemplo B:**
```
Afluencia alta + Clima favorable = Buenas condiciones, pero gran concurrencia
```

### 14.2. Resultado

La conveniencia se expresará mediante una puntuación y una categoría textual. El siguiente es un **ejemplo ilustrativo**; las categorías definitivas se definen en `03-especificacion-motor-estimacion.md`.

```
Puntuación de conveniencia: 82/100
Resultado: Recomendado
```

El documento de requisitos (`02-requisitos-del-sistema.md`, RF-07) establece las siguientes categorías para el MVP:

- Recomendado.
- Visitable con precaución.
- No recomendado.

### 14.3. Factores

La conveniencia podrá considerar:

- Probabilidad de precipitación.
- Precipitación acumulada.
- Código meteorológico.
- Temperatura.
- Temperatura aparente.
- Velocidad del viento.
- Índice UV.
- Puntuación de afluencia.
- Restricciones conocidas.

> **Nota:** La fórmula exacta de conveniencia, los pesos de cada factor y los umbrales de clasificación se definen en `03-especificacion-motor-estimacion.md`.

---

## 15. Selección del mejor día

El sistema evaluará los próximos siete días y seleccionará la mejor opción comparativa.

**Ejemplo ilustrativo** *(los criterios de selección definitivos se definen en `03-especificacion-motor-estimacion.md`)*:

| Día | Afluencia | Conveniencia |
|---|---|---|
| Lunes | 42/100 | 76/100 |
| Martes | 35/100 | 81/100 |
| **Miércoles** | **29/100** | **89/100** |
| Jueves | 47/100 | 69/100 |
| Viernes | 61/100 | 73/100 |
| Sábado | 82/100 | 58/100 |
| Domingo | 88/100 | 51/100 |

```
Mejor día recomendado: miércoles
Motivo: Se espera una afluencia baja y condiciones meteorológicas favorables.
```

La selección no deberá basarse exclusivamente en el día con menor afluencia. Deberá considerar simultáneamente la conveniencia meteorológica.

---

## 16. Dashboard del visitante

La interfaz principal mostrará mediciones comprensibles sin exigir registro.

### 16.1. Indicadores principales

- Puntuación estimada de afluencia.
- Nivel de afluencia.
- Puntuación de conveniencia.
- Categoría de recomendación.
- Probabilidad de lluvia.
- Precipitación esperada.
- Temperatura máxima y mínima.
- Mejor día recomendado.
- Fecha de actualización del pronóstico.

### 16.2. Comparación de siete días

El usuario podrá comparar los próximos siete días mediante tarjetas. Cada día deberá mostrar, como mínimo:

- Fecha y día de la semana.
- Afluencia de 0 a 100 con su nivel.
- Conveniencia de 0 a 100.
- Resumen meteorológico.
- Indicación de feriado o fecha especial.

### 16.3. Sección histórica — excluida del MVP

> **Decisión de alcance:** Una versión anterior de este documento contemplaba mostrar al visitante una sección con evolución mensual de visitantes, comparación anual, meses de mayor afluencia y distribución entre nacionales y extranjeros. Esta funcionalidad fue **descartada para el MVP** en el documento `02-requisitos-del-sistema.md` (ver RUI-04 y sección 12 de ese documento).
>
> Los datos históricos permanecen como insumo interno del motor de estimación y no se exponen en la experiencia pública.

### 16.4. Explicación mínima

La interfaz mostrará una justificación breve generada mediante **plantillas de texto basadas en reglas**, no mediante texto libre generado por IA. El siguiente es un ejemplo del contenido que una plantilla podría producir:

```
¿Por qué se obtuvo esta puntuación?
• Es fin de semana.
• El mes presenta una afluencia histórica elevada.
• Se esperan condiciones meteorológicas favorables.
```

La aplicación no necesita mostrar fórmulas, pesos ni detalles técnicos completos al visitante.

---

## 17. Información oficial de visita

La página oficial de SERNANP dedicada al Parque Nacional de Tingo María contiene secciones sobre:

- Información general.
- Tipo y horarios de ingreso.
- Cómo llegar.
- Rutas turísticas.
- Consejos y recomendaciones.
- Operadores turísticos.
- Materiales para el visitante.

También indica: temporada recomendada durante todo el año, clima cálido y húmedo, temperatura habitual entre 22 y 26 °C, y temporada de lluvias de octubre a abril.

SERNANP dispone igualmente de un portal de compra de entradas para áreas naturales protegidas.

### 17.1. Limitación

El sistema no afirmará automáticamente:

- Que el sitio se encuentra abierto.
- Que quedan entradas disponibles.
- Que no existen cierres.
- Que el horario publicado no ha cambiado.
- Que las condiciones operativas permiten el ingreso.

### 17.2. Solución

Se mostrarán enlaces como:

- Consultar información oficial.
- Comprar entrada.
- Revisar recomendaciones de SERNANP.

Y la advertencia:

> Antes de realizar la visita, consulte los horarios, disponibilidad de entradas, restricciones y avisos vigentes en los canales oficiales de SERNANP.

No se utilizará Google Maps como fuente autoritativa de horarios o cierres.

---

## 18. Funcionalidades incluidas

El MVP permitirá:

- Abrir la aplicación sin autenticación.
- Consultar los próximos siete días.
- Ver el pronóstico meteorológico diario.
- Ver una puntuación diaria de afluencia.
- Ver el nivel de afluencia.
- Ver una puntuación de conveniencia.
- Comparar todos los días evaluados.
- Recibir una recomendación del mejor día.
- Consultar una explicación breve de la puntuación.
- Acceder a enlaces oficiales relacionados con la visita.

---

## 19. Funcionalidades excluidas

El MVP no incluirá:

- Inicio de sesión.
- Registro de usuarios.
- Recuperación de contraseñas.
- Roles.
- Perfiles.
- Favoritos.
- Intención de visita.
- Comentarios.
- Calificaciones.
- Panel administrativo.
- Reservaciones.
- Venta propia de entradas.
- Pagos.
- Notificaciones.
- Chat.
- Aplicación móvil nativa.
- Geolocalización en tiempo real.
- Predicción por horas.
- Conteo de personas en tiempo real.
- Integración con cámaras o sensores.
- API de tránsito.
- API externa de calendario.
- Scraping de Google Maps.
- Sección histórica visible para el usuario.
- Múltiples destinos turísticos.
- Machine learning complejo.
- Recomendaciones personalizadas.

---

## 20. Integraciones externas

| Estado | Integración |
|---|---|
| ✅ Incluida | API meteorológica |
| ❌ Excluida del MVP | API de tráfico |
| ❌ Excluida del MVP | API de calendario |
| ❌ Excluida del MVP | API de redes sociales |
| ❌ Excluida del MVP | API de popularidad de Google Maps |
| ❌ Excluida del MVP | API de venta de entradas |
| ❌ Excluida del MVP | API de autenticación externa |

La información de tránsito podrá considerarse para un MVP posterior como señal complementaria de movilidad, pero no formará parte de la primera versión.

---

## 21. Persistencia de datos

La aplicación utilizará una base de datos. Como mínimo, deberá persistir:

- Sitio turístico.
- Registros mensuales oficiales.
- Fuente de cada registro.
- Estado de disponibilidad del periodo.
- Registros diarios sintéticos o parámetros para generarlos.
- Versiones del generador sintético.
- Predicciones generadas.
- Variables consideradas en cada predicción.
- Puntuación de afluencia.
- Puntuación de conveniencia.
- Instantáneas meteorológicas.
- Fecha y hora de actualización.
- Versión del motor de estimación.

El diseño exacto de tablas y relaciones se realizará durante la etapa de arquitectura y modelado de datos.

---

## 22. Transparencia y limitaciones

La aplicación deberá comunicar claramente:

> La puntuación de afluencia es una estimación académica calculada mediante datos mensuales oficiales, distribución diaria sintética, variables de calendario y pronóstico meteorológico.

También deberá señalar:

> La puntuación no representa ocupación real, disponibilidad de entradas ni un conteo en tiempo real.

Y:

> Las condiciones meteorológicas y operativas pueden cambiar. Antes de realizar la visita, consulte los canales oficiales.

---

## 23. Evolución futura

La solución deberá permitir incorporar, sin reemplazar completamente el sistema:

- Otros destinos turísticos.
- Datos diarios oficiales.
- Sensores o contadores de visitantes.
- API de tráfico.
- Señales de movilidad.
- Información histórica meteorológica.
- Datos de eventos regionales.
- Modelo estadístico.
- Modelo de machine learning.
- Mayor horizonte de pronóstico.
- Predicción por horarios.
- Panel administrativo.
- Gestión dinámica de reglas.
- Sistema de usuarios.
- Validación de predicciones frente a registros reales.

Cuando existan datos diarios reales, el distribuidor sintético deberá poder sustituirse por un proveedor real sin modificar la interfaz principal ni los contratos externos del sistema.

---

## 24. Decisiones cerradas

| Decisión | Valor |
|---|---|
| Destino | Cueva de las Lechuzas |
| Horizonte | Próximos 7 días |
| Granularidad | Diaria |
| Datos históricos utilizados | Enero 2022 a agosto 2026 |
| Fuente histórica | Registros oficiales mensuales (MINCETUR) |
| Datos diarios | Sintéticos y condicionados |
| Conservación | La suma diaria debe coincidir con el total mensual oficial |
| Resultado principal | Puntuación de afluencia entre 0 y 100 |
| Resultado adicional | Puntuación de conveniencia |
| Recomendación | Mejor día para visitar |
| API externa | Solo meteorología |
| Calendario | Local y versionado |
| Usuarios | Sin autenticación |
| Dashboard | Público |
| Tráfico | Fuera del MVP |
| Horarios y cierres | Consulta mediante enlaces oficiales |
| Despliegue | Amazon Web Services |
| Repositorio | GitHub |

---

## 25. Decisiones pendientes para la siguiente etapa

### Motor de estimación

Definidas en `03-especificacion-motor-estimacion.md` (documento pendiente de elaboración):

- Método de referencia mensual (promedio, mediana o tendencia).
- Factores por día de la semana.
- Factores de feriados.
- Factores de temporadas.
- Variación sintética y semilla de reproducibilidad.
- Normalización de 0 a 100.
- Umbrales de afluencia.
- Variables meteorológicas exactas.
- Penalizaciones meteorológicas.
- Fórmula de conveniencia.
- Umbrales de recomendación.
- Condición mínima para considerar un día recomendado.
- Selección del mejor día.
- Comportamiento del sistema ante ausencia de pronóstico o datos históricos.
- Pruebas y escenarios esperados.

### Arquitectura

- Número y responsabilidad de cada microservicio.
- Contratos API entre servicios.
- Comunicación entre servicios.
- Separación de datos.
- Base de datos.
- Caché meteorológica.
- Tecnologías de frontend y backend.
- Contenedores.
- Observabilidad.
- Seguridad.
- Despliegue en AWS.
- CI/CD.

### Diseño de interfaz

- Wireframes.
- Organización del dashboard.
- Gráficos.
- Identidad visual.
- Navegación.
- Experiencia móvil y de escritorio.

### Desarrollo asistido por IA

- SDD general.
- SDD por servicio.
- Reglas del repositorio.
- Instrucciones para agentes.
- Skills especializadas.
- Criterios de aceptación.
- Estrategia de tareas y revisión.

---

## 26. Definición consolidada del MVP

El MVP será una aplicación web enfocada en la Cueva de las Lechuzas que estimará la afluencia turística diaria para los próximos siete días. Utilizará registros mensuales oficiales comprendidos entre 2022 y agosto de 2026, distribuidos sintéticamente en días mediante reglas documentadas que conservarán los totales mensuales. La estimación incorporará factores de calendario administrados localmente y un pronóstico meteorológico obtenido mediante una API externa.

Para cada fecha, la aplicación producirá una puntuación de afluencia entre 0 y 100, un nivel de afluencia y una puntuación independiente de conveniencia. Finalmente, comparará los siete días y recomendará el más apropiado para realizar la visita.

El dashboard será público, no tendrá gestión de usuarios ni sección histórica visible, y ofrecerá enlaces hacia los canales oficiales de SERNANP para comprobar horarios, entradas y restricciones.

## Alineación de implementación (2026-10-06)

La plataforma aprobada por el usuario es AWS: EC2 para STP, SMS y PostgreSQL 16; AWS Amplify Hosting para el frontend. Esta decisión descarta los anexos anteriores de otros proveedores y mantiene el requisito académico de AWS.
Los documentos 03–06 ya existen; las referencias anteriores a su elaboración pendiente
son históricas. Las precisiones de cálculo y fallos están en docs/03 §16 y docs/05 §9.
