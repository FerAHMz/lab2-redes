"""Capa de Transmision del emisor.

Envia y recibe tramas por sockets TCP usando JSON delimitado por salto de linea,
lo que permite interoperar con el receptor escrito en Node.js.
"""

import json
import socket

HOST_DEFECTO = "127.0.0.1"
PUERTO_DEFECTO = 9100


def conectar(host=HOST_DEFECTO, puerto=PUERTO_DEFECTO):
    """Abre la conexion TCP con el servidor bancario (receptor)."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, puerto))
    return sock


def enviar_informacion(sock, paquete: dict):
    """Serializa el paquete a JSON y lo envia terminado en salto de linea."""
    linea = json.dumps(paquete) + "\n"
    sock.sendall(linea.encode("utf-8"))


def recibir_informacion(sock):
    """Lee una linea JSON de respuesta del receptor."""
    buffer = b""
    while not buffer.endswith(b"\n"):
        parte = sock.recv(4096)
        if not parte:
            break
        buffer += parte
    if not buffer:
        return None
    return json.loads(buffer.decode("utf-8").strip())
