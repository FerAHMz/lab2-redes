"""Capa de Aplicacion del emisor (cajero automatico).

Solicita al usuario el mensaje a enviar, el algoritmo de integridad y la tasa de
error, y muestra la respuesta del servidor bancario.
"""

MENSAJE_DEFECTO = "RETIRO 100.00 TARJETA 23748"
TASA_DEFECTO = 0.01


def solicitar_mensaje(algoritmos_disponibles):
    """Pide texto, algoritmo y tasa de error. Devuelve (texto, algoritmo, tasa)."""
    texto = input(f"Mensaje a enviar [{MENSAJE_DEFECTO}]: ").strip() or MENSAJE_DEFECTO

    opciones = "/".join(algoritmos_disponibles)
    predeterminado = algoritmos_disponibles[0]
    algoritmo = input(
        f"Algoritmo ({opciones}) [{predeterminado}]: "
    ).strip().lower() or predeterminado

    entrada = input(f"Tasa de error por bit (0-1) [{TASA_DEFECTO}]: ").strip()
    tasa = float(entrada) if entrada else TASA_DEFECTO
    return texto, algoritmo, tasa


def mostrar_respuesta(respuesta):
    """Muestra la respuesta del banco al usuario del cajero."""
    if respuesta is None:
        print(">> Sin respuesta del servidor.")
        return
    estado = respuesta.get("estado", "?")
    mensaje = respuesta.get("mensaje", "")
    print(f">> [banco/{estado}] {mensaje}")
