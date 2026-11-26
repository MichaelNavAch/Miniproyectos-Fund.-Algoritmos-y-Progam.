# Mini proyecto 2 — Copa Loyola

Fundamentos de Algoritmos y Programación · Pontificia Universidad Javeriana

Aplicación en Tkinter para gestionar la Copa Loyola: universidades, deportistas, disciplinas, inscripciones y resultados. El Mini proyecto 2 agrega:

- **Archivos:** guardar y cargar toda la información en `copa_loyola_datos.json` (módulo `json`) y exportar `medallero.csv`.
- **Conjuntos (sets):** detectar universidades, disciplinas, deportistas e inscripciones repetidas antes de guardar.
- **Pandas:** reporte de medallas y puntos por universidad (Oro = 3, Plata = 2, Bronce = 1), con ventana `Toplevel` y exportación a `reporte_copa_loyola.csv`.

## Cómo ejecutarlo

```bash
py -m pip install -r requirements.txt
py MiniProyectoCopa2.py
```

En la pestaña **Consultas / Archivos / Reportes** presione **Cargar datos (JSON)** para cargar los datos de ejemplo de `copa_loyola_datos.json`.

## Estructura

```
MiniProyectoCopa2.py      programa completo (interfaz + funciones)
copa_loyola_datos.json    datos de ejemplo
requirements.txt          dependencias (pandas)
diagramas/                diagramas de flujo de las funciones nuevas
  Diagramas_Mini_Proyecto_2.drawio   editable en app.diagrams.net (una página por función)
  48_...png … 68_...png              un PNG por función
  Diagramas de Flujo-Mini Proyecto 2.pdf
```

## Reparto de funciones

Las funciones nuevas están en `MiniProyectoCopa2.py` marcadas con `# PENDIENTE (Parte A)` o `# PENDIENTE (Parte B)`. Cada una ya tiene su comentario de Entradas / Procedimiento / Salidas; solo falta el cuerpo. Mientras estén pendientes, el botón correspondiente muestra "Función pendiente".

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
git clone <url-del-repositorio>
cd Miniproyecto-programaci-n
git switch parte-a          # o parte-b
# ... completar las funciones ...
git add MiniProyectoCopa2.py
git commit -m "Parte A: guardar y cargar datos en JSON"
git push
```

Cuando una parte esté lista, se abre un **Pull Request** de `parte-a` (o `parte-b`) hacia `main` en GitHub y se hace merge. Como cada uno edita funciones distintas, los dos merges deberían entrar sin conflictos. Antes de empezar a trabajar cada día: `git pull`.
