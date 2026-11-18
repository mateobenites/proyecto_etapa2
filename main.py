# main.py
# Unico modulo que interactua con el usuario (input y print).
# Hace el login, carga los archivos, muestra el menu y atrapa las excepciones
# que lanzan los otros modulos para mostrarlas como mensajes de error.
#
# No hay variables globales: los datos se cargan dentro de main()
# y se pasan por parametro a las funciones que los necesitan.

import json

import archivos
import validaciones
import operaciones


# Login

def iniciar_sesion(usuarios):
    # Pide usuario y contrasena, con 3 intentos. Devuelve el usuario o "" si se agotan.
    print("\n--- INICIO DE SESION ---")
    intentos = 0
    while intentos < 3:
        usuario = input("Usuario: ").strip()
        contrasena = input("Contrasena: ").strip()
        if validaciones.validar_login(usuario, contrasena, usuarios):
            print("Bienvenido/a,", usuario)
            return usuario
        intentos += 1
        print("Usuario o contrasena incorrectos. Intentos restantes:", 3 - intentos)
    return ""


# Funciones auxiliares

def guardar_operacion(equipos, movimientos, codigo, copia, movimiento):
    # Guarda equipos.csv y despues agrega el movimiento en movimientos.csv.
    # La operacion solo se confirma si se guardan los dos archivos. Si falla alguno,
    # el equipo vuelve a como estaba (copia) y se vuelve a guardar equipos.csv.
    # copia es None cuando es un alta: en ese caso deshacer es borrar el equipo nuevo.
    try:
        archivos.guardar_equipos(equipos)
        archivos.agregar_movimiento(movimiento)
    except PermissionError:
        print("Error: no hay permiso para escribir los archivos.")
        print("Revisar que equipos.csv y movimientos.csv no esten abiertos en otro programa (por ejemplo Excel).")
    except OSError as error:
        print("Error al guardar los archivos:", error)
    else:
        # solo llega aca si no hubo ningun error
        movimientos.append(movimiento)
        return True

    # Si llego aca es porque hubo un error: se deshace la operacion en memoria
    if copia is None:
        del equipos[codigo]
    else:
        equipos[codigo] = copia

    # y se intenta dejar equipos.csv como estaba
    try:
        archivos.guardar_equipos(equipos)
    except OSError:
        print("Atencion: tampoco se pudo restaurar", archivos.ARCHIVO_EQUIPOS)

    print("La operacion no se completo correctamente.")
    print("Verifique los archivos antes de realizar otra operacion.")
    return False



def pedir_estado(config):
    print("Estados:", ", ".join(config["estados"]))
    estado = input("Estado: ").strip().capitalize()

    if estado == "En reparacion":
        estado = "En reparación"

    validaciones.validar_en_lista(estado, config["estados"], "Estado")
    return estado



def pedir_departamento(config):
    print("Departamentos:", ", ".join(config["departamentos"]))
    departamento = input("Departamento: ").strip().capitalize()
    if departamento == "Administracion":
        departamento = "Administración"
    validaciones.validar_en_lista(departamento, config["departamentos"], "Departamento")
    return departamento


def mostrar_equipo(codigo, equipo, empleados):
    texto = codigo + " | " + equipo["tipo"] + " | " + equipo["estado"]
    legajo = equipo["legajo"]
    if legajo != "":
        if legajo in empleados:
            texto += " | " + empleados[legajo]["nombre"] + " (" + empleados[legajo]["departamento"] + ")"
        else:
            texto += " | legajo " + legajo + " (no existe)"
    print(texto)


def mostrar_movimiento(mov):
    texto = mov["fecha"] + " " + mov["hora"] + " | " + mov["codigo"] + " | " + mov["tipo_movimiento"]
    if mov["estado_anterior"] != "":
        texto += " | " + mov["estado_anterior"] + " -> " + mov["estado_nuevo"]
    else:
        texto += " | " + mov["estado_nuevo"]
    if mov["legajo"] != "":
        texto += " | legajo " + mov["legajo"]
    texto += " | " + mov["usuario"] + " | " + mov["detalle"]
    print(texto)


def mostrar_menu(usuario):
    print("\n--- GESTIÓN DE EQUIPAMIENTO --- (usuario: " + usuario + ")")
    print("0. Acerca del sistema")
    print("1. Registrar equipo")
    print("2. Registrar empleado")
    print("3. Asignar equipo")
    print("4. Registrar devolución")
    print("5. Modificar estado de equipo")
    print("6. Buscar equipo")
    print("7. Consultar equipos de un empleado")
    print("8. Listar inventario")
    print("9. Estadísticas e informes")
    print("10. Historial de movimientos")
    print("11. Generar reportes en archivo")
    print("12. Salir")


