# archivos.py
# Lectura y escritura de los archivos del sistema (JSON, CSV y TXT).
# Todos los archivos se abren con codificacion UTF-8.
# Los CSV usan ; como separador y la primera fila es el encabezado.
#
# Los errores al ESCRIBIR no se atrapan aca: se dejan pasar para que
# main.py le avise al usuario y deshaga la operacion si hace falta.

import json
from datetime import datetime

import validaciones

ARCHIVO_CONFIG = "configuracion.json"
ARCHIVO_USUARIOS = "usuarios.csv"
ARCHIVO_EQUIPOS = "equipos.csv"
ARCHIVO_EMPLEADOS = "empleados.csv"
ARCHIVO_MOVIMIENTOS = "movimientos.csv"
ARCHIVO_REPORTE = "reporte.txt"
ARCHIVO_ALERTAS = "alertas.txt"
ARCHIVO_DESCARTADOS = "descartados.txt"

SEPARADOR = ";"

ENCABEZADO_USUARIOS = ("usuario", "contrasena")
ENCABEZADO_EQUIPOS = ("codigo", "tipo", "estado", "legajo")
ENCABEZADO_EMPLEADOS = ("legajo", "nombre", "departamento")
ENCABEZADO_MOVIMIENTOS = ("fecha", "hora", "codigo", "legajo", "tipo_movimiento",
                          "estado_anterior", "estado_nuevo", "usuario", "detalle")

CLAVES_CONFIG = ("estados", "departamentos", "tipos", "transiciones",
                 "minimo_disponibles", "legajo_minimo", "legajo_maximo")


# Archivos obligatorios: configuracion y usuarios

def cargar_configuracion():
    # Lee configuracion.json y devuelve un diccionario.
    # Si el archivo no existe tira FileNotFoundError, si no es un JSON valido tira
    # JSONDecodeError y si le falta alguna clave tira ValueError. No se crea uno nuevo
    # porque sin la configuracion el programa no puede funcionar.
    with open(ARCHIVO_CONFIG, "rt", encoding="utf-8") as archivo:
        contenido = archivo.read()

    config = json.loads(contenido)

    for clave in CLAVES_CONFIG:
        if clave not in config:
            raise ValueError("Al archivo " + ARCHIVO_CONFIG + " le falta la clave '" + clave + "'.")

    if not isinstance(config["tipos"], dict):
        raise ValueError("Los tipos de equipo deben estar en un diccionario.")

    if not isinstance(config["estados"], list):
        raise ValueError("Los estados deben estar en una lista.")

    if not isinstance(config["departamentos"], list):
        raise ValueError("Los departamentos deben estar en una lista.")

    if not isinstance(config["transiciones"], dict):
        raise ValueError("Las transiciones deben estar en un diccionario.")
    
    # cada estado tiene que tener su lista de cambios permitidos (puede estar vacia)
    for estado in config["estados"]:
        if estado not in config["transiciones"]:
            raise ValueError("En " + ARCHIVO_CONFIG + " falta el estado '" + estado + "' dentro de transiciones.")

    # los limites tienen que ser numeros enteros
    try:
        config["minimo_disponibles"] = int(config["minimo_disponibles"])
        config["legajo_minimo"] = int(config["legajo_minimo"])
        config["legajo_maximo"] = int(config["legajo_maximo"])
    except (ValueError, TypeError):
        raise ValueError("En " + ARCHIVO_CONFIG + " minimo_disponibles, legajo_minimo y legajo_maximo tienen que ser numeros.")

    # Una vez cargados, los valores fijos se manejan como tuplas (como en la etapa 1)
    config["estados"] = tuple(config["estados"])
    config["departamentos"] = tuple(config["departamentos"])

    return config


