"""Capa de Presentacion del emisor.

Codifica cada caracter del mensaje a su ASCII binario de 8 bits y ofrece la
operacion inversa. Ejemplo: 'A' -> '01000001'.
"""

BITS_POR_CARACTER = 8


def codificar_mensaje(texto: str) -> str:
    """Convierte el texto a una cadena de bits ASCII, 8 bits por caracter."""
    bits = []
    for caracter in texto:
        codigo = ord(caracter)
        if codigo > 0xFF:
            raise ValueError(
                f"Caracter fuera de rango (0-255): {caracter!r} ({codigo})"
            )
        bits.append(format(codigo, "08b"))
    return "".join(bits)


def decodificar_mensaje(bits: str) -> str:
    """Convierte una cadena de bits ASCII de vuelta a texto."""
    if len(bits) % BITS_POR_CARACTER != 0:
        raise ValueError("La cantidad de bits no es multiplo de 8")
    caracteres = []
    for i in range(0, len(bits), BITS_POR_CARACTER):
        octeto = bits[i:i + BITS_POR_CARACTER]
        caracteres.append(chr(int(octeto, 2)))
    return "".join(caracteres)