def generar_alertas(equipos, empleados, movimientos, config, descartados, usuario):
    # Arma el reporte de alertas, lo guarda en alertas.txt y devuelve la cantidad de incidencias.
    lineas, cantidad = operaciones.armar_reporte_alertas(equipos, empleados, movimientos, config, descartados, usuario)
    try:
        archivos.guardar_texto(archivos.ARCHIVO_ALERTAS, lineas)
    except OSError:
        print("Error: no se pudo guardar", archivos.ARCHIVO_ALERTAS)
    return cantidad


# Opciones del menu

def opcion_acerca():
    print("\n--- ACERCA DEL SISTEMA ---")
    print("Sistema de Administración de Equipamiento Tecnológico (Etapa 2).")
    print("Permite registrar equipos y empleados, asignar y devolver dispositivos,")
    print("controlar su estado y consultar estadisticas del inventario.")
    print("Desde esta etapa los datos se guardan en archivos CSV, cada operacion")
    print("queda registrada en el historial de movimientos y se pueden generar")
    print("reportes y alertas en archivos de texto.")


def opcion_registrar_equipo(config, equipos, movimientos, usuario):
    print("Prefijos validos:", ", ".join(config["tipos"]))
    codigo = input("Ingrese el codigo del equipo (ej: NTB-0001): ").strip().upper()

    try:
        tipo = validaciones.validar_codigo(codigo, config["tipos"])
        movimiento = operaciones.registrar_equipo(equipos, codigo, tipo, usuario)
    except ValueError as error:
        print("Error:", error)
        return

    if guardar_operacion(equipos, movimientos, codigo, None, movimiento):
        print("Equipo", codigo, "(" + tipo + ") registrado correctamente.")


def opcion_registrar_empleado(config, empleados):
    # cada dato se valida apenas se ingresa, asi no se piden los demas si el primero ya esta mal
    try:
        legajo = input("Ingrese el numero de legajo (" + str(config["legajo_minimo"]) + " a " + str(config["legajo_maximo"]) + "): ").strip()
        validaciones.validar_legajo(legajo, config["legajo_minimo"], config["legajo_maximo"])
        if legajo in empleados:
            raise ValueError("Ya existe un empleado con el legajo " + legajo + ".")

        nombre = input("Ingrese el nombre y apellido: ").strip()
        validaciones.validar_obligatorio(nombre, "nombre y apellido")
        validaciones.validar_sin_separador(nombre, "nombre y apellido")

        departamento = pedir_departamento(config)

        operaciones.registrar_empleado(empleados, legajo, nombre, departamento)
    except ValueError as error:
        print("Error:", error)
        return

    try:
        archivos.agregar_empleado(legajo, empleados[legajo])
    except OSError:
        del empleados[legajo]
        print("Error: no se pudo guardar el empleado en", archivos.ARCHIVO_EMPLEADOS + ". No se registro.")
        return

    print("Empleado registrado correctamente.")


def opcion_asignar(config, equipos, empleados, movimientos, usuario):
    codigo = input("Ingrese el codigo del equipo a asignar: ").strip().upper()
    legajo = input("Ingrese el legajo del empleado: ").strip()

    try:
        validaciones.validar_codigo(codigo, config["tipos"])
        validaciones.validar_legajo(legajo, config["legajo_minimo"], config["legajo_maximo"])
    except ValueError as error:
        print("Error:", error)
        return

    if codigo not in equipos:
        print("Error: no existe un equipo con el codigo", codigo)
        return

    copia = equipos[codigo].copy()  # copia de seguridad por si falla el guardado
    try:
        movimiento = operaciones.asignar_equipo(equipos, empleados, codigo, legajo, usuario)
    except ValueError as error:
        print("Error:", error)
        return

    if guardar_operacion(equipos, movimientos, codigo, copia, movimiento):
        print("Equipo asignado correctamente a", empleados[legajo]["nombre"])


def opcion_devolver(config, equipos, empleados, movimientos, usuario):
    codigo = input("Ingrese el codigo del equipo a devolver: ").strip().upper()

    try:
        validaciones.validar_codigo(codigo, config["tipos"])
    except ValueError as error:
        print("Error:", error)
        return

    if codigo not in equipos:
        print("Error: no existe un equipo con el codigo", codigo)
        return

    copia = equipos[codigo].copy()
    try:
        movimiento = operaciones.devolver_equipo(equipos, empleados, codigo, usuario)
    except ValueError as error:
        print("Error:", error)
        return

    if guardar_operacion(equipos, movimientos, codigo, copia, movimiento):
        print("Devolucion registrada. El equipo", codigo, "vuelve a estar Disponible.")


