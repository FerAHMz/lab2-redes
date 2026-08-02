"""Capa de Enlace del emisor.

Selecciona el algoritmo de integridad y calcula la trama (datos + redundancia).
La verificacion/correccion ocurre del lado del receptor; se incluye aqui tambien
para permitir pruebas locales sin sockets.
"""

from algoritmos import crc32, hamming

ALGORITMOS = {
    hamming.NOMBRE: hamming,
    crc32.NOMBRE: crc32,
}


def algoritmos_disponibles():
    return list(ALGORITMOS.keys())


def _obtener(algoritmo):
    if algoritmo not in ALGORITMOS:
        raise ValueError(
            f"Algoritmo no soportado: {algoritmo!r}. "
            f"Disponibles: {algoritmos_disponibles()}"
        )
    return ALGORITMOS[algoritmo]


def calcular_integridad(bits_datos: str, algoritmo: str) -> str:
    """Concatena la informacion de integridad al mensaje binario original."""
    return _obtener(algoritmo).calcular_integridad(bits_datos)


def verificar_integridad(trama: str, algoritmo: str, n_datos=None) -> dict:
    """Verifica (y corrige si aplica) la trama. Para pruebas locales del emisor."""
    modulo = _obtener(algoritmo)
    if hasattr(modulo, "verificar_y_corregir"):
        return modulo.verificar_y_corregir(trama)
    return modulo.verificar_integridad(trama, n_datos)
