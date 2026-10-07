# Requisitos del sistema

## Aplicación web para la estimación de afluencia turística en la Cueva de las Lechuzas

**Versión:** 0.1  
**Estado:** Borrador consolidado  
**Documento relacionado:** `01-definicion-y-alcance-del-proyecto.md`  
**Destino del MVP:** Parque Nacional de Tingo María, sector Cueva de las Lechuzas  
**Idioma del MVP:** Español

---

## 1. Propósito

Este documento especifica los requisitos verificables del MVP de una aplicación web orientada a estimar la afluencia turística diaria y recomendar el día más conveniente para visitar la Cueva de las Lechuzas.

Los requisitos se derivan de las decisiones establecidas en el documento `01-definicion-y-alcance-del-proyecto.md`. Este documento define qué deberá hacer el sistema y qué condiciones deberá cumplir, sin fijar todavía las fórmulas exactas del motor de estimación, la arquitectura de microservicios, las tecnologías de implementación ni la infraestructura específica de despliegue.

---

## 2. Alcance de esta especificación

Esta especificación cubre:

- La experiencia pública del visitante.
- La consulta de los próximos siete días.
- La presentación de la afluencia estimada.
- La presentación de la conveniencia de visita.
- La recomendación del mejor día.
- La integración con información meteorológica.
- El uso interno de datos históricos mensuales oficiales.
- La generación reproducible de datos diarios sintéticos.
- La administración local de factores de calendario.
- Los enlaces hacia fuentes oficiales de visita.
- Las condiciones mínimas de calidad del sistema.

Esta especificación no define:

- Las fórmulas y pesos exactos del motor de estimación.
- Los umbrales numéricos definitivos de clasificación.
- El número y los límites de los microservicios.
- La tecnología de frontend, backend o base de datos.
- El mecanismo técnico de caché.
- Los contratos detallados de las API internas.
- La infraestructura detallada de AWS.
- El diseño visual definitivo.

Estos puntos deberán definirse en documentos posteriores.

---

## 3. Actores y sistemas externos

### 3.1. Visitante

Persona que accede a la aplicación para comparar los próximos siete días y determinar cuál resulta más conveniente para visitar la Cueva de las Lechuzas.

El visitante no necesita registrarse ni iniciar sesión.

### 3.2. Proveedor meteorológico

Servicio externo encargado de proporcionar el pronóstico meteorológico necesario para evaluar los próximos siete días.

### 3.3. Fuente oficial de datos históricos

Fuente pública utilizada para obtener los registros mensuales de visitantes. Los datos se incorporarán al sistema mediante un proceso de importación controlado y reproducible.

### 3.4. Canales oficiales de visita

Sitios externos oficiales a los que el visitante podrá acceder para verificar horarios, entradas, restricciones, recomendaciones y otra información operativa vigente.

---

## 4. Supuestos y dependencias

### AS-01. Disponibilidad de datos históricos

El sistema dispondrá de registros mensuales oficiales correspondientes al destino turístico contemplado por el MVP.

### AS-02. Periodo de referencia

El patrón regular utilizado por el motor se construirá con datos comprendidos entre enero de 2022 y el último mes oficial disponible, inicialmente agosto de 2026.

Los registros anteriores podrán conservarse como información de respaldo, pero no formarán parte del patrón regular del MVP.

### AS-03. Ausencia de registros diarios oficiales

Debido a que los datos oficiales disponibles están agregados mensualmente, la distribución diaria utilizada por el MVP será sintética y reproducible.

### AS-04. Disponibilidad del pronóstico

La recomendación completa de visita dependerá de la disponibilidad de pronóstico meteorológico para la fecha evaluada.

### AS-05. Horizonte del MVP

La interfaz pública estará limitada a hoy y los seis días siguientes, aunque el motor de afluencia podrá diseñarse sin quedar técnicamente acoplado a ese horizonte.

### AS-06. Información operativa del destino

La aplicación no garantizará que el lugar esté abierto, que existan entradas disponibles ni que no haya restricciones extraordinarias. El visitante deberá verificar esa información en los canales oficiales enlazados.

---

## 5. Casos de uso

### CU-01. Consultar el panorama de los próximos siete días

El visitante accede a la aplicación y visualiza hoy y los seis días siguientes con sus respectivas mediciones de afluencia, conveniencia y clima.

### CU-02. Consultar el detalle de un día

El visitante selecciona una de las siete fechas y consulta el detalle de afluencia, conveniencia, condiciones meteorológicas, recomendación y factores principales.

### CU-03. Identificar el mejor día para visitar