def opcion_modificar_estado(config, equipos, movimientos, usuario):
    codigo = input("Ingrese el codigo del equipo: ").strip().upper()

    try:
        validaciones.validar_codigo(codigo, config["tipos"])
    except ValueError as error:
        print("Error:", error)
        return

    if codigo not in equipos:
        print("Error: no existe un equipo con el codigo", codigo)
        return

    print("Estado actual:", equipos[codigo]["estado"])
    copia = equipos[codigo].copy()
    try:
        nuevo_estado = pedir_estado(config)
        detalle = input("Motivo del cambio (opcional): ").strip()
        validaciones.validar_sin_separador(detalle, "motivo")
        if detalle == "":
            detalle = "Cambio de estado"
        movimiento = operaciones.cambiar_estado(equipos, codigo, nuevo_estado, config["transiciones"], usuario, detalle)
    except ValueError as error:
        print("Error:", error)
        return

    if guardar_operacion(equipos, movimientos, codigo, copia, movimiento):
        print("Estado actualizado correctamente.")


def opcion_buscar_equipo(config, equipos, empleados, movimientos):
    codigo = input("Codigo del equipo: ").strip().upper()

    try:
        validaciones.validar_codigo(codigo, config["tipos"])
    except ValueError as error:
        print("Error:", error)
        return

    if codigo not in equipos:
        print("No existe ese equipo.")
        return

    equipo = equipos[codigo]
    print("\nCodigo:", codigo)
    print("Tipo:", equipo["tipo"])
    print("Estado:", equipo["estado"])

    legajo = equipo["legajo"]
    if legajo == "":
        print("Empleado: sin asignar")
    elif legajo in empleados:
        print("Empleado:", empleados[legajo]["nombre"], "- legajo", legajo, "-", empleados[legajo]["departamento"])
    else:
        print("Empleado: legajo", legajo, "(ATENCION: ese empleado no existe)")

    # la funcion recursiva hace una llamada por cada movimiento del historial.
    # Si el historial fuera muy largo se pasaria del limite de llamadas de Python.
    try:
        cantidad = operaciones.contar_movimientos_equipo(movimientos, codigo)
        print("Movimientos registrados:", cantidad)
    except RecursionError:
        print("Movimientos registrados: no se pudo calcular, el historial es demasiado largo.")


def opcion_equipos_empleado(config, equipos, empleados):
    legajo = input("Legajo del empleado: ").strip()

    try:
        validaciones.validar_legajo(legajo, config["legajo_minimo"], config["legajo_maximo"])
    except ValueError as error:
        print("Error:", error)
        return

    if legajo not in empleados:
        print("No existe ese empleado.")
        return

    empleado = empleados[legajo]
    print("\n" + empleado["nombre"], "-", empleado["departamento"])

    codigos = operaciones.equipos_de_empleado(equipos, legajo)
    if len(codigos) == 0:
        print("No tiene equipos asignados.")
    for codigo in codigos:
        print(" -", codigo, equipos[codigo]["tipo"], equipos[codigo]["estado"])


def opcion_listar_inventario(config, equipos, empleados):
    print("\n--- LISTAR INVENTARIO ---")
    print("1. Todos los equipos")
    print("2. Filtrar por estado")
    print("3. Filtrar por tipo")
    print("4. Filtrar por departamento")
    filtro = input("Seleccione una opcion: ").strip()

    try:
        if filtro == "1":
            codigos = list(equipos)
        elif filtro == "2":
            estado = pedir_estado(config)
            codigos = operaciones.filtrar_equipos(equipos, empleados, "estado", estado)
        elif filtro == "3":
            tipos = list(config["tipos"].values())
            print("Tipos:", ", ".join(tipos))
            tipo = input("Tipo: ").strip().capitalize()
            validaciones.validar_en_lista(tipo, tipos, "Tipo")
            codigos = operaciones.filtrar_equipos(equipos, empleados, "tipo", tipo)
        elif filtro == "4":
            departamento = pedir_departamento(config)
            codigos = operaciones.filtrar_equipos(equipos, empleados, "departamento", departamento)
        else:
            print("Opcion invalida.")
            return
    except ValueError as error:
        print("Error:", error)
        return

    if len(codigos) == 0:
        print("No hay equipos para mostrar.")
        return

    print()
    for codigo in codigos:
        mostrar_equipo(codigo, equipos[codigo], empleados)
    print("Total:", len(codigos), "equipo(s)")


