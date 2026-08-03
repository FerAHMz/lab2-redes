"""Emisor: cajero automatico.

Recorre la pila de capas de arriba hacia abajo (Aplicacion -> Presentacion ->
Enlace -> Ruido -> Transmision) para enviar un mensaje al servidor bancario a
traves de un canal no confiable, y muestra la respuesta.

Uso:
    python3 emisor/emisor.py [puerto]
El receptor Node debe estar escuchando primero (en el mismo puerto):
    node receptor/receptor.js [puerto]
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from capas import aplicacion, enlace, presentacion, ruido, transmision


def enviar_mensaje(sock, texto, algoritmo, tasa_error):
    """Recorre la pila del emisor para un mensaje y muestra la respuesta."""
    # PRESENTACION: texto -> ASCII binario
    bits = presentacion.codificar_mensaje(texto)
    # ENLACE: datos -> trama con redundancia
    trama = enlace.calcular_integridad(bits, algoritmo)
    # RUIDO: canal no confiable
    trama_ruidosa, volteados = ruido.aplicar_ruido(trama, tasa_error)
    print(
        f"[emisor] datos={len(bits)}b trama={len(trama)}b "
        f"tasa={tasa_error} bits_volteados={volteados}"
    )
    # TRANSMISION: envio por socket
    paquete = {
        "algoritmo": algoritmo,
        "trama": trama_ruidosa,
        "n_datos": len(bits),
        "tasa_error": tasa_error,
    }
    transmision.enviar_informacion(sock, paquete)
    # Respuesta del banco
    respuesta = transmision.recibir_informacion(sock)
    aplicacion.mostrar_respuesta(respuesta)


def main():
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else transmision.PUERTO_DEFECTO
    sock = transmision.conectar(puerto=puerto)
    print(f"[emisor] conectado al banco en {transmision.HOST_DEFECTO}:{puerto}")
    try:
        while True:
            texto, algoritmo, tasa = aplicacion.solicitar_mensaje(
                enlace.algoritmos_disponibles()
            )
            enviar_mensaje(sock, texto, algoritmo, tasa)
            if input("\n¿Enviar otro mensaje? (s/n) [s]: ").strip().lower() == "n":
                break
    finally:
        sock.close()
        print("[emisor] conexion cerrada")


if __name__ == "__main__":
    main()
