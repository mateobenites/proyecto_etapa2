# operaciones.py
# Logica del sistema: altas, asignaciones, devoluciones, cambios de estado,
# calculos, reportes y la funcion recursiva.
#
# A diferencia de la etapa 1, estas funciones NO usan print ni input:
# reciben los datos por parametro y devuelven resultados. Si algo no se
# puede hacer, lanzan ValueError con el motivo. Asi se pueden probar con pytest.
#
# Estructuras que se usan:
#   equipos     -> diccionario {codigo: {"tipo", "estado", "legajo"}}
#   empleados   -> diccionario {legajo: {"nombre", "departamento"}}
#   movimientos -> lista de diccionarios (un diccionario por movimiento)

from datetime import datetime


# ---------------------------------------------------------------
# Movimientos
# ---------------------------------------------------------------

def crear_movimiento(codigo, legajo, tipo_movimiento, estado_anterior, estado_nuevo, usuario, detalle):
    """Arma el diccionario de un movimiento con la fecha y la hora actuales."""
    ahora = datetime.now()
    movimiento = {
        "fecha": ahora.strftime("%d/%m/%Y"),
        "hora": ahora.strftime("%H:%M:%S"),
        "codigo": codigo,
        "legajo": legajo,
        "tipo_movimiento": tipo_movimiento,
        "estado_anterior": estado_anterior,
        "estado_nuevo": estado_nuevo,
        "usuario": usuario,
        "detalle": detalle
    }
    return movimiento


# ---------------------------------------------------------------
# Altas y operaciones sobre equipos
# ---------------------------------------------------------------

def registrar_equipo(equipos, codigo, tipo, usuario):
    """Agrega un equipo nuevo en estado Disponible y devuelve el movimiento de alta.
    El codigo tiene que venir validado (formato y prefijo)."""
    if codigo in equipos:
        raise ValueError("Ya existe un equipo con el codigo " + codigo + ".")

    equipos[codigo] = {"tipo": tipo, "estado": "Disponible", "legajo": ""}
    return crear_movimiento(codigo, "", "alta", "", "Disponible", usuario, "Alta de equipo " + tipo)


def registrar_empleado(empleados, legajo, nombre, departamento):
    """Agrega un empleado nuevo. Los datos tienen que venir validados."""
    if legajo in empleados:
        raise ValueError("Ya existe un empleado con el legajo " + legajo + ".")

    empleados[legajo] = {"nombre": nombre, "departamento": departamento}


def asignar_equipo(equipos, empleados, codigo, legajo, usuario):
    """Asigna un equipo Disponible a un empleado. Devuelve el movimiento."""
    if codigo not in equipos:
        raise ValueError("No existe un equipo con el codigo " + codigo + ".")
    if legajo not in empleados:
        raise ValueError("No existe un empleado con el legajo " + legajo + ".")

    equipo = equipos[codigo]
    if equipo["estado"] != "Disponible":
        raise ValueError("El equipo tiene que estar Disponible para poder asignarlo (estado actual: " + equipo["estado"] + ").")

    equipo["estado"] = "Asignado"
    equipo["legajo"] = legajo

    detalle = "Asignado a " + empleados[legajo]["nombre"]
    return crear_movimiento(codigo, legajo, "asignacion", "Disponible", "Asignado", usuario, detalle)


def devolver_equipo(equipos, empleados, codigo, usuario):
    """Registra la devolucion de un equipo Asignado. Vuelve a Disponible y queda sin empleado."""
    if codigo not in equipos:
        raise ValueError("No existe un equipo con el codigo " + codigo + ".")

    equipo = equipos[codigo]
    if equipo["estado"] != "Asignado":
        raise ValueError("Solo se puede devolver un equipo Asignado (estado actual: " + equipo["estado"] + ").")

    legajo = equipo["legajo"]
    if legajo in empleados:
        detalle = "Devuelto por " + empleados[legajo]["nombre"]
    else:
        # caso de un equipo asignado a un legajo que no existe: se corrige devolviendolo
        detalle = "Devolucion de equipo asignado a un legajo inexistente"

    equipo["estado"] = "Disponible"
    equipo["legajo"] = ""
    return crear_movimiento(codigo, legajo, "devolucion", "Asignado", "Disponible", usuario, detalle)