def cargar_usuarios(descartados):
    # Lee usuarios.csv y devuelve un diccionario {usuario: contrasena}.
    # Si el archivo no existe tira FileNotFoundError.
    # Las filas incompletas o con el usuario repetido se agregan a descartados.
    usuarios = {}

    with open(ARCHIVO_USUARIOS, "rt", encoding="utf-8") as archivo:
        archivo.readline()  # el encabezado no se procesa
        numero_linea = 1
        for linea in archivo:
            numero_linea += 1
            linea = linea.rstrip("\n")
            if linea.strip() == "":
                continue

            campos = linea.split(SEPARADOR)
            if len(campos) != len(ENCABEZADO_USUARIOS):
                agregar_descartado(descartados, ARCHIVO_USUARIOS, numero_linea, linea, "cantidad de campos incorrecta")
                continue

            usuario = campos[0].strip()
            contrasena = campos[1].strip()
            if usuario == "" or contrasena == "":
                agregar_descartado(descartados, ARCHIVO_USUARIOS, numero_linea, linea, "usuario o contrasena vacios")
            elif usuario in usuarios:
                agregar_descartado(descartados, ARCHIVO_USUARIOS, numero_linea, linea, "usuario repetido")
            else:
                usuarios[usuario] = contrasena

    if len(usuarios) == 0:
        raise ValueError("El archivo " + ARCHIVO_USUARIOS + " no tiene ningun usuario valido.")

    return usuarios


# Funciones generales

def crear_si_no_existe(nombre_archivo, encabezado):
    # Si el archivo no existe, lo crea vacio con su encabezado.
    # Devuelve True si lo tuvo que crear.
    try:
        archivo = open(nombre_archivo, "rt", encoding="utf-8")
        archivo.close()
        return False
    except FileNotFoundError:
        with open(nombre_archivo, "wt", encoding="utf-8") as archivo:
            archivo.write(SEPARADOR.join(encabezado) + "\n")
        return True


def asegurar_salto_final(nombre_archivo):
    # Si la ultima linea del archivo no termina con salto de linea, lo agrega.
    # Puede pasar si alguien edito el CSV a mano. Sin esto, la fila nueva que se
    # agrega con modo "at" quedaria pegada a la ultima fila.
    ultima = ""
    with open(nombre_archivo, "rt", encoding="utf-8") as archivo:
        for linea in archivo:
            ultima = linea

    if ultima != "" and not ultima.endswith("\n"):
        with open(nombre_archivo, "at", encoding="utf-8") as archivo:
            archivo.write("\n")


def agregar_descartado(descartados, nombre_archivo, numero_linea, contenido, motivo):
    # Agrega una fila invalida a la lista de descartados.
    descartados.append({
        "archivo": nombre_archivo,
        "linea": numero_linea,
        "contenido": contenido,
        "motivo": motivo
    })


# Carga de registros (equipos, empleados y movimientos)
# Los archivos se recorren linea por linea, como vimos en la clase de archivos.

def cargar_equipos(config, descartados):
    # Lee equipos.csv y devuelve un diccionario con el codigo como clave:
    # {"NTB-0001": {"tipo": "Notebook", "estado": "Asignado", "legajo": "2350"}, ...}
    # Las filas invalidas no se cargan y se agregan a descartados.
    crear_si_no_existe(ARCHIVO_EQUIPOS, ENCABEZADO_EQUIPOS)
    equipos = {}

    with open(ARCHIVO_EQUIPOS, "rt", encoding="utf-8") as archivo:
        archivo.readline()  # el encabezado no se procesa
        numero_linea = 1    # la linea 1 es el encabezado
        for linea in archivo:
            numero_linea += 1
            linea = linea.rstrip("\n")
            if linea.strip() == "":
                continue

            campos = linea.split(SEPARADOR)
            if len(campos) != len(ENCABEZADO_EQUIPOS):
                agregar_descartado(descartados, ARCHIVO_EQUIPOS, numero_linea, linea, "cantidad de campos incorrecta")
                continue

            codigo = campos[0].strip()
            estado = campos[2].strip()
            legajo = campos[3].strip()

            try:
                # el tipo no se toma de la columna, sale del prefijo del codigo
                tipo = validaciones.validar_codigo(codigo, config["tipos"])
                validaciones.validar_en_lista(estado, config["estados"], "Estado")
                if legajo != "":
                    validaciones.validar_legajo(legajo, config["legajo_minimo"], config["legajo_maximo"])
                # solo un equipo Asignado puede tener legajo, y siempre tiene que tenerlo
                if estado == "Asignado" and legajo == "":
                    raise ValueError("equipo Asignado sin legajo")
                if estado != "Asignado" and legajo != "":
                    raise ValueError("equipo con legajo pero en estado " + estado)
                if codigo in equipos:
                    raise ValueError("codigo repetido")
            except ValueError as error:
                agregar_descartado(descartados, ARCHIVO_EQUIPOS, numero_linea, linea, str(error))
                continue

            equipos[codigo] = {"tipo": tipo, "estado": estado, "legajo": legajo}

    return equipos