El visitante identifica la fecha marcada como mejor opción entre los siete días evaluados.

### CU-04. Consultar información oficial de visita

El visitante accede a enlaces externos para revisar información oficial, comprar entradas o consultar cómo llegar.

---

## 6. Requisitos funcionales

### RF-01. Cargar el panorama de siete días

El sistema deberá presentar hoy y los seis días siguientes como horizonte de consulta del MVP.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Se muestran exactamente siete fechas consecutivas.
2. La primera fecha corresponde a la fecha local actual.
3. Las fechas aparecen ordenadas cronológicamente.
4. No se presentan fechas anteriores al día actual.
5. El usuario no puede seleccionar desde la interfaz una fecha fuera del horizonte mostrado.

---

### RF-02. Seleccionar inicialmente el día actual

El sistema deberá mostrar inicialmente el detalle correspondiente al día actual.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Al abrir el dashboard, la tarjeta de hoy aparece seleccionada.
2. El panel principal muestra la información correspondiente a hoy.
3. La fecha seleccionada se distingue visualmente de las demás.

---

### RF-03. Seleccionar un día del horizonte

El visitante deberá poder seleccionar cualquiera de las siete fechas presentadas.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Cada tarjeta diaria es seleccionable.
2. Al seleccionar una tarjeta, el detalle principal se actualiza con la información de esa fecha.
3. La actualización ocurre en la misma página.
4. Solo una fecha aparece seleccionada a la vez.
5. La selección no abre una nueva página ni requiere un calendario independiente.

---

### RF-04. Mostrar la puntuación de afluencia

El sistema deberá mostrar para cada fecha una puntuación estimada de afluencia comprendida entre 0 y 100.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Toda fecha evaluada contiene una puntuación de afluencia.
2. La puntuación es un valor entre 0 y 100, ambos inclusive.
3. La interfaz identifica la puntuación como una estimación.
4. La puntuación no se presenta como porcentaje real de ocupación.
5. La interfaz no muestra una cantidad exacta de visitantes como si fuera un conteo oficial diario.

---

### RF-05. Mostrar el nivel de afluencia

El sistema deberá asociar la puntuación de afluencia con uno de los siguientes niveles:

- Baja.
- Media.
- Alta.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Toda puntuación mostrada posee un nivel asociado.
2. El mismo valor produce siempre el mismo nivel bajo una misma versión del motor.
3. Los umbrales utilizados corresponden a la configuración vigente del motor.
4. El nivel de afluencia se diferencia de la recomendación de visita.

---

### RF-06. Mostrar la puntuación de conveniencia

El sistema deberá mostrar para cada fecha una puntuación de conveniencia comprendida entre 0 y 100.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Toda fecha con información suficiente contiene una puntuación de conveniencia.
2. La puntuación se calcula independientemente de la puntuación de afluencia.
3. Una afluencia baja no implica automáticamente una conveniencia alta.
4. La puntuación se presenta como apoyo para la decisión de visita, no como garantía de seguridad ni de apertura del lugar.

---

### RF-07. Clasificar la recomendación de visita

El sistema deberá asociar la conveniencia de cada fecha con una de las siguientes categorías:

- Recomendado.
- Visitable con precaución.
- No recomendado.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Cada día evaluado presenta una categoría textual.
2. La categoría corresponde a la puntuación de conveniencia según los umbrales vigentes.
3. La categoría se muestra mediante texto y no exclusivamente mediante color.
4. La aplicación diferencia claramente la recomendación del nivel de afluencia.

---

### RF-08. Aplicar codificación visual a las tarjetas diarias

El sistema deberá utilizar una codificación visual para facilitar la comparación de los siete días.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Los días recomendados utilizan una señal visual verde.
2. Los días visitables con precaución utilizan una señal visual amarilla o ámbar.
3. Los días no recomendados utilizan una señal visual roja.
4. La información también se comunica mediante texto o iconos.
5. La comprensión de la recomendación no depende únicamente del color.
6. La tarjeta seleccionada conserva una indicación visual independiente de la categoría de recomendación.

---

### RF-09. Mostrar el resumen meteorológico diario

El sistema deberá mostrar un resumen meteorológico para el día seleccionado y una síntesis en cada tarjeta diaria.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. El detalle del día muestra las variables meteorológicas seleccionadas para el MVP.
2. Cada tarjeta diaria muestra al menos un resumen legible de las condiciones esperadas.
3. La fecha del dato meteorológico coincide con la fecha de la predicción turística.
4. El detalle indica cuándo se actualizó el pronóstico, si esa información está disponible.
5. Las variables definitivas se establecen en la especificación del motor y de la integración meteorológica.

