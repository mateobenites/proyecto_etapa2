# Pruebas unitarias del sistema.
# Se ejecutan desde la carpeta del proyecto con:  python -m pytest -v
# Cada prueba arma sus propios datos, no se leen los archivos reales del sistema.
# Ninguna prueba usa input ni depende de lo que se muestra por pantalla.

import validaciones
import operaciones


# 1) Validacion correcta
def test_codigo_valido():
    tipos = {"NTB": "Notebook", "MON": "Monitor"}
    assert validaciones.validar_codigo("NTB-0001", tipos) == "Notebook"


# 2) Validacion incorrecta que produce una excepcion
def test_legajo_invalido():
    try:
        validaciones.validar_legajo("12a4", 1000, 9999)
        hubo_error = False
    except ValueError:
        hubo_error = True
    assert hubo_error


# 3) Calculo simple con resultado conocido
def test_porcentaje_asignados():
    equipos = {
        "NTB-0001": {"tipo": "Notebook", "estado": "Asignado", "legajo": "1234"},
        "NTB-0002": {"tipo": "Notebook", "estado": "Disponible", "legajo": ""},
        "MON-0001": {"tipo": "Monitor", "estado": "Disponible", "legajo": ""},
        "CEL-0001": {"tipo": "Celular", "estado": "En reparacion", "legajo": ""}
    }
    assert operaciones.porcentaje_asignados(equipos) == 25


# 4) Acumulacion por clave
def test_contar_por_estado():
    estados = ("Disponible", "Asignado", "En reparacion", "Fuera de servicio")
    equipos = {
        "NTB-0001": {"tipo": "Notebook", "estado": "Asignado", "legajo": "1234"},
        "NTB-0002": {"tipo": "Notebook", "estado": "Disponible", "legajo": ""},
        "MON-0001": {"tipo": "Monitor", "estado": "Disponible", "legajo": ""},
        "CEL-0001": {"tipo": "Celular", "estado": "En reparacion", "legajo": ""}
    }
    esperado = {"Disponible": 2, "Asignado": 1, "En reparacion": 1, "Fuera de servicio": 0}
    assert operaciones.contar_por_estado(equipos, estados) == esperado


# 5) Condicion critica
def test_baja_disponibilidad_monitor():
    tipos = {"MON": "Monitor"}
    equipos = {
        "MON-0001": {"tipo": "Monitor", "estado": "Disponible", "legajo": ""},
        "MON-0002": {"tipo": "Monitor", "estado": "Asignado", "legajo": "1234"}
    }
    alertas = operaciones.tipos_con_baja_disponibilidad(equipos, tipos, 2)
    assert "Monitor" in alertas


# 6) Funcion recursiva
def test_contar_movimientos_recursivo():
    movimientos = [
        {"codigo": "NTB-0001", "tipo_movimiento": "alta"},
        {"codigo": "MON-0001", "tipo_movimiento": "alta"},
        {"codigo": "NTB-0001", "tipo_movimiento": "asignacion"},
        {"codigo": "NTB-0001", "tipo_movimiento": "devolucion"}
    ]
    assert operaciones.contar_movimientos_equipo(movimientos, "NTB-0001") == 3


# 7) Caso limite: inventario vacio y un tipo con exactamente el minimo de disponibles
def test_casos_limite():
    # inventario vacio: no se divide por cero, da 0%
    assert operaciones.porcentaje_asignados({}) == 0

    # con exactamente 2 disponibles y minimo 2 no hay alerta (la alerta es con MENOS del minimo)
    tipos = {"NTB": "Notebook"}
    equipos = {
        "NTB-0001": {"tipo": "Notebook", "estado": "Disponible", "legajo": ""},
        "NTB-0002": {"tipo": "Notebook", "estado": "Disponible", "legajo": ""}
    }
    assert operaciones.tipos_con_baja_disponibilidad(equipos, tipos, 2) == {}
