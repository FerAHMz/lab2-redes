# Arquitectura de capas

El sistema modela el envío de un mensaje desde un cajero automático (emisor) hacia un
servidor bancario (receptor) a través de un canal no confiable. Cada lado implementa la
misma pila de capas; el emisor las recorre de arriba hacia abajo y el receptor de abajo
hacia arriba.

## Emisor (cajero, Python) — flujo descendente

1. **APLICACION** · `solicitar_mensaje`: solicita el texto a enviar, el algoritmo de
   integridad (hamming | crc32) y la tasa de error (errores por bit).
2. **PRESENTACION** · `codificar_mensaje`: convierte cada carácter a su ASCII binario de
   8 bits. Ej.: `A` → `01000001`.
3. **ENLACE** · `calcular_integridad`: aplica el algoritmo elegido sobre los bits y
   concatena la información de redundancia, produciendo la trama.
4. **RUIDO** · `aplicar_ruido`: recorre la trama y voltea cada bit con probabilidad `p`.
   La redundancia también está sujeta al ruido.
5. **TRANSMISION** · `enviar_informacion`: envía la trama por sockets al puerto elegido.

## Receptor (banco, Node.js) — flujo ascendente

1. **TRANSMISION** · `recibir_informacion`: escucha en el puerto y recibe la trama.
2. **ENLACE** · `verificar_integridad` / `corregir_mensaje`: recalcula la integridad,
   detecta errores y —si el algoritmo lo permite— los corrige.
3. **PRESENTACION** · `decodificar_mensaje`: si no hay error, convierte el ASCII binario
   de vuelta a texto; si hay error no corregible, lo señala a la capa de aplicación.
4. **APLICACION** · `mostrar_mensaje`: muestra el mensaje recibido o el error, y el banco
   responde al cajero.

## Formato de trama (protocolo entre capas de Transmisión)

Se transmite un objeto JSON terminado en salto de línea (`\n`), lo que permite a Python y
Node.js interoperar. Solo el campo `trama` sufre el ruido; los metadatos viajan intactos
porque describen cómo interpretar la trama.

```json
{
  "algoritmo": "hamming",
  "trama": "0100...",
  "n_datos": 40,
  "tasa_error": 0.01
}
```

- `algoritmo`: identificador del esquema usado en Enlace.
- `trama`: cadena de bits (datos + redundancia) tras aplicar el ruido.
- `n_datos`: cantidad de bits de datos originales (antes de la redundancia). Permite al
  receptor separar datos de redundancia.
- `tasa_error`: informativo, la probabilidad usada por la capa de Ruido.

La respuesta del banco al cajero viaja como JSON simple (no pasa por el canal ruidoso):

```json
{ "estado": "ok" | "corregido" | "error", "mensaje": "..." }
```

## Overhead

El overhead es la redundancia agregada respecto a los datos útiles.

- **Hamming (12,8):** por cada 8 bits de datos se envían 12 → 4 bits de redundancia por
  byte, overhead del 50 %. Corrige 1 bit por bloque de 12.
- **CRC-32:** 32 bits fijos de redundancia por mensaje, sin importar su longitud → el
  overhead relativo baja conforme el mensaje crece. Solo detecta, no corrige.
