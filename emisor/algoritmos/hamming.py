"""Algoritmo de Hamming (12,8) para correccion de errores.

Autor: Fernando Rueda (23748)

Cada byte de datos (8 bits) se codifica en un bloque de 12 bits con 4 bits de
paridad en las posiciones 1, 2, 4 y 8 (indexadas desde 1). Cumple la condicion
(m + r + 1) <= 2^r con m=8, r=4. El codigo corrige un error de 1 bit por bloque
y senala como no corregible un sindrome fuera de rango (indicio de error de
multiples bits).
"""

NOMBRE = "hamming"
BITS_DATOS = 8
BITS_BLOQUE = 12
POSICIONES_PARIDAD = (1, 2, 4, 8)
POSICIONES_DATOS = (3, 5, 6, 7, 9, 10, 11, 12)


def _codificar_bloque(datos8: str) -> str:
    """Codifica 8 bits de datos en un bloque Hamming de 12 bits (paridad par)."""
    cw = [0] * (BITS_BLOQUE + 1)  # posiciones 1..12
    for pos, bit in zip(POSICIONES_DATOS, datos8):
        cw[pos] = int(bit)
    for pp in POSICIONES_PARIDAD:
        paridad = 0
        for j in range(1, BITS_BLOQUE + 1):
            if j != pp and (j & pp):
                paridad ^= cw[j]
        cw[pp] = paridad
    return "".join(str(cw[i]) for i in range(1, BITS_BLOQUE + 1))


def _decodificar_bloque(bloque12: str):
    """Devuelve (datos8, estado) corrigiendo hasta 1 bit por bloque."""
    cw = [0] + [int(b) for b in bloque12]  # 1-indexado
    sindrome = 0
    for pp in POSICIONES_PARIDAD:
        paridad = 0
        for j in range(1, BITS_BLOQUE + 1):
            if j & pp:
                paridad ^= cw[j]
        if paridad:
            sindrome += pp
    estado = "ok"
    if sindrome != 0:
        if sindrome <= BITS_BLOQUE:
            cw[sindrome] ^= 1  # corrige el bit senalado por el sindrome
            estado = "corregido"
        else:
            estado = "error"  # sindrome fuera de rango: no corregible
    datos8 = "".join(str(cw[pos]) for pos in POSICIONES_DATOS)
    return datos8, estado


def calcular_integridad(bits_datos: str) -> str:
    """Codifica toda la cadena ASCII en bloques Hamming de 12 bits."""
    if len(bits_datos) % BITS_DATOS != 0:
        raise ValueError("La cantidad de bits de datos no es multiplo de 8")
    trama = []
    for i in range(0, len(bits_datos), BITS_DATOS):
        trama.append(_codificar_bloque(bits_datos[i:i + BITS_DATOS]))
    return "".join(trama)


def verificar_y_corregir(trama: str) -> dict:
    """Verifica la trama y corrige errores de 1 bit por bloque.

    Devuelve un dict con:
      estado: 'ok' | 'corregido' | 'error'
      bits_datos: cadena de bits de datos recuperada (mejor esfuerzo)
      bloques_corregidos, bloques_con_error: conteos por bloque
    """
    if len(trama) % BITS_BLOQUE != 0:
        raise ValueError("La trama no es multiplo de 12")
    datos = []
    corregidos = 0
    con_error = 0
    for i in range(0, len(trama), BITS_BLOQUE):
        datos8, estado = _decodificar_bloque(trama[i:i + BITS_BLOQUE])
        datos.append(datos8)
        if estado == "corregido":
            corregidos += 1
        elif estado == "error":
            con_error += 1
    if con_error:
        estado = "error"
    elif corregidos:
        estado = "corregido"
    else:
        estado = "ok"
    return {
        "estado": estado,
        "bits_datos": "".join(datos),
        "bloques_corregidos": corregidos,
        "bloques_con_error": con_error,
    }
