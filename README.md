# Laboratorio 2 — Esquemas de detección y corrección de errores

CC3067 Redes · Universidad del Valle de Guatemala

Aplicación de intercambio de mensajes entre un **cajero automático** (emisor) y un
**servidor bancario** (receptor) construida sobre una arquitectura de capas, expuesta a
un canal no confiable. Se implementan algoritmos de detección y corrección de errores en
la capa de Enlace.

## Integrantes

| Nombre | Carné | Rol principal |
|---|---|---|
| Fernando Rueda Rodas | 23748 | Emisor (Python) + algoritmo Hamming |
| Fernando Hernandez | 23645 | Receptor (Node.js) + algoritmo CRC-32 |

## Arquitectura

El emisor y el receptor están escritos en **lenguajes distintos**, según lo exige el
laboratorio (al menos uno diferente de Python):

- **Emisor — cajero automático:** Python (`emisor/`). Punto de partida: `client.py` del Lab1.
- **Receptor — servidor bancario:** Node.js (`receptor/`). Punto de partida: `server.py` del Lab1.

Ambos lados implementan la misma pila de 5 capas. El detalle de cada capa y del formato de
trama está en [docs/arquitectura.md](docs/arquitectura.md).

```
APLICACION     solicitar_mensaje / mostrar_mensaje
PRESENTACION   codificar_mensaje (ASCII binario) / decodificar_mensaje
ENLACE         calcular_integridad / verificar_integridad / corregir_mensaje
RUIDO          aplicar_ruido (flip de bits por probabilidad)   [solo emisor]
TRANSMISION    enviar_informacion / recibir_informacion (sockets)
```

## Algoritmos

| Algoritmo | Tipo | Dueño | Estado |
|---|---|---|---|
| Hamming (12,8) | Corrección (1 bit por bloque) | Fernando Rueda | Implementado |
| CRC-32 | Detección | Fernando Hernandez | Pendiente |

## Estructura del repositorio

```
lab2-redes/
├── emisor/                 Cajero automático (Python)
│   ├── emisor.py           Entry point
│   ├── capas/              aplicacion, presentacion, enlace, ruido, transmision
│   └── algoritmos/         hamming.py, crc32.py
├── receptor/               Servidor bancario (Node.js)
│   ├── receptor.js         Entry point
│   ├── capas/              aplicacion, presentacion, enlace, transmision
│   └── algoritmos/         hamming.js, crc32.js
├── pruebas/                Harness de experimentos y gráficas
└── docs/                   Arquitectura y reporte
```

## Cómo ejecutar

Requisitos: Python 3.10+ y Node.js 18+.

En una terminal, levantar el receptor (servidor banco):

```bash
node receptor/receptor.js
```

En otra terminal, correr el emisor (cajero):

```bash
python3 emisor/emisor.py
```

El cajero solicita el mensaje a enviar, el algoritmo de integridad y la tasa de error
(errores por bit). La trama se transmite por sockets; el banco verifica integridad,
corrige si el algoritmo lo permite, decodifica el mensaje y responde.