def cambiar_estado(equipos, codigo, nuevo_estado, transiciones, usuario, detalle):
    """Cambia el estado de un equipo si la transicion esta permitida en la configuracion.
    Asignar y devolver tienen sus propias opciones, por eso aca no se permiten."""
    if codigo not in equipos:
        raise ValueError("No existe un equipo con el codigo " + codigo + ".")

    equipo = equipos[codigo]
    estado_actual = equipo["estado"]

    if nuevo_estado == estado_actual:
        raise ValueError("El equipo ya esta en estado " + estado_actual + ".")
    if estado_actual == "Asignado":
        raise ValueError("El equipo esta Asignado. Primero hay que registrar la devolucion (opcion 4).")
    if nuevo_estado == "Asignado":
        raise ValueError("Para asignar un equipo se usa la opcion 3.")

    # Asignado no se muestra entre las opciones porque se hace con la opcion 3
    permitidos = [estado for estado in transiciones[estado_actual] if estado != "Asignado"]
    if len(permitidos) == 0:
        raise ValueError("Un equipo " + estado_actual + " no puede cambiar de estado.")
    if nuevo_estado not in permitidos:
        raise ValueError("Desde " + estado_actual + " solo se puede pasar a: " + ", ".join(permitidos) + ".")

    equipo["estado"] = nuevo_estado
    return crear_movimiento(codigo, "", "cambio_estado", estado_actual, nuevo_estado, usuario, detalle)


# ---------------------------------------------------------------
# Busquedas y filtros
# ---------------------------------------------------------------

def equipos_de_empleado(equipos, legajo):
    """Devuelve la lista de codigos de los equipos que tiene asignados un empleado."""
    return [codigo for codigo in equipos if equipos[codigo]["legajo"] == legajo]


def filtrar_equipos(equipos, empleados, campo, valor):
    """Devuelve los codigos de los equipos que cumplen el filtro.
    campo puede ser "estado", "tipo" o "departamento"."""
    resultado = []
    for codigo in equipos:
        equipo = equipos[codigo]
        if campo == "departamento":
            legajo = equipo["legajo"]
            if legajo in empleados and empleados[legajo]["departamento"] == valor:
                resultado.append(codigo)
        elif equipo[campo] == valor:
            resultado.append(codigo)
    return resultado


def movimientos_por_fecha(movimientos, fecha):
    return [mov for mov in movimientos if mov["fecha"] == fecha]


def movimientos_por_equipo(movimientos, codigo):
    return [mov for mov in movimientos if mov["codigo"] == codigo]


def contar_movimientos_equipo(movimientos, codigo, i=0):
    """Cuenta en forma RECURSIVA cuantos movimientos tiene un equipo.
    Recorre la lista de a un elemento por vez usando el indice i.
    - Caso base: i llego al final de la lista, no quedan movimientos para revisar -> 0.
    - Caso recursivo: miro el movimiento i y le sumo lo que da el resto de la lista (i + 1).
    Como i aumenta en cada llamada, siempre se llega al caso base."""
    if i == len(movimientos):
        return 0
    if movimientos[i]["codigo"] == codigo:
        return 1 + contar_movimientos_equipo(movimientos, codigo, i + 1)
    else:
        return 0 + contar_movimientos_equipo(movimientos, codigo, i + 1)


# ---------------------------------------------------------------
# Calculos y acumulaciones
# ---------------------------------------------------------------

def contar_por_estado(equipos, estados):
    """Diccionario acumulador: cuantos equipos hay en cada estado."""
    conteo = {}
    for estado in estados:
        conteo[estado] = 0
    for codigo in equipos:
        estado = equipos[codigo]["estado"]
        conteo[estado] = conteo.get(estado, 0) + 1
    return conteo


def porcentaje_asignados(equipos):
    """Porcentaje de equipos en estado Asignado sobre el total. Si no hay equipos devuelve 0."""
    if len(equipos) == 0:
        return 0
    asignados = 0
    for codigo in equipos:
        if equipos[codigo]["estado"] == "Asignado":
            asignados += 1
    return asignados / len(equipos) * 100


def asignados_por_departamento_y_tipo(equipos, empleados, departamentos, tipos):
    """Reemplaza a la matriz de la etapa 1. Devuelve un diccionario de diccionarios:
    {"Ventas": {"Desktop": 0, "Notebook": 1, ...}, "Sistemas": {...}, ...}
    Se arma de nuevo cada vez que se necesita, a partir de equipos y empleados."""
    resultado = {}
    for depto in departamentos:
        resultado[depto] = {}
        for tipo in tipos.values():
            resultado[depto][tipo] = 0

    for codigo in equipos:
        equipo = equipos[codigo]
        legajo = equipo["legajo"]
        if equipo["estado"] == "Asignado" and legajo in empleados:
            depto = empleados[legajo]["departamento"]
            tipo = equipo["tipo"]
            resultado[depto][tipo] = resultado[depto][tipo] + 1

    return resultado