---

### RF-10. Mostrar una recomendación textual

El sistema deberá generar una recomendación breve para el día seleccionado.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. La recomendación es coherente con la afluencia, la conveniencia y el clima del día.
2. La recomendación evita prometer disponibilidad de entradas o apertura del lugar.
3. La recomendación utiliza lenguaje comprensible para una persona no técnica.
4. El mensaje distingue entre un día recomendado, uno visitable con precaución y uno no recomendado.
5. La recomendación se genera mediante **plantillas de texto basadas en reglas**, no mediante texto libre generado por IA en tiempo de ejecución.
6. La longitud es breve: máximo tres oraciones o equivalente en viñetas cortas.

---

### RF-11. Mostrar factores principales de la estimación

El sistema deberá mostrar una explicación breve de los factores principales que influyeron en el resultado del día seleccionado.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Se muestran al menos los factores más relevantes utilizados en la estimación.
2. Los factores pueden incluir tipo de día, comportamiento histórico mensual, fecha especial y condiciones meteorológicas.
3. No es obligatorio mostrar fórmulas, pesos ni operaciones matemáticas completas.
4. La explicación mostrada corresponde a factores realmente utilizados por el motor.
5. El texto evita presentar datos sintéticos como observaciones oficiales diarias.

---

### RF-12. Identificar la mejor opción de la semana

El sistema deberá identificar una fecha como la mejor opción comparativa entre los siete días evaluados.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Una tarjeta muestra la etiqueta `Mejor opción` o una expresión equivalente.
2. La fecha marcada coincide con el resultado del mecanismo de selección vigente.
3. La recomendación considera la conveniencia y no únicamente la menor afluencia.
4. La selección inicial de hoy no cambia automáticamente a la mejor opción.
5. El visitante puede seleccionar la mejor opción para consultar su detalle.

---

### RF-13. Informar cuando ningún día sea recomendable

Si ninguna fecha alcanza el nivel mínimo para considerarse recomendada, el sistema deberá identificar la mejor alternativa disponible y mostrar una advertencia.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Se identifica una mejor alternativa comparativa.
2. La interfaz no clasifica falsamente esa fecha como recomendada.
3. Se muestra un mensaje indicando que ninguno de los siete días presenta condiciones completamente recomendables.
4. La tarjeta correspondiente puede conservar la etiqueta de mejor alternativa, diferenciada de una recomendación favorable.

---

### RF-14. Resolver empates entre fechas

El sistema deberá resolver empates de manera determinista.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Ante igual puntuación de conveniencia, se prioriza la fecha con menor afluencia.
2. Si el empate continúa, se prioriza la fecha más cercana.
3. Una misma entrada y una misma versión del motor producen siempre la misma selección.
4. La regla se aplica tanto para la mejor opción como para la mejor alternativa disponible.

---

### RF-15. Mostrar enlaces oficiales

El sistema deberá ofrecer acceso a fuentes externas relacionadas con la visita.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Se ofrece un enlace hacia la información oficial del Parque Nacional Tingo María.
2. Se ofrece un enlace hacia el portal oficial de entradas, cuando corresponda.
3. Se ofrece un enlace externo para consultar cómo llegar.
4. Los enlaces externos se identifican como tales.
5. La aplicación no utiliza el servicio de mapas como fuente autoritativa de horarios, cierres o disponibilidad.

---

### RF-16. Mostrar advertencias de alcance y vigencia

El sistema deberá mostrar advertencias sobre el carácter estimado de los resultados y la necesidad de consultar fuentes oficiales.

**Prioridad:** Obligatoria.

**Criterios de aceptación:**

1. Se indica que la afluencia diaria es una estimación académica.
2. Se indica que los registros diarios se derivan de datos mensuales oficiales y una distribución sintética.
3. Se aclara que la puntuación no representa ocupación ni conteo en tiempo real.
4. Se recomienda verificar horarios, entradas, restricciones y avisos en los canales oficiales.
5. La advertencia es visible sin necesidad de iniciar sesión.

---

## 7. Requisitos de datos

### RD-01. Almacenar registros históricos mensuales

El sistema deberá conservar los registros mensuales oficiales utilizados por el proyecto.

**Criterios de aceptación:**

1. Cada registro identifica el año y el mes.
2. Cada registro conserva el total mensual oficial.
3. Cuando estén disponibles, se conservan los valores de visitantes nacionales y extranjeros.
4. Cada registro mantiene la referencia o identificación de su fuente.
5. El sistema impide la duplicación lógica del mismo destino, año, mes y fuente.