def opcion_estadisticas(config, equipos, empleados, movimientos):
    print("\n=== ESTADÍSTICAS E INFORMES ===")

    print("\n--- Resumen general ---")
    print("Cantidad total de equipos:", len(equipos))
    por_estado = operaciones.contar_por_estado(equipos, config["estados"])
    for estado in por_estado:
        print(" ", estado + ":", por_estado[estado])
    print("Porcentaje de equipos asignados:", round(operaciones.porcentaje_asignados(equipos), 2), "%")
    print("Equipos en reparacion:", por_estado.get("En reparación", 0))

    tabla = operaciones.asignados_por_departamento_y_tipo(equipos, empleados, config["departamentos"], config["tipos"])

    print("\n--- Equipos asignados por departamento y tipo ---")
    for depto in tabla:
        detalle = ""
        for tipo in tabla[depto]:
            detalle += tipo + ": " + str(tabla[depto][tipo]) + "   "
        print(" ", depto + " ->", detalle)

    totales_depto = operaciones.total_por_departamento(tabla)
    print("\n--- Totales por departamento ---")
    for depto in totales_depto:
        print(" ", depto + ":", totales_depto[depto])

    totales_tipo = operaciones.total_por_tipo(tabla)
    print("\n--- Totales por tipo de equipo ---")
    for tipo in totales_tipo:
        print(" ", tipo + ":", totales_tipo[tipo])

    print("\n--- Departamento con mas equipos asignados ---")
    ganadores, maximo = operaciones.departamentos_con_mas_equipos(totales_depto)
    if len(ganadores) == 0:
        print("No hay equipos asignados.")
    for depto in ganadores:
        print(" ", depto + ":", maximo)

    print("\n--- Ranking de departamentos ---")
    ranking = operaciones.ranking_departamentos(totales_depto)
    for depto, cantidad in ranking:
        print(" ", depto + ":", cantidad)

    print("\n--- Alertas de baja disponibilidad ---")
    baja = operaciones.tipos_con_baja_disponibilidad(equipos, config["tipos"], config["minimo_disponibles"])
    if len(baja) == 0:
        print("No hay tipos con baja disponibilidad.")
    for tipo in baja:
        print("  Alerta:", tipo, "-", baja[tipo], "disponible(s)")

    print("\n--- Resumen de unicos ---")
    unicos = operaciones.resumen_unicos(equipos, empleados, movimientos)

    print("Empleados con al menos un equipo:", len(unicos["empleados_con_equipo"]))
    for legajo in sorted(unicos["empleados_con_equipo"]):
        print("  -", legajo, empleados[legajo]["nombre"])

    print("Empleados sin equipos asignados:", len(unicos["empleados_sin_equipo"]))
    for legajo in sorted(unicos["empleados_sin_equipo"]):
        print("  -", legajo, empleados[legajo]["nombre"])

    print("Tipos de equipo que pasaron por reparacion:", ", ".join(sorted(unicos["tipos_en_reparacion"])))
    print("Departamentos con movimientos:", ", ".join(sorted(unicos["departamentos_con_movimientos"])))


def opcion_historial(config, movimientos):
    print("\n--- HISTORIAL DE MOVIMIENTOS ---")
    print("1. Filtrar por fecha")
    print("2. Filtrar por equipo")
    filtro = input("Seleccione una opcion: ").strip()

    try:
        if filtro == "1":
            fecha = input("Ingrese la fecha (dd/mm/aaaa): ").strip()
            validaciones.validar_fecha(fecha)
            resultado = operaciones.movimientos_por_fecha(movimientos, fecha)
        elif filtro == "2":
            codigo = input("Ingrese el codigo del equipo: ").strip().upper()
            validaciones.validar_codigo(codigo, config["tipos"])
            resultado = operaciones.movimientos_por_equipo(movimientos, codigo)
        else:
            print("Opcion invalida.")
            return
    except ValueError as error:
        print("Error:", error)
        return

    if len(resultado) == 0:
        print("No hay movimientos para ese filtro.")
        return

    print()
    for mov in resultado:
        mostrar_movimiento(mov)
    print("Total:", len(resultado), "movimiento(s)")


