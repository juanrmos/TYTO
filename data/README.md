# Datos

Esta carpeta contiene los datos utilizados por el proyecto Tyto — estimación de afluencia turística en la Cueva de las Lechuzas.

**Documentos de referencia:**
- `docs/01-definicion-y-alcance-del-proyecto.md`
- `docs/02-requisitos-del-sistema.md`

---

## Estructura

```
data/
├── raw/
│   └── Tabla_data.csv          ← Archivo original oficial (INMUTABLE)
├── processed/
│   ├── visitas_mensuales_completas.csv   ← Todos los meses válidos disponibles
│   └── visitas_mensuales_modelo.csv      ← Solo los meses del periodo regular del motor
└── reports/
    └── calidad_datos_mensuales.json      ← Reporte de calidad generado automáticamente
```

---

## Archivo original

`data/raw/Tabla_data.csv` contiene los registros mensuales oficiales de visitantes publicados por MINCETUR correspondientes al Parque Nacional de Tingo María, sector Cueva de las Lechuzas.

**Este archivo es inmutable.** No debe modificarse, ni sobrescribirse, ni completarse manualmente. Cualquier actualización consiste en reemplazarlo por una nueva versión oficial y volver a ejecutar el proceso.

**Estructura del archivo original:**

| Columna            | Descripción                                  |
|--------------------|----------------------------------------------|
| `Mes`              | Nombre del mes en español                    |
| `Año`              | Año de cuatro dígitos                        |
| `Tipo de Visitante`| `Nacional` o `Extranjero`                    |
| `Llegadas`         | Total de visitantes del periodo              |

- Delimitador: `;` (punto y coma)
- Codificación: UTF-8
- Una fila por tipo de visitante por mes

---

## Cómo ejecutar el proceso

Desde la raíz del repositorio:

```bash
python scripts/normalize_monthly_visitors.py
```

El script:
1. Lee `data/raw/Tabla_data.csv` sin modificarlo.
2. Detecta automáticamente el delimitador y la codificación.
3. Valida todas las filas.
4. Genera los tres archivos de salida.

Si el proceso encuentra errores de validación, termina con un mensaje claro y no produce salidas parciales.

---

## Cómo ejecutar las pruebas

```bash
pytest scripts/test_normalize_monthly_visitors.py -v
```

---

## Archivos producidos

### `visitas_mensuales_completas.csv`

Contiene **todos los meses válidos** presentes en el archivo oficial, desde 2019 hasta el último mes disponible.

Cada fila representa un mes completo con:

| Columna              | Descripción                                         |
|----------------------|-----------------------------------------------------|
| `year`               | Año numérico                                        |
| `month`              | Número de mes (1–12)                                |
| `month_start`        | Fecha ISO del primer día del periodo (p.ej. `2022-01-01`) |
| `national_visitors`  | Visitantes nacionales del mes                       |
| `foreign_visitors`   | Visitantes extranjeros del mes                      |
| `total_visitors`     | Suma de nacionales y extranjeros                    |

La columna `month_start` representa el mes como periodo, no indica que el conteo se realizó ese día.

### `visitas_mensuales_modelo.csv`

Contiene **únicamente los meses del periodo regular del motor**: desde enero de 2022 hasta el último mes disponible en el archivo oficial (determinado automáticamente al procesar).

Los registros anteriores a 2022 permanecen en el archivo completo pero no influyen en el patrón regular de estimación (ver `docs/01-definicion-y-alcance-del-proyecto.md`, sección 10.1).

### `data/reports/calidad_datos_mensuales.json`

Reporte de calidad calculado automáticamente. Incluye:

- Ruta del archivo de entrada.
- Fecha y hora de procesamiento.
- Delimitador detectado y codificación utilizada.
- Columnas originales y cantidad de filas.
- Cobertura temporal detectada (completa y del modelo).
- Duplicados, meses incompletos y valores inválidos encontrados.
- Advertencias por limpiezas aplicadas.
- Resultado de cada validación.
- Rutas de los archivos producidos.

---

## Diferencia entre el CSV completo y el CSV del modelo

| Aspecto                    | Completo                          | Modelo                              |
|----------------------------|-----------------------------------|-------------------------------------|
| Cobertura                  | Todos los años disponibles        | Enero 2022 en adelante              |
| Uso                        | Trazabilidad e histórico          | Base para el motor de estimación    |
| Incluye datos pre-pandemia | Sí (2019–2021)                    | No                                  |

---

## Validaciones realizadas

El proceso falla de forma explícita si encuentra:

- Mes desconocido (incluyendo variantes no reconocidas de nombres en español).
- Año inválido.
- Tipo de visitante distinto de Nacional o Extranjero.
- Cantidad no convertible a entero.
- Cantidad negativa.
- Más de un registro para el mismo año, mes y tipo de visitante.
- Mes con solo nacionales o solo extranjeros (categoría faltante).
- Total mensual inconsistente (total ≠ nacional + extranjero).
- Columnas obligatorias ausentes en el archivo.

Los ceros presentes en el archivo son valores oficiales y se conservan tal como aparecen.

---

## Lo que este proceso NO hace

Este proceso **no genera datos diarios sintéticos**. Su único objetivo es transformar el CSV oficial en registros mensuales normalizados y validados.

La generación diaria sintética, los factores de distribución, la semilla de reproducibilidad y la conservación del total mensual serán definidos en:

> `docs/03-especificacion-motor-estimacion.md` (documento pendiente de elaboración)

---

## Reproducibilidad

Ejecutar el script con el mismo archivo de entrada produce siempre el mismo resultado. No existe estado externo ni aleatoriedad en el proceso de normalización.