def cargar_empleados(config, descartados):
    # Lee empleados.csv y devuelve un diccionario con el legajo como clave:
    # {"2350": {"nombre": "Carla Rodriguez", "departamento": "Sistemas"}, ...}
    crear_si_no_existe(ARCHIVO_EMPLEADOS, ENCABEZADO_EMPLEADOS)
    empleados = {}

    with open(ARCHIVO_EMPLEADOS, "rt", encoding="utf-8") as archivo:
        archivo.readline()
        numero_linea = 1
        for linea in archivo:
            numero_linea += 1
            linea = linea.rstrip("\n")
            if linea.strip() == "":
                continue

            campos = linea.split(SEPARADOR)
            if len(campos) != len(ENCABEZADO_EMPLEADOS):
                agregar_descartado(descartados, ARCHIVO_EMPLEADOS, numero_linea, linea, "cantidad de campos incorrecta")
                continue

            legajo = campos[0].strip()
            nombre = campos[1].strip()
            departamento = campos[2].strip()

            try:
                validaciones.validar_legajo(legajo, config["legajo_minimo"], config["legajo_maximo"])
                validaciones.validar_obligatorio(nombre, "nombre")
                validaciones.validar_en_lista(departamento, config["departamentos"], "Departamento")
                if legajo in empleados:
                    raise ValueError("legajo repetido")
            except ValueError as error:
                agregar_descartado(descartados, ARCHIVO_EMPLEADOS, numero_linea, linea, str(error))
                continue

            empleados[legajo] = {"nombre": nombre, "departamento": departamento}

    return empleados


def cargar_movimientos(config, descartados):
    # Lee movimientos.csv y devuelve una lista de diccionarios (un diccionario por movimiento),
    # en el mismo orden en que estan en el archivo (del mas viejo al mas nuevo).
    crear_si_no_existe(ARCHIVO_MOVIMIENTOS, ENCABEZADO_MOVIMIENTOS)
    movimientos = []

    with open(ARCHIVO_MOVIMIENTOS, "rt", encoding="utf-8") as archivo:
        archivo.readline()
        numero_linea = 1
        for linea in archivo:
            numero_linea += 1
            linea = linea.rstrip("\n")
            if linea.strip() == "":
                continue

            campos = linea.split(SEPARADOR)
            if len(campos) != len(ENCABEZADO_MOVIMIENTOS):
                agregar_descartado(descartados, ARCHIVO_MOVIMIENTOS, numero_linea, linea, "cantidad de campos incorrecta")
                continue

            # armo el diccionario usando el encabezado, asi cada campo queda con su nombre
            movimiento = {}
            for j in range(len(ENCABEZADO_MOVIMIENTOS)):
                movimiento[ENCABEZADO_MOVIMIENTOS[j]] = campos[j].strip()

            try:
                validaciones.validar_fecha(movimiento["fecha"])
                validaciones.validar_codigo(movimiento["codigo"], config["tipos"])
                validaciones.validar_en_lista(movimiento["tipo_movimiento"], validaciones.TIPOS_MOVIMIENTO, "Tipo de movimiento")
                validaciones.validar_en_lista(movimiento["estado_nuevo"], config["estados"], "Estado nuevo")
                if movimiento["legajo"] != "":
                    validaciones.validar_legajo(movimiento["legajo"], config["legajo_minimo"], config["legajo_maximo"])
            except ValueError as error:
                agregar_descartado(descartados, ARCHIVO_MOVIMIENTOS, numero_linea, linea, str(error))
                continue

            movimientos.append(movimiento)

    return movimientos