def total_por_departamento(por_depto_y_tipo):
    totales = {}
    for depto in por_depto_y_tipo:
        totales[depto] = sum(por_depto_y_tipo[depto].values())
    return totales


def total_por_tipo(por_depto_y_tipo):
    totales = {}
    for depto in por_depto_y_tipo:
        for tipo in por_depto_y_tipo[depto]:
            totales[tipo] = totales.get(tipo, 0) + por_depto_y_tipo[depto][tipo]
    return totales


def departamentos_con_mas_equipos(totales_depto):
    """Devuelve la lista de departamentos con mas equipos asignados (puede haber empate)
    y la cantidad. Si nadie tiene equipos devuelve una lista vacia."""
    if len(totales_depto) == 0:
        return [], 0
    maximo = max(totales_depto.values())
    if maximo == 0:
        return [], 0
    ganadores = [depto for depto in totales_depto if totales_depto[depto] == maximo]
    return ganadores, maximo


def ranking_departamentos(totales_depto):
    """Misma funcion de la etapa 1, adaptada a diccionarios.
    Ordena de mayor a menor con una lambda y devuelve los 3 primeros (slicing)."""
    totales = list(totales_depto.items())   # lista de tuplas (departamento, cantidad)

    obtener_cantidad = lambda x: x[1]

    for i in range(len(totales)):
        indice_mayor = i
        for j in range(i + 1, len(totales)):
            if obtener_cantidad(totales[j]) > obtener_cantidad(totales[indice_mayor]):
                indice_mayor = j
        totales[i], totales[indice_mayor] = totales[indice_mayor], totales[i]

    return totales[:3]


# ---------------------------------------------------------------
# Alertas y condiciones criticas
# ---------------------------------------------------------------

def tipos_con_baja_disponibilidad(equipos, tipos, minimo):
    """Devuelve un diccionario {tipo: cantidad_disponible} con los tipos que tienen
    MENOS unidades disponibles que el minimo de la configuracion."""
    disponibles = {}
    for tipo in tipos.values():
        disponibles[tipo] = 0
    for codigo in equipos:
        equipo = equipos[codigo]
        if equipo["estado"] == "Disponible":
            disponibles[equipo["tipo"]] = disponibles.get(equipo["tipo"], 0) + 1

    alertas = {}
    for tipo in disponibles:
        if disponibles[tipo] < minimo:
            alertas[tipo] = disponibles[tipo]
    return alertas


def equipos_con_legajo_inexistente(equipos, empleados):
    """Equipos que figuran asignados a un legajo que no esta en empleados."""
    return [codigo for codigo in equipos
            if equipos[codigo]["legajo"] != "" and equipos[codigo]["legajo"] not in empleados]


def equipos_con_estado_inconsistente(equipos, movimientos):
    """Devuelve un diccionario {codigo: estado_del_ultimo_movimiento} con los equipos cuyo
    estado actual no coincide con el estado nuevo de su ultimo movimiento.
    Los movimientos estan del mas viejo al mas nuevo. Al recorrerlos y guardar
    ultimo_estado[codigo], la clave se pisa en cada vuelta, asi que al final cada
    equipo queda con el estado de su ultimo movimiento.
    Los equipos sin movimientos no se revisan."""
    ultimo_estado = {}
    for mov in movimientos:
        ultimo_estado[mov["codigo"]] = mov["estado_nuevo"]

    inconsistentes = {}
    for codigo in equipos:
        if codigo in ultimo_estado and ultimo_estado[codigo] != equipos[codigo]["estado"]:
            inconsistentes[codigo] = ultimo_estado[codigo]
    return inconsistentes


def resumen_unicos(equipos, empleados, movimientos):
    """Resumen armado con conjuntos (valores sin repetir)."""
    # empleados que tienen al menos un equipo asignado
    empleados_con_equipo = set()
    for codigo in equipos:
        legajo = equipos[codigo]["legajo"]
        if legajo in empleados:
            empleados_con_equipo.add(legajo)

    # con la resta de conjuntos salen los que no tienen ninguno
    empleados_sin_equipo = set(empleados) - empleados_con_equipo

    # tipos de equipo que alguna vez pasaron a En reparacion
    tipos_en_reparacion = set()
    for mov in movimientos:
        if mov["estado_nuevo"] == "En reparacion" and mov["codigo"] in equipos:
            tipos_en_reparacion.add(equipos[mov["codigo"]]["tipo"])

    # departamentos de los empleados que aparecen en algun movimiento
    departamentos_con_movimientos = set()
    for mov in movimientos:
        if mov["legajo"] in empleados:
            departamentos_con_movimientos.add(empleados[mov["legajo"]]["departamento"])

    return {
        "empleados_con_equipo": empleados_con_equipo,
        "empleados_sin_equipo": empleados_sin_equipo,
        "tipos_en_reparacion": tipos_en_reparacion,
        "departamentos_con_movimientos": departamentos_con_movimientos
    }