---

### RD-02. Diferenciar disponibilidad y valor cero

El sistema deberá diferenciar entre un valor igual a cero y un dato no publicado o incompleto.

**Criterios de aceptación:**

1. Un mes no publicado no se almacena como cero.
2. Los estados de disponibilidad pueden distinguir, como mínimo, entre disponible, no disponible todavía, incompleto y cero reportado.
3. El procesamiento excluye de los cálculos los periodos no disponibles según las reglas del motor.
4. Los meses posteriores a agosto de 2026 no se interpretan automáticamente como meses sin visitantes.

---

### RD-03. Utilizar el periodo regular definido

El motor deberá utilizar como referencia regular los datos desde enero de 2022 hasta el último mes oficial disponible.

**Criterios de aceptación:**

1. Los datos anteriores a 2022 no participan en el patrón regular del MVP.
2. Los registros anteriores pueden conservarse sin influir en el cálculo.
3. El periodo efectivo utilizado queda identificable en los resultados o registros técnicos de la ejecución.
4. La ampliación del periodo con nuevos datos oficiales no requiere modificar manualmente cada requisito funcional.

---

### RD-04. Generar datos diarios sintéticos de forma reproducible

El sistema deberá disponer de un proceso reproducible para generar la distribución diaria sintética a partir de los totales mensuales.

**Criterios de aceptación:**

1. El mismo conjunto de entradas, configuración y versión produce el mismo resultado.
2. Cada registro diario sintético identifica su fecha.
3. Cada registro se identifica explícitamente como sintético.
4. El proceso registra o permite identificar la versión del generador.
5. La generación puede repetirse cuando cambien los parámetros del motor.

---

### RD-05. Conservar el total mensual

La distribución diaria sintética deberá conservar el total mensual oficial.

**Criterios de aceptación:**

1. La suma de los registros diarios sintéticos de un mes coincide con el total mensual oficial correspondiente.
2. La validación se realiza para cada mes procesado.
3. Un mes que no supera esta validación no se considera apto para el cálculo del MVP.
4. Los ajustes por redondeo no alteran el total mensual final.

---

### RD-06. Mantener un calendario turístico local

El sistema deberá disponer de una configuración local y versionada para fechas o periodos especiales.

**Criterios de aceptación:**

1. El día de la semana se calcula a partir de la fecha.
2. Los fines de semana se identifican sin almacenar individualmente todos los días del año.
3. Los feriados, periodos especiales y excepciones se mantienen en una configuración separada de la lógica principal.
4. Cada excepción puede incluir nombre, tipo, fecha o intervalo y referencia de su origen.
5. La configuración puede actualizarse sin reescribir el motor completo.

---

### RD-07. Importar actualizaciones históricas mediante un proceso reproducible

El sistema deberá permitir incorporar nuevos registros oficiales mediante un archivo y un proceso de importación controlado.

**Criterios de aceptación:**

1. La importación valida la estructura mínima del archivo.
2. La importación identifica registros inválidos o duplicados.
3. La importación no requiere un panel administrativo.
4. La importación conserva la fuente de los datos.
5. La ejecución del proceso queda documentada para poder repetirse.

---

### RD-08. Conservar la trazabilidad de las predicciones

El sistema deberá conservar información suficiente para identificar cómo se produjo una predicción.

**Criterios de aceptación:**

1. La predicción identifica la fecha evaluada.
2. La predicción identifica la versión del motor.
3. La predicción conserva las puntuaciones resultantes.
4. La predicción permite identificar los datos meteorológicos y factores principales utilizados.
5. La trazabilidad no requiere almacenar datos personales del visitante.

---

## 8. Requisitos de integración

### RI-01. Consumir una API meteorológica

El sistema deberá obtener el pronóstico meteorológico diario mediante una API externa.

**Criterios de aceptación:**

1. La integración obtiene información correspondiente a las coordenadas del destino.
2. La respuesta cubre el horizonte necesario para el dashboard.
3. Los datos externos se transforman a un formato interno controlado.
4. La lógica principal no depende directamente de los nombres específicos de los campos del proveedor.
5. La sustitución futura del proveedor no obliga a rediseñar toda la interfaz del usuario.

---

### RI-02. Reutilizar temporalmente el pronóstico vigente

El sistema deberá permitir reutilizar un pronóstico previamente obtenido mientras se considere vigente.

**Criterios de aceptación:**

