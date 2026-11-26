# Copa Loyola — Mini proyectos de programación

Fundamentos de Algoritmos y Programación · Pontificia Universidad Javeriana

Aplicación en Python + Tkinter para gestionar la Copa Loyola, un evento deportivo entre universidades nacionales e internacionales.

| Carpeta | Contenido |
|---|---|
| [`mini-proyecto-1/`](mini-proyecto-1) | Primera entrega: gestión de universidades, deportistas, disciplinas, inscripciones, resultados, medallero y estadísticas. |
| [`mini-proyecto-2/`](mini-proyecto-2) | Segunda entrega: lo anterior + guardar/cargar en JSON, medallero en CSV, detección de repetidos con conjuntos y reporte con Pandas. |

## Estructura

```
mini-proyecto-1/
├── MiniProyectoCopa1.py          programa
├── diagramas/                    diagramas de flujo (25–47) + PDF
└── enunciado/                    enunciado del profesor

mini-proyecto-2/
├── MiniProyectoCopa2.py          programa
├── copa_loyola_datos.json        datos de ejemplo
├── diagramas/                    diagramas de flujo (48–68): .drawio editable, PNG y PDF
└── enunciado/                    enunciado del profesor

requirements.txt                  dependencias (pandas)
```

## Cómo ejecutar

```bash
py -m pip install -r requirements.txt

py mini-proyecto-1/MiniProyectoCopa1.py
py mini-proyecto-2/MiniProyectoCopa2.py
```

En el Mini proyecto 2, en la pestaña **Consultas / Archivos / Reportes**, el botón **Cargar datos (JSON)** carga los datos de ejemplo.

Los diagramas del Mini proyecto 2 se pueden abrir y editar en [app.diagrams.net](https://app.diagrams.net) con `mini-proyecto-2/diagramas/Diagramas_Mini_Proyecto_2.drawio`.

## Mini proyecto 2: reparto de funciones

Las funciones nuevas están en `mini-proyecto-2/MiniProyectoCopa2.py` marcadas con `# PENDIENTE (Parte A)` o `# PENDIENTE (Parte B)`. Cada una ya tiene su comentario de Entradas / Procedimiento / Salidas. Mientras estén pendientes, el botón correspondiente muestra "Función pendiente".

| Parte A — Archivos y conjuntos | Parte B — Pandas y consultas |
|---|---|
| `ruta` | `crear_dataframe_resultados` |
| `datos_a_json` | `calcular_reporte` |
| `es_texto` | `buscar_ganadoras` |
| `validar_estructura` | `exportar_reporte_csv` |
| `detectar_duplicados` | `mostrar_ventana_reporte` |
| `avisar_duplicados` | `generar_reporte` |
| `resumen_datos` | `mostrar_info` |
| `guardar_datos` | `ejecutar_consulta` * |
| `reemplazar_datos` | `calcular_medallero` * |
| `cargar_datos` | `consulta_estadisticas` * |
| `generar_medallero_csv` | |

\* Ya existían en el Mini proyecto 1; por ahora tienen esa versión y hay que actualizarlas a la del Mini proyecto 2 (resultados individuales y `mostrar_info`).

## Cómo trabajamos con Git

Cada parte tiene su rama: `parte-a` y `parte-b`.

```bash
git switch parte-b                  # (o parte-a)
git pull
# ... completar las funciones en mini-proyecto-2/MiniProyectoCopa2.py ...
git add mini-proyecto-2/MiniProyectoCopa2.py
git commit -m "Parte B: reporte con Pandas y consultas"
git push
```

Luego en GitHub: **Pull requests → New pull request**, base `main` ← compare `parte-b`, **Create pull request** y **Merge pull request**. Como cada parte edita funciones distintas, los dos merges entran sin conflictos.
