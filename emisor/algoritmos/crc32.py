"""Algoritmo CRC-32 para deteccion de errores.

Autor: Fernando Hernandez (23645)

Usa el polinomio estandar de 32 bits de CRC-32 (IEEE 802.3):
0x04C11DB7. El registro inicia en 0xFFFFFFFF y el residuo final se
complementa, procesando la trama bit a bit (MSB primero). El CRC de 32 bits se
concatena al final del mensaje binario original.

La trama debe tener n > 32 bits; si el mensaje es menor se agregan 0s de
padding al final antes de calcular el CRC. Para retirar el padding en el
receptor se utiliza n_datos (longitud original del mensaje).
"""

NOMBRE = "crc32"
POLINOMIO = 0x04C11DB7
BITS_CRC = 32
MASCARA = 0xFFFFFFFF


def _crc(bits: str) -> int:
    """Calcula el CRC-32 de una cadena de bits, bit a bit (MSB primero)."""
    registro = MASCARA  # valor inicial: todos 1s
    for bit in bits:
        msb = (registro >> (BITS_CRC - 1)) & 1
        registro = (registro << 1) & MASCARA
        if msb ^ int(bit):
            registro ^= POLINOMIO
    return registro ^ MASCARA  # complemento final


def _con_padding(bits_datos: str) -> str:
    """Agrega 0s al final si el mensaje tiene 32 bits o menos (n > 32)."""
    if len(bits_datos) > BITS_CRC:
        return bits_datos
    return bits_datos + "0" * (BITS_CRC + 1 - len(bits_datos))


def calcular_integridad(bits_datos: str) -> str:
    """Concatena el CRC-32 (32 bits) al final del mensaje binario."""
    if not bits_datos:
        raise ValueError("El mensaje binario esta vacio")
    datos = _con_padding(bits_datos)
    return datos + format(_crc(datos), f"0{BITS_CRC}b")


def verificar_integridad(trama: str, n_datos=None) -> dict:
    """Recalcula el CRC del lado del receptor y lo compara con el recibido.

    Devuelve un dict con:
      estado: 'ok' | 'error' (CRC-32 detecta, no corrige)
      bits_datos: mensaje original sin padding ni CRC (si estado es 'ok')
    `n_datos` es la longitud original del mensaje, para retirar el padding.
    """
    if len(trama) <= BITS_CRC:
        raise ValueError("La trama debe tener mas de 32 bits")
    datos, crc_recibido = trama[:-BITS_CRC], trama[-BITS_CRC:]
    crc_calculado = format(_crc(datos), f"0{BITS_CRC}b")
    if crc_calculado != crc_recibido:
        return {"estado": "error", "bits_datos": ""}
    if n_datos is not None:
        datos = datos[:n_datos]
    return {"estado": "ok", "bits_datos": datos}