1. Seleccionar diferentes tarjetas no provoca necesariamente una nueva solicitud externa por cada día.
2. Una respuesta con varios días puede utilizarse para construir todo el horizonte semanal.
3. El sistema conserva la fecha y hora de obtención del pronóstico.
4. La duración exacta de vigencia se define en la arquitectura.

---

### RI-03. Limitar las integraciones externas del MVP

El MVP no deberá depender de una API de tránsito, una API de calendario, autenticación externa ni una API propia de venta de entradas.

**Criterios de aceptación:**

1. Los feriados y periodos especiales se resuelven mediante configuración local.
2. Los enlaces de entradas redirigen hacia el canal oficial, sin procesar pagos.
3. La ubicación puede abrir un enlace externo, sin requerir una integración avanzada de mapas.
4. La ausencia de estas integraciones no impide el funcionamiento central del MVP.

---

## 9. Requisitos de interfaz y experiencia

### RUI-01. Utilizar el dashboard como página principal

La aplicación deberá presentar como página principal el dashboard de decisión de visita.

**Criterios de aceptación:**

1. El visitante accede directamente a la comparación de los siete días.
2. No se requiere autenticación previa.
3. El detalle del día seleccionado y las tarjetas semanales están disponibles en la misma vista.
4. No existe una sección histórica visible para el usuario en el MVP.

---

### RUI-02. Mostrar el detalle del día seleccionado

El panel principal deberá mostrar, como mínimo:

- Destino turístico.
- Fecha seleccionada.
- Puntuación y nivel de afluencia.
- Puntuación y categoría de conveniencia.
- Resumen meteorológico.
- Recomendación textual.
- Factores principales.
- Advertencia metodológica.
- Enlaces oficiales.

**Criterios de aceptación:**

1. La información corresponde a la fecha seleccionada.
2. La jerarquía visual permite distinguir las mediciones principales.
3. El visitante puede localizar la recomendación sin revisar contenido técnico.
4. El panel no presenta gráficos históricos ajenos a la decisión inmediata.

---

### RUI-03. Mostrar siete tarjetas comparables

El dashboard deberá incluir una tarjeta para cada fecha del horizonte.

**Criterios de aceptación:**

1. Todas las tarjetas utilizan una estructura consistente.
2. Cada tarjeta muestra la fecha, afluencia, conveniencia o recomendación y un resumen meteorológico.
3. La mejor opción se distingue mediante una etiqueta adicional.
4. La tarjeta seleccionada se distingue sin ocultar su categoría de recomendación.
5. La comparación puede comprenderse sin abrir siete páginas diferentes.

---

### RUI-04. No mostrar una sección histórica

El MVP no deberá exponer al visitante gráficos o páginas de evolución histórica.

**Criterios de aceptación:**

1. No se presenta una pestaña de histórico turístico.
2. No se presentan comparaciones anuales o mensuales en la experiencia pública.
3. Los datos históricos permanecen como insumo interno del motor.
4. La exclusión de la sección histórica no impide explicar el origen de los datos en la advertencia metodológica.

---

### RUI-05. Adaptar la interfaz a escritorio y móvil

La aplicación deberá ofrecer una experiencia utilizable en pantallas de escritorio y teléfonos móviles.

**Criterios de aceptación:**

1. El contenido principal puede leerse sin desplazamiento horizontal general de la página.
2. Las tarjetas de los siete días pueden consultarse en móvil mediante una disposición adaptable o desplazamiento controlado.
3. Los controles seleccionables tienen un tamaño apropiado para interacción táctil.
4. Las puntuaciones, categorías y advertencias permanecen legibles.

---

### RUI-06. Presentar la aplicación en español

Todos los textos visibles del MVP deberán estar en español.

**Criterios de aceptación:**

1. Etiquetas, mensajes, recomendaciones y errores visibles están en español.
2. Las fechas se presentan con formato comprensible para el público objetivo.
3. Los valores provenientes de proveedores externos se traducen o transforman cuando sea necesario.

---

### RUI-07. Mantener accesible la codificación visual

La interfaz deberá complementar los colores con texto, iconos o patrones visuales.

**Criterios de aceptación:**

1. Verde, ámbar y rojo no son el único medio para comunicar la recomendación.
2. Las categorías aparecen escritas.
3. Existe contraste suficiente entre texto y fondo.
4. Los elementos interactivos pueden identificarse visualmente.

---

## 10. Requisitos no funcionales

### RNF-01. Mantenibilidad

La solución deberá separar la lógica de presentación, integración, tratamiento de datos y estimación para permitir cambios controlados.