# Escritura

def guardar_equipos(equipos):
    # Reescribe equipos.csv completo con los datos del diccionario.
    with open(ARCHIVO_EQUIPOS, "wt", encoding="utf-8") as archivo:
        archivo.write(SEPARADOR.join(ENCABEZADO_EQUIPOS) + "\n")
        for codigo in equipos:
            equipo = equipos[codigo]
            fila = [codigo, equipo["tipo"], equipo["estado"], equipo["legajo"]]
            archivo.write(SEPARADOR.join(fila) + "\n")


def agregar_empleado(legajo, empleado):
    # Agrega una fila al final de empleados.csv (modo "at" = agregar texto).
    asegurar_salto_final(ARCHIVO_EMPLEADOS)
    with open(ARCHIVO_EMPLEADOS, "at", encoding="utf-8") as archivo:
        fila = [legajo, empleado["nombre"], empleado["departamento"]]
        archivo.write(SEPARADOR.join(fila) + "\n")


def agregar_movimiento(movimiento):
    # Agrega un movimiento al final de movimientos.csv, respetando el orden del encabezado.
    asegurar_salto_final(ARCHIVO_MOVIMIENTOS)
    with open(ARCHIVO_MOVIMIENTOS, "at", encoding="utf-8") as archivo:
        fila = [movimiento[campo] for campo in ENCABEZADO_MOVIMIENTOS]
        archivo.write(SEPARADOR.join(fila) + "\n")


def guardar_texto(nombre_archivo, lineas):
    # Escribe un archivo de texto (reporte.txt o alertas.txt). Si ya existia se sobrescribe.
    with open(nombre_archivo, "wt", encoding="utf-8") as archivo:
        for linea in lineas:
            archivo.write(linea + "\n")


def registrar_descartados(descartados):
    # Agrega las filas descartadas al final de descartados.txt. Este archivo nunca se sobrescribe.
    # Como las filas de empleados.csv y movimientos.csv no se borran, la misma fila invalida
    # aparece cada vez que se abre el programa. Para no anotarla dos veces, primero se arma
    # un conjunto con las filas que ya estan en descartados.txt.
    # Devuelve cuantas filas nuevas se agregaron.
    if len(descartados) == 0:
        return 0

    ya_registradas = set()
    try:
        with open(ARCHIVO_DESCARTADOS, "rt", encoding="utf-8") as archivo:
            for linea in archivo:
                partes = linea.split(" | ")
                if len(partes) >= 4:
                    # partes = [fecha, archivo, "linea N", contenido, motivo]
                    ya_registradas.add(partes[1] + "|" + partes[2] + "|" + partes[3])
    except FileNotFoundError:
        pass  # la primera vez el archivo todavia no existe

    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nuevas = 0
    with open(ARCHIVO_DESCARTADOS, "at", encoding="utf-8") as archivo:
        for fila in descartados:
            clave = fila["archivo"] + "|" + "linea " + str(fila["linea"]) + "|" + fila["contenido"]
            if clave in ya_registradas:
                continue
            archivo.write(ahora + " | " + fila["archivo"] + " | linea " + str(fila["linea"])
                          + " | " + fila["contenido"] + " | motivo: " + fila["motivo"] + "\n")
            ya_registradas.add(clave)
            nuevas += 1
    return nuevas
