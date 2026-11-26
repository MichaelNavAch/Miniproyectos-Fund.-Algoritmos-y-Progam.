# Copa Loyola

Proyecto de Fundamentos de Algoritmos y Programación, Pontificia Universidad Javeriana.

Aplicación en Python con interfaz en Tkinter para gestionar la Copa Loyola: universidades, deportistas, disciplinas, inscripciones, resultados, medallero y estadísticas.

## Integrantes

- Johan Sebastian Villota Tarazona
- Michael Navarrete Achicanoy

## Contenido

**Mini_Proyecto_1**
- `Codigo/MiniProyectoCopa1.py`: programa de la primera entrega.
- `Diagramas_Flujo/`: diagramas de flujo de las funciones.
- `Mini_Proyecto_1_Copa_Loyola.pdf`: enunciado.

**Mini_Proyecto_2**
- `Codigo/MiniProyectoCopa2.py`: programa de la segunda entrega. Agrega guardar y cargar los datos en JSON, el medallero en CSV, la detección de registros repetidos con conjuntos y el reporte con Pandas.
- `Codigo/copa_loyola_datos.json`: datos de ejemplo.
- `Codigo/medallero.csv` y `Codigo/reporte_copa_loyola.csv`: archivos generados durante las pruebas.
- `Diagramas_Flujo/`: diagramas de flujo de las funciones nuevas (el archivo `.drawio` se abre en app.diagrams.net).
- `Mini_Proyecto_2_Copa_Loyola.pdf`: enunciado.

## Distribución del trabajo (Mini Proyecto 2)

| Integrante | Parte | Funciones |
|---|---|---|
| Sebastian Villota | Manejo de archivos JSON y conjuntos | `ruta`, `datos_a_json`, `es_texto`, `validar_estructura`, `detectar_duplicados`, `avisar_duplicados`, `resumen_datos`, `guardar_datos`, `reemplazar_datos`, `cargar_datos` |
| Michael Navarrete | Medallero CSV y reporte con Pandas | `mostrar_info`, `generar_medallero_csv`, `crear_dataframe_resultados`, `calcular_reporte`, `buscar_ganadoras`, `exportar_reporte_csv`, `mostrar_ventana_reporte`, `generar_reporte` |

Los dos integrantes trabajaron juntos en la pestaña "Consultas / Archivos / Reportes" de la interfaz.

## Ejecución

```
pip install -r requirements.txt
python Mini_Proyecto_2/Codigo/MiniProyectoCopa2.py
```