# ---------------------------------------------------------------
# Reportes (devuelven una lista de lineas, main.py las guarda en el .txt)
# ---------------------------------------------------------------

def encabezado_reporte(titulo, usuario):
    ahora = datetime.now()
    return [
        titulo,
        "Generado el " + ahora.strftime("%d/%m/%Y") + " a las " + ahora.strftime("%H:%M:%S") + " por " + usuario,
        "-" * 50
    ]


def armar_reporte_general(equipos, empleados, config, usuario):
    lineas = encabezado_reporte("REPORTE GENERAL DEL INVENTARIO", usuario)

    lineas.append("Cantidad total de equipos: " + str(len(equipos)))
    lineas.append("")
    lineas.append("Cantidad por estado:")
    por_estado = contar_por_estado(equipos, config["estados"])
    for estado in por_estado:
        lineas.append("  " + estado + ": " + str(por_estado[estado]))

    lineas.append("")
    lineas.append("Porcentaje de equipos asignados: " + str(round(porcentaje_asignados(equipos), 2)) + " %")

    tabla = asignados_por_departamento_y_tipo(equipos, empleados, config["departamentos"], config["tipos"])
    totales_depto = total_por_departamento(tabla)

    ganadores, maximo = departamentos_con_mas_equipos(totales_depto)
    if len(ganadores) == 0:
        lineas.append("Departamento con mas equipos asignados: ninguno tiene equipos asignados")
    else:
        lineas.append("Departamento con mas equipos asignados: " + ", ".join(ganadores) + " (" + str(maximo) + ")")

    lineas.append("")
    lineas.append("Ranking de departamentos:")
    ranking = ranking_departamentos(totales_depto)
    for i in range(len(ranking)):
        lineas.append("  " + str(i + 1) + ". " + ranking[i][0] + ": " + str(ranking[i][1]))

    return lineas


def armar_reporte_alertas(equipos, empleados, movimientos, config, descartados, usuario):
    """Devuelve las lineas del reporte de alertas y la cantidad de incidencias encontradas.
    Las incidencias no se corrigen solas: solo se informan."""
    lineas = encabezado_reporte("REPORTE DE ALERTAS E INCIDENCIAS", usuario)
    cantidad = 0

    lineas.append("Tipos con baja disponibilidad (minimo " + str(config["minimo_disponibles"]) + "):")
    baja = tipos_con_baja_disponibilidad(equipos, config["tipos"], config["minimo_disponibles"])
    if len(baja) == 0:
        lineas.append("  Ninguno")
    for tipo in baja:
        lineas.append("  - " + tipo + ": " + str(baja[tipo]) + " disponible(s)")
        cantidad += 1

    lineas.append("")
    lineas.append("Equipos asignados a empleados que no existen:")
    inexistentes = equipos_con_legajo_inexistente(equipos, empleados)
    if len(inexistentes) == 0:
        lineas.append("  Ninguno")
    for codigo in inexistentes:
        lineas.append("  - " + codigo + " (legajo " + equipos[codigo]["legajo"] + "). Corregir registrando la devolucion.")
        cantidad += 1

    lineas.append("")
    lineas.append("Filas invalidas encontradas en los archivos (ver descartados.txt):")
    if len(descartados) == 0:
        lineas.append("  Ninguna")
    for fila in descartados:
        lineas.append("  - " + fila["archivo"] + " linea " + str(fila["linea"]) + ": " + fila["motivo"])
        cantidad += 1

    lineas.append("")
    lineas.append("Equipos cuyo estado no coincide con su ultimo movimiento:")
    inconsistentes = equipos_con_estado_inconsistente(equipos, movimientos)
    if len(inconsistentes) == 0:
        lineas.append("  Ninguno")
    for codigo in inconsistentes:
        lineas.append("  - " + codigo + ": figura " + equipos[codigo]["estado"] + " pero su ultimo movimiento dice "
                      + inconsistentes[codigo] + ". Revisar manualmente.")
        cantidad += 1

    lineas.append("")
    lineas.append("Total de incidencias: " + str(cantidad))
    return lineas, cantidad
