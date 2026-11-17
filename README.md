# Administración de Equipamiento Tecnológico - Etapa 2

Proyecto Integrador de Programación I - UADE

## Integrantes

- Agostino, Francisco
- Benites, Mateo Gaspar
- Tobar, Thiago Ignacio
- Perez Torres, Stefany Nicole

## Problema

En una organización el equipamiento tecnológico (notebooks, desktops, monitores y celulares) se reparte entre empleados de distintas áreas. Sin un registro ordenado no se sabe qué equipos están disponibles, quién tiene cada uno ni en qué estado están.

En la etapa 1 hicimos un sistema por consola que resolvía esto, pero los datos se perdían al cerrar el programa. En esta etapa el sistema guarda todo en archivos y lo recupera cada vez que se ejecuta.

## Alcance de la etapa 2

- Inicio de sesión con usuario y contraseña leídos de `usuarios.csv` (3 intentos).
- Configuración (estados, departamentos, tipos, transiciones, límites) cargada desde `configuracion.json`.
- Equipos, empleados y movimientos guardados en archivos CSV.
- Historial de movimientos: cada alta, asignación, devolución y cambio de estado queda registrado con fecha, hora y usuario.
- Validaciones con expresiones regulares para el código de equipo, el legajo y la fecha.
- Reportes en archivos de texto: `reporte.txt` (general) y `alertas.txt` (alertas e incidencias).
- Filas inválidas de los CSV guardadas en `descartados.txt`.
- Función recursiva para contar los movimientos de un equipo.
- 7 pruebas unitarias con pytest.

## Requisitos

- Python 3
- pytest (solo para las pruebas): `pip install pytest`

## Cómo ejecutar

Desde la carpeta del proyecto:

```
python main.py
```

Usuarios de prueba (están en `usuarios.csv`):

| Usuario | Contraseña |
| --- | --- |
| fagostino | fran2026 |
| mbenites | mateo2026 |
| ttobar | thiago2026 |
| sperez | stefy2026 |
| admin | admin |

## Cómo ejecutar las pruebas

Desde la carpeta del proyecto:

```
python -m pytest -v
```

Resultado esperado: `7 passed`.

Para guardar la evidencia en un archivo (desde la consola cmd):

```
python -m pytest -v > evidencia_pruebas.txt
```

## Estructura

```
proyecto_etapa2/
├── main.py                 # login, menú, input y print. Atrapa las excepciones y muestra los errores
├── operaciones.py          # altas, asignaciones, devoluciones, cálculos, reportes y recursividad (sin print)
├── validaciones.py         # expresiones regulares y validaciones (lanzan ValueError)
├── archivos.py             # lectura y escritura de CSV, JSON y TXT
├── configuracion.json      # configuración del sistema (obligatorio)
├── usuarios.csv            # usuarios para el login (obligatorio)
├── equipos.csv             # equipos
├── empleados.csv           # empleados
├── movimientos.csv         # historial de movimientos
├── README.md
└── tests/
    └── test_operaciones.py # 7 pruebas unitarias
```

Los archivos `reporte.txt`, `alertas.txt` y `descartados.txt` los genera el programa al usarlo.

## Datos de demostración

Los CSV traen 21 equipos, 8 empleados y 39 movimientos válidos, más algunas filas con errores a propósito para probar la detección de incidencias:

- `equipos.csv`: el código `NTB-08` no respeta el formato.
- `empleados.csv`: a `Ana Torres` le falta el departamento.
- `movimientos.csv`: un movimiento con fecha `31/04/2026`, que no existe.
- `CEL-0005` está asignado al legajo 6012, que no existe.
- `DSK-0005` figura Disponible pero su último movimiento lo pasó a En reparación.

## Menú

```
0. Acerca del sistema
1. Registrar equipo
2. Registrar empleado
3. Asignar equipo
4. Registrar devolución
5. Modificar estado de equipo
6. Buscar equipo (muestra también la cantidad de movimientos)
7. Consultar equipos de un empleado
8. Listar inventario (con filtro por estado, tipo o departamento)
9. Estadísticas e informes
10. Historial de movimientos (filtro por fecha o por equipo)
11. Generar reportes en archivo
12. Salir
```