**Criterios de aceptación:**

1. Las reglas del motor no están dispersas en componentes visuales.
2. Las integraciones externas se encuentran aisladas de la lógica central.
3. Las configuraciones de calendario y parámetros pueden versionarse.
4. Las responsabilidades principales están documentadas.

---

### RNF-02. Extensibilidad

La solución deberá permitir incorporar nuevos destinos, fuentes de datos o implementaciones del motor sin rehacer completamente la experiencia principal.

**Criterios de aceptación:**

1. La lógica no utiliza funciones o estructuras exclusivamente nombradas para la Cueva de las Lechuzas cuando corresponde una entidad turística general.
2. El destino inicial se maneja como un registro o configuración del sistema.
3. La interfaz consume resultados mediante estructuras que podrían reutilizarse con otro destino.
4. La evolución futura no forma parte del MVP, pero no queda bloqueada por decisiones rígidas innecesarias.

---

### RNF-03. Reproducibilidad

Los datos sintéticos y las predicciones deberán poder reproducirse cuando se utilicen las mismas entradas, reglas y versiones.

**Criterios de aceptación:**

1. El generador sintético dispone de versión identificable.
2. Cualquier variación pseudoaleatoria utiliza un mecanismo controlado y reproducible.
3. Las reglas y configuraciones usadas pueden recuperarse desde el repositorio o el almacenamiento definido.
4. Una prueba automatizada puede comprobar la conservación mensual.

---

### RNF-04. Rendimiento percibido

La página principal deberá ofrecer una respuesta adecuada para una consulta de siete días.

**Criterios de aceptación:**

1. Cambiar entre días ya cargados actualiza la vista sin repetir todo el proceso de carga.
2. La aplicación evita solicitudes meteorológicas por cada interacción con una tarjeta.
3. El diseño no exige descargar información histórica innecesaria para mostrar el dashboard.
4. Las metas cuantitativas se establecerán durante la arquitectura y las pruebas.

---

### RNF-05. Seguridad básica

La solución deberá proteger configuraciones sensibles y validar la información que procesa.

**Criterios de aceptación:**

1. Las credenciales, si fueran necesarias, no se incluyen en el repositorio público.
2. Las entradas provenientes de archivos o servicios externos se validan antes de persistirse.
3. La aplicación no solicita datos personales al visitante.
4. Los enlaces externos se gestionan de forma segura.

---

### RNF-06. Observabilidad

Los componentes del sistema deberán producir información suficiente para diagnosticar fallos y revisar ejecuciones importantes.

**Criterios de aceptación:**

1. Se registran los errores de integración meteorológica.
2. Se registran los errores de importación y generación sintética.
3. Se puede identificar la versión del motor utilizada en una predicción.
4. No se registran secretos ni información personal inexistente o innecesaria.
5. La herramienta concreta se definirá en la arquitectura de AWS.

---

### RNF-07. Despliegue en la nube

El MVP deberá poder desplegarse en Amazon Web Services.

**Criterios de aceptación:**

1. Los componentes desplegables están documentados.
2. La configuración de entorno no queda codificada directamente en el código fuente.
3. La aplicación desplegada es accesible mediante una URL para la demostración.
4. La selección de servicios concretos se define en el documento de arquitectura y despliegue.

---

### RNF-08. Arquitectura de microservicios

La solución deberá implementar una arquitectura de microservicios con responsabilidades justificables y contratos bien definidos.

> **Nota:** Este documento no predetermina ni acota el número de microservicios. La cantidad de servicios, sus límites y sus responsabilidades son una decisión de arquitectura que se fijará en el documento de arquitectura de software. Implementar un número arbitrario de servicios sin sustento funcional contradiría el criterio 3.

**Criterios de aceptación:**

1. Los servicios definidos poseen responsabilidades diferenciadas.
2. La comunicación entre servicios utiliza contratos explícitos.
3. La división evita crear servicios sin una responsabilidad funcional clara.
4. El número y los límites precisos de los servicios se fijan en la arquitectura.

---

### RNF-09. Documentación para desarrollo asistido por IA

El proyecto deberá mantener documentación suficiente para que agentes de desarrollo implementen cambios sin reinterpretar decisiones fundamentales.

**Criterios de aceptación:**

1. El alcance y los requisitos están versionados en el repositorio.
2. Las decisiones del motor y la arquitectura se documentan por separado.
3. Los criterios de aceptación pueden convertirse en tareas y pruebas.
4. Las instrucciones para agentes no contradicen los documentos principales.

---

### RNF-10. Pruebas