def opcion_generar_reportes(config, equipos, empleados, movimientos, descartados, usuario):
    lineas = operaciones.armar_reporte_general(equipos, empleados, config, usuario)
    try:
        archivos.guardar_texto(archivos.ARCHIVO_REPORTE, lineas)
        print("Reporte general guardado en", archivos.ARCHIVO_REPORTE)
    except OSError:
        print("Error: no se pudo guardar", archivos.ARCHIVO_REPORTE)

    cantidad = generar_alertas(equipos, empleados, movimientos, config, descartados, usuario)
    print("Reporte de alertas guardado en", archivos.ARCHIVO_ALERTAS, "(" + str(cantidad) + " incidencias)")


# Programa principal

def main():
    print("=== SISTEMA DE ADMINISTRACION DE EQUIPAMIENTO TECNOLOGICO ===")

    # lista donde se van juntando las filas invalidas de todos los CSV
    descartados = []

    # 1) Archivos obligatorios. Si faltan o estan mal, el programa no sigue.
    try:
        config = archivos.cargar_configuracion()
    except FileNotFoundError:
        print("Error: no se encontro el archivo", archivos.ARCHIVO_CONFIG)
        print("El programa no puede funcionar sin la configuracion.")
        return
    except PermissionError:
        print("Error: no hay permiso para leer", archivos.ARCHIVO_CONFIG)
        return
    except json.JSONDecodeError:  # va antes que ValueError porque JSONDecodeError es un tipo de ValueError
        print("Error: el archivo", archivos.ARCHIVO_CONFIG, "no tiene un formato JSON valido.")
        return
    except ValueError as error:
        print("Error:", error)
        return

    try:
        usuarios = archivos.cargar_usuarios(descartados)
    except FileNotFoundError:
        print("Error: no se encontro el archivo", archivos.ARCHIVO_USUARIOS + ". No se puede iniciar sesion.")
        return
    except PermissionError:
        print("Error: no hay permiso para leer", archivos.ARCHIVO_USUARIOS)
        return
    except ValueError as error:
        print("Error:", error)
        return

    # 2) Login
    usuario = iniciar_sesion(usuarios)
    if usuario == "":
        print("Se agotaron los intentos. El programa finaliza.")
        return

    # 3) Registros. Si un archivo no existe se crea vacio con su encabezado.
    try:
        equipos = archivos.cargar_equipos(config, descartados)
        empleados = archivos.cargar_empleados(config, descartados)
        movimientos = archivos.cargar_movimientos(config, descartados)
    except (OSError, ValueError) as error:
        print("Error al leer los archivos de registros:", error)
        return

    print("Se cargaron", len(equipos), "equipos,", len(empleados), "empleados y", len(movimientos), "movimientos.")

    if len(descartados) > 0:
        print("Se descartaron", len(descartados), "fila(s) invalidas. El contenido original esta en", archivos.ARCHIVO_DESCARTADOS)
        try:
            archivos.registrar_descartados(descartados)
        except OSError:
            print("Error: no se pudo escribir", archivos.ARCHIVO_DESCARTADOS)

    # 4) Alertas al iniciar sesion
    cantidad = generar_alertas(equipos, empleados, movimientos, config, descartados, usuario)
    if cantidad > 0:
        print("Atencion: se detectaron", cantidad, "incidencia(s). El detalle esta en", archivos.ARCHIVO_ALERTAS)

    # 5) Menu
    opcion = ""
    while opcion != "12":
        mostrar_menu(usuario)
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "0":
            opcion_acerca()
        elif opcion == "1":
            opcion_registrar_equipo(config, equipos, movimientos, usuario)
        elif opcion == "2":
            opcion_registrar_empleado(config, empleados)
        elif opcion == "3":
            opcion_asignar(config, equipos, empleados, movimientos, usuario)
        elif opcion == "4":
            opcion_devolver(config, equipos, empleados, movimientos, usuario)
        elif opcion == "5":
            opcion_modificar_estado(config, equipos, movimientos, usuario)
        elif opcion == "6":
            opcion_buscar_equipo(config, equipos, empleados, movimientos)
        elif opcion == "7":
            opcion_equipos_empleado(config, equipos, empleados)
        elif opcion == "8":
            opcion_listar_inventario(config, equipos, empleados)
        elif opcion == "9":
            opcion_estadisticas(config, equipos, empleados, movimientos)
        elif opcion == "10":
            opcion_historial(config, movimientos)
        elif opcion == "11":
            opcion_generar_reportes(config, equipos, empleados, movimientos, descartados, usuario)
        elif opcion == "12":
            print("Programa finalizado. Los datos quedaron guardados.")
        else:
            print("Opción inválida. Intente nuevamente.")


if __name__ == "__main__":
    main()
