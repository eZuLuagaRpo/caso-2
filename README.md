# Caso de Estudio 2: Pruebas de Software

Este proyecto fue realizado por Camilo Herrera-Arcila, M.Sc. Prohibido todo su uso y distribución sin previa autorización del autor. Para solicitar más información, escriba a [camilo.arcila97@gmail.com](mailto:camilo.arcila97@gmail.com) y su propósito es solamente educativo para la Universidad de San Buenaventura - Medellín en el curso de Pruebas de Software.

## Descripción del Proyecto

Este proyecto tiene como objetivo proporcionar una experiencia práctica en la generación y ejecución de pruebas de software unitarias e integración, utilizando Pytest y Allure. Se deberá implementar dobles de prueba, gestionar archivos, y aplicar fixtures para el correcto manejo del entorno de pruebas.

## Estructura del Proyecto

El proyecto tiene la siguiente estructura de carpetas:

```text
proyecto/
├── modules/
│   ├── __init__.py
│   |── _00spinner.py
│   |── _01authentication.py
│   |── _02request.py
│   |── _03analytics.py
│   └── _04report.py
├── data/
│   |── input/
│   |── output/
├── assets/
│   |── usb.jpg
├── tests/
└── main.py
```

## Antes de comenzar

Crea el entorno virtual en la raíz del proyecto:

```bash
python -m venv venv
```

Activa el entorno virtual:

```bash
venv/scripts/activate
```

Instala las dependencias necesarias con `pip`:

```bash
pip install -r requirements.txt
```

## Funcionalidad

El sistema incluye módulos para la generación de reportes y la manipulación de datos relacionados con un sistema de bicicletas públicas. Deberán probar la funcionalidad de los siguientes módulos:

- **_01authentication.py**: Autenticación de usuarios requerido para el uso del sistema de analítica.
- **_02request.py**: Descarga los datos desde una URL proporcionada y los guarda como un archivo Excel en `data/input/`.
- **_03analytics.py**: Realiza el análisis de los datos, incluyendo rutas populares, distancias entre estaciones, y duración promedio de las rutas.
- **_04report.py**: Genera un reporte en PDF con las rutas más populares, las distancias más grandes, las rutas con mayor duración promedio y un mapa de las estaciones de bicicletas.
- **main.py**: El sistema de analítica que depende de todos los demás módulos. Debe generar correctamente el reporte y analizar sin problemas la información.

## Consideraciones

El mapa de las estaciones se genera usando geopandas y contextily para agregar un mapa base, por lo que se requiere conexión a internet para descargar los mapas de fondo. En caso de errores en la conexión para obtener los mapas, se omitirán los mapas base y solo se mostrarán las estaciones. Los archivos PDF generados se abrirán automáticamente (en Windows) al finalizar el proceso.
  
## Actividad a Realizar

1. **Mejoramiento de analítica y reporte**: Complemente el modulo de analítica con la estimación de parámetros estadísticos como promedio, varianza, desviación estandar, máximo, mínimo, percentiles 25%, 50% y 75%. Cada uno de estos debe ser generado para la duración de los viajes y las distancias. Estos nuevos indicadores deben ser agregados como una tabla en el reporte automático. Es un plus incluir gráficos adicionales en el reporte.
2. **Generación de Pruebas**:
   - Crear pruebas unitarias y de integración del sistema.
   - Almacenar todas las pruebas en la carpeta `tests/`.
   - Ejecutar las pruebas utilizando Pytest.

3. **Aplicación de Dobles de Prueba**:
   - Implementar dobles de prueba donde sea necesario.

4. **Gestión de Archivos**:
   - Utilizar `tmp_path` y `tmp_path_factory` para la gestión de archivos temporales en las pruebas.

5. **Uso de Fixtures**:
   - Aplicar fixtures para la configuración y limpieza de pruebas (`setUp` y `tearDown`).

6. **Informe Escrito**:
   - Elaborar un informe escrito que contenga:
     - Introducción
     - Resumen ejecutivo con el resultado de todas las pruebas.
     - Sección detallada por cada prueba con:
       - Precondiciones
       - Procesos
       - Post-condiciones
       - Resultado (pasó/no pasó)
       - Recomendación de solución en caso de no pasar.
       - Solución implementada.

7. **Informe Digital con Allure**:
   - Utilizar Allure para generar un informe digital.
   - Incluir metadatos en cada prueba utilizando decoradores de Allure como `@allure.title`, `@allure.issue`, y todas las demás vistas en clase (consulte la página web de allure para más detalles).

### Comandos para Generar el Informe con Allure

Para generar el informe con Allure, utiliza los siguientes comandos:

```bash
# Ejecutar las pruebas y generar el reporte
pytest --alluredir allure-results

# Generar el informe visual
allure generate allure-report
```

## Entregables

Los entregables para esta actividad son:

1. Informe escrito en formato PDF o Word.
2. Informe de Allure generado.
3. Proyecto comprimido en formato ZIP que incluya todas las pruebas en la carpeta `tests/`.

### Fecha Límite de Entrega

La fecha límite para la entrega de todos los documentos es el miércoles 09 de octubre a media noche, en la carpeta `/Entregas/Caso1/apellido_nombre_psoft_caso2.zip`.

## Rúbricas de Evaluación

La evaluación se realizará con base en los siguientes criterios:

1. **Calidad de las Pruebas (40%):** Cobertura de casos de prueba. Uso adecuado de dobles de prueba. Aplicación de fixtures.

2. **Informe Escrito (40%):** Claridad y estructura del informe. Detalle de las pruebas y resultados.

3. **Informe de Allure (20%):** Complejidad de las pruebas y uso adecuado de metadatos que se muestran en el informe html.

¡Buena suerte con el caso de estudio! Si tienen alguna pregunta, no duden en preguntar.