El sistema deberá contar con pruebas sobre la lógica crítica del MVP.

**Criterios de aceptación:**

1. Existen pruebas para la conservación de totales mensuales.
2. Existen pruebas para la clasificación de afluencia y conveniencia.
3. Existen pruebas para la selección de la mejor opción y los desempates.
4. Existen pruebas para la transformación de datos meteorológicos.
5. Existen pruebas para las validaciones principales de importación.
6. La estrategia completa se detallará en el documento de pruebas.

---

## 11. Reglas de negocio identificadas

### RN-01. Horizonte semanal

El dashboard público evalúa hoy y los seis días siguientes.

### RN-02. Afluencia y conveniencia son resultados diferentes

La afluencia expresa el nivel relativo de concurrencia esperado. La conveniencia expresa qué tan apropiada resulta la visita al considerar la afluencia y las condiciones meteorológicas.

### RN-03. La afluencia no representa ocupación

Una puntuación de afluencia de 80 no significa que el lugar esté ocupado al 80 % ni que exista una probabilidad del 80 % de encontrar visitantes.

### RN-04. Los datos diarios son sintéticos

La distribución diaria utilizada por el MVP se deriva de totales mensuales oficiales y reglas documentadas.

### RN-05. Conservación mensual

La suma de los valores diarios sintéticos de un mes debe coincidir con el total mensual oficial.

### RN-06. Periodo regular

El patrón regular del MVP utiliza información desde enero de 2022 hasta el último mes oficial disponible.

### RN-07. Clasificación de afluencia

Toda puntuación de afluencia se clasifica como baja, media o alta según los umbrales vigentes.

### RN-08. Clasificación de conveniencia

Toda puntuación de conveniencia con información suficiente se clasifica como recomendada, visitable con precaución o no recomendada.

### RN-09. Color asociado a recomendación

La codificación verde, ámbar y roja corresponde a la recomendación de visita, no directamente al nivel de afluencia.

### RN-10. Mejor opción

La mejor opción se obtiene comparando la conveniencia de los siete días mediante las reglas del motor.

### RN-11. Mejor alternativa desfavorable

Si ningún día alcanza el mínimo de recomendación, el sistema identifica la mejor alternativa y advierte que ninguna fecha es completamente recomendable.

### RN-12. Desempate

Ante igual conveniencia se prioriza la menor afluencia; si el empate continúa, se prioriza la fecha más cercana.

### RN-13. Verificación oficial

La recomendación del sistema no reemplaza la consulta de horarios, entradas, cierres ni restricciones en los canales oficiales.

### RN-14. Datos futuros no publicados

La ausencia de un registro mensual futuro no equivale a cero visitantes.

### RN-15. Recomendación completa y meteorología

La conveniencia completa requiere información meteorológica disponible para la fecha evaluada.

---

## 12. Exclusiones explícitas del MVP

> **Alineación con `01-definicion-y-alcance-del-proyecto.md`:** Una versión anterior del documento de alcance (sección 16.3) contemplaba una sección histórica visible para el usuario con evolución mensual, comparación anual y distribución de visitantes. Esa funcionalidad fue descartada en este documento (ver RUI-04). El documento de alcance ha sido actualizado para reflejar esta decisión.

El MVP no incluirá:

- Inicio de sesión.
- Registro de usuarios.
- Recuperación de contraseñas.
- Gestión de perfiles.
- Roles y permisos de usuario.
- Favoritos.
- Intención de visita.
- Comentarios.
- Calificaciones.
- Panel administrativo.
- Reservaciones.
- Venta propia de entradas.
- Procesamiento de pagos.
- Notificaciones.
- Chat.
- Aplicación móvil nativa.
- Geolocalización en tiempo real.
- Predicción por horas.
- Conteo de visitantes en tiempo real.
- Cámaras o sensores.
- API de tránsito.
- API externa de calendario.
- Scraping de Google Maps.
- Sección histórica visible.
- Selección de fechas fuera de los siete días.
- Múltiples destinos implementados en el MVP.
- Recomendaciones personalizadas.
- Machine learning complejo como requisito obligatorio.

---

## 13. Matriz de trazabilidad resumida

