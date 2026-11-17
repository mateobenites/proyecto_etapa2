# validaciones.py
# Validaciones de los datos que ingresa el usuario o que se leen de los archivos.
# Si un dato no es correcto, la funcion lanza un ValueError con el motivo
# y el formato esperado. El mensaje lo muestra main.py.

import re
from datetime import datetime

# Expresiones regulares (constantes)
PATRON_CODIGO = r"^[A-Z]{3}-\d{4}$"      # tres letras mayusculas, guion y cuatro numeros. Ej: NTB-0001
PATRON_LEGAJO = r"^[1-9]\d{3}$"          # cuatro digitos que no empiecen con cero. Ej: 1234
PATRON_FECHA = r"^\d{2}/\d{2}/\d{4}$"    # dd/mm/aaaa. Ej: 15/03/2026

TIPOS_MOVIMIENTO = ("alta", "asignacion", "devolucion", "cambio_estado")


def validar_codigo(codigo, tipos):
    """Valida el formato del codigo de equipo y que su prefijo exista en la configuracion.
    tipos es el diccionario de la config que asocia prefijo con nombre (ej: "NTB" -> "Notebook").
    Devuelve el tipo de equipo que corresponde al prefijo."""
    if codigo == "":
        raise ValueError("El codigo de equipo es obligatorio.")

    if not re.match(PATRON_CODIGO, codigo):
        raise ValueError("Codigo '" + codigo + "' invalido. El formato esperado es AAA-0000 (por ejemplo NTB-0001).")

    prefijo = codigo[:3]
    if prefijo not in tipos:
        raise ValueError("El prefijo " + prefijo + " no corresponde a ningun tipo de equipo. "
                         "Prefijos validos: " + ", ".join(tipos))

    return tipos[prefijo]


def validar_legajo(legajo, legajo_minimo, legajo_maximo):
    """Valida que el legajo tenga 4 digitos (sin empezar con 0) y que este dentro del rango."""
    if legajo == "":
        raise ValueError("El legajo es obligatorio.")

    if not re.match(PATRON_LEGAJO, legajo):
        raise ValueError("Legajo '" + legajo + "' invalido. Tiene que ser un numero de 4 digitos que no empiece con 0 (por ejemplo 1234).")

    numero = int(legajo)
    if numero < legajo_minimo or numero > legajo_maximo:
        raise ValueError("El legajo tiene que estar entre " + str(legajo_minimo) + " y " + str(legajo_maximo) + ".")

    return legajo


def validar_fecha(fecha):
    """Valida que la fecha tenga formato dd/mm/aaaa y que sea una fecha real."""
    if not re.match(PATRON_FECHA, fecha):
        raise ValueError("Fecha '" + fecha + "' invalida. El formato esperado es dd/mm/aaaa (por ejemplo 15/03/2026).")

    # La regex solo controla el formato. Para saber si la fecha existe
    # (por ej. 31/02/2026 no existe) usamos datetime: si no puede armar la fecha, tira ValueError.
    try:
        datetime.strptime(fecha, "%d/%m/%Y")
    except ValueError:
        raise ValueError("La fecha " + fecha + " tiene el formato correcto pero no existe.")

    return fecha


def validar_obligatorio(valor, campo):
    """Controla que un campo de texto no este vacio."""
    if valor == "":
        raise ValueError("El campo " + campo + " es obligatorio.")
    return valor


def validar_sin_separador(valor, campo):
    """Controla que un texto libre (nombre, motivo) no tenga punto y coma.
    El ; es el separador de los CSV: si se guardara, la fila quedaria con un campo de mas."""
    if ";" in valor:
        raise ValueError("El campo " + campo + " no puede tener ';' porque es el separador de los archivos.")
    return valor


def validar_en_lista(valor, opciones, campo):
    """Controla que el valor este entre las opciones permitidas.
    Se usa para estados, departamentos, tipos y tipos de movimiento."""
    if valor not in opciones:
        raise ValueError(campo + " '" + valor + "' invalido. Opciones validas: " + ", ".join(opciones))
    return valor


def validar_login(usuario, contrasena, usuarios):
    """Devuelve True si el usuario existe y la contrasena coincide."""
    if usuario in usuarios and usuarios[usuario] == contrasena:
        return True
    return False
