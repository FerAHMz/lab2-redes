"""Harness de pruebas del laboratorio.

Autor: Fernando Hernandez (23645)

Corre la arquitectura completa end-to-end (emisor Python -> sockets -> receptor
Node) variando algoritmo, tamano de mensaje y probabilidad de error, y registra
cada envio en pruebas/resultados.csv para generar las graficas del reporte.

Clasificacion de cada envio:
  exito        el banco entrego el mensaje y coincide con el original
  detectado    el algoritmo detecto errores y no pudo (o no puede) corregirlos
  no_detectado el banco entrego un mensaje corrupto sin darse cuenta

Uso (lanza el receptor Node automaticamente en el puerto de pruebas):
    python3 pruebas/benchmark.py
"""

import csv
import os
import random
import string
import subprocess
import sys
import time

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "emisor"))

from capas import enlace, presentacion, ruido, transmision  # noqa: E402

PUERTO_PRUEBAS = 9350
SEMILLA = 23645  # reproducibilidad

ALGORITMOS = ("hamming", "crc32")
TAMANOS = (4, 16, 64, 256)  # caracteres por mensaje
TASAS = (0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1)  # errores por bit
REPETICIONES = 200  # envios por combinacion

RUTA_CSV = os.path.join(RAIZ, "pruebas", "resultados.csv")


def mensaje_aleatorio(rng, n_caracteres):
    alfabeto = string.ascii_uppercase + string.digits + " .,-"
    return "".join(rng.choice(alfabeto) for _ in range(n_caracteres))


def clasificar(respuesta, texto_original):
    if respuesta is None or respuesta.get("estado") == "error":
        return "detectado"
    if respuesta.get("mensaje") == f"Recibido: {texto_original}":
        return "exito"
    return "no_detectado"


def correr_pruebas(sock, escritor):
    rng = random.Random(SEMILLA)
    random.seed(SEMILLA)  # la capa de ruido usa el generador global
    total = len(ALGORITMOS) * len(TAMANOS) * len(TASAS) * REPETICIONES
    hechos = 0
    for algoritmo in ALGORITMOS:
        for n_caracteres in TAMANOS:
            for tasa in TASAS:
                for repeticion in range(REPETICIONES):
                    texto = mensaje_aleatorio(rng, n_caracteres)
                    bits = presentacion.codificar_mensaje(texto)
                    trama = enlace.calcular_integridad(bits, algoritmo)
                    trama_ruidosa, volteados = ruido.aplicar_ruido(trama, tasa)
                    transmision.enviar_informacion(sock, {
                        "algoritmo": algoritmo,
                        "trama": trama_ruidosa,
                        "n_datos": len(bits),
                    })
                    respuesta = transmision.recibir_informacion(sock)
                    escritor.writerow({
                        "algoritmo": algoritmo,
                        "n_caracteres": n_caracteres,
                        "tasa_error": tasa,
                        "repeticion": repeticion,
                        "bits_datos": len(bits),
                        "bits_trama": len(trama),
                        "bits_volteados": volteados,
                        "resultado": clasificar(respuesta, texto),
                    })
                    hechos += 1
                print(f"\r{hechos}/{total} envios", end="", flush=True)
    print()


def main():
    receptor = subprocess.Popen(
        ["node", os.path.join(RAIZ, "receptor", "receptor.js"), str(PUERTO_PRUEBAS)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)  # dar tiempo a que el servidor quede escuchando
    try:
        sock = transmision.conectar(puerto=PUERTO_PRUEBAS)
        with open(RUTA_CSV, "w", newline="") as archivo:
            escritor = csv.DictWriter(archivo, fieldnames=[
                "algoritmo", "n_caracteres", "tasa_error", "repeticion",
                "bits_datos", "bits_trama", "bits_volteados", "resultado",
            ])
            escritor.writeheader()
            inicio = time.time()
            correr_pruebas(sock, escritor)
        sock.close()
        print(f"Resultados en {RUTA_CSV} ({time.time() - inicio:.1f}s)")
    finally:
        receptor.terminate()


if __name__ == "__main__":
    main()