| Objetivo del MVP | Caso de uso | Requisitos relacionados |
|---|---|---|
| Consultar los próximos siete días | CU-01 | RF-01, RF-02, RF-04, RF-05, RF-06, RF-07, RF-08, RF-09 |
| Consultar el detalle de una fecha | CU-02 | RF-03, RF-04, RF-05, RF-06, RF-07, RF-09, RF-10, RF-11, RF-16 |
| Identificar el mejor día | CU-03 | RF-12, RF-13, RF-14 |
| Verificar información oficial | CU-04 | RF-15, RF-16 |
| Utilizar registros oficiales | CU-01, CU-02, CU-03 | RD-01, RD-02, RD-03, RD-07 |
| Construir la base diaria sintética | CU-01, CU-02, CU-03 | RD-04, RD-05, RD-06, RNF-03 |
| Integrar el clima | CU-01, CU-02, CU-03 | RI-01, RI-02 |
| Presentar el dashboard público | CU-01, CU-02, CU-03, CU-04 | RUI-01, RUI-02, RUI-03, RUI-04, RUI-05, RUI-06, RUI-07 |
| Mantener una solución ampliable | Todos | RNF-01, RNF-02, RNF-08, RNF-09 |

---

## 14. Definición general de terminado del MVP

El MVP se considerará funcionalmente terminado cuando:

1. La aplicación desplegada presenta hoy y los seis días siguientes.
2. Hoy aparece seleccionado inicialmente.
3. El visitante puede seleccionar cualquiera de las siete tarjetas.
4. Cada día presenta afluencia, conveniencia y clima.
5. Las tarjetas utilizan color y texto según la recomendación.
6. El sistema identifica la mejor opción o la mejor alternativa disponible.
7. El detalle muestra una recomendación textual y factores principales.
8. Se muestran las advertencias metodológicas y los enlaces oficiales.
9. Los datos mensuales oficiales han sido importados correctamente.
10. La distribución diaria sintética es reproducible y conserva los totales mensuales.
11. La integración meteorológica cubre el horizonte del dashboard.
12. La interfaz funciona en escritorio y móvil.
13. No se requiere autenticación.
14. La solución está desplegada en AWS y disponible para la demostración.
15. Las pruebas críticas del motor, los datos y la integración se ejecutan satisfactoriamente.

---

## 15. Elementos pendientes de documentos posteriores

### 15.1. Especificación del motor de estimación

Deberá definir:

- Método para obtener la referencia mensual.
- Factores por día de la semana.
- Tratamiento de feriados y periodos especiales.
- Método de distribución diaria.
- Variación sintética y semilla.
- Corrección de redondeos.
- Variables meteorológicas seleccionadas.
- Factores meteorológicos.
- Normalización de afluencia entre 0 y 100.
- Umbrales de afluencia.
- Fórmula de conveniencia.
- Umbrales de recomendación.
- Condición mínima para considerar un día recomendado.
- Selección de la mejor opción.
- Escenarios y pruebas de cálculo.

### 15.2. Arquitectura de software

Deberá definir:

- Límites y responsabilidades de los microservicios.
- Contratos de comunicación.
- Tecnología de frontend y backend.
- Base de datos.
- Caché meteorológica.
- Manejo técnico de fallos.
- Observabilidad.
- Seguridad.
- Contenedores.
- CI/CD.
- Servicios concretos de AWS.

### 15.3. Diseño de interfaz

Deberá definir:

- Wireframes.
- Jerarquía visual.
- Diseño de las tarjetas.
- Estados de carga y error.
- Colores definitivos y contraste.
- Comportamiento adaptable.
- Iconografía.

---

## 16. Resumen

El sistema ofrecerá un dashboard público y adaptable que mostrará hoy y los seis días siguientes para la Cueva de las Lechuzas. Cada fecha tendrá una puntuación y nivel de afluencia, una puntuación y categoría de conveniencia, un resumen meteorológico y una codificación visual. El visitante podrá seleccionar cualquiera de los siete días y consultar el detalle dentro de la misma página.

El sistema identificará la mejor opción de la semana o, cuando todas las condiciones sean desfavorables, la mejor alternativa disponible con una advertencia. La estimación utilizará registros mensuales oficiales desde 2022, una distribución diaria sintética reproducible, un calendario turístico local y un pronóstico meteorológico externo. La aplicación no tendrá usuarios, panel administrativo, sección histórica, predicción horaria ni integraciones de tráfico o calendario.

## Alineación de implementación (2026-10-06)

La plataforma aprobada por el usuario es AWS: EC2 para STP, SMS y PostgreSQL 16; AWS Amplify Hosting para el frontend. Esta decisión descarta los anexos anteriores de otros proveedores y mantiene el requisito académico de AWS.
Los documentos 03–06 ya existen; las referencias anteriores a su elaboración pendiente
son históricas. Las precisiones de cálculo y fallos están en docs/03 §16 y docs/05 §9.
