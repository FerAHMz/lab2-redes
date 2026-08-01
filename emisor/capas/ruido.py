"""Capa de Ruido (lado emisor).

No es una capa real del modelo, pero simula el canal no confiable: recorre la
trama y voltea cada bit con cierta probabilidad (errores por bit). La informacion
de redundancia tambien esta sujeta al ruido.
"""

import random


def aplicar_ruido(trama: str, tasa_error: float):
    """Voltea cada bit con probabilidad tasa_error.

    Devuelve (trama_con_ruido, bits_volteados).
    """
    if not 0.0 <= tasa_error <= 1.0:
        raise ValueError("La tasa de error debe estar entre 0 y 1")
    bits = list(trama)
    volteados = 0
    for i, bit in enumerate(bits):
        if random.random() < tasa_error:
            bits[i] = "1" if bit == "0" else "0"
            volteados += 1
    return "".join(bits), volteados
