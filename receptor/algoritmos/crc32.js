// Algoritmo CRC-32 para deteccion de errores.
// Autor: Fernando Hernandez (23645)
//
// Mismo esquema que emisor/algoritmos/crc32.py: polinomio estandar de CRC-32
// (IEEE 802.3) 0x04C11DB7, registro inicial 0xFFFFFFFF y complemento final,
// procesando la trama bit a bit (MSB primero). El CRC de 32 bits viene
// concatenado al final del mensaje binario; n_datos permite retirar el padding
// agregado a mensajes de 32 bits o menos.

const NOMBRE = "crc32";
const POLINOMIO = 0x04c11db7;
const BITS_CRC = 32;

function crc(bits) {
  let registro = 0xffffffff;
  for (const bit of bits) {
    const msb = (registro >>> (BITS_CRC - 1)) & 1;
    registro = (registro << 1) >>> 0; // fuerza aritmetica sin signo de 32 bits
    if (msb ^ Number(bit)) registro = (registro ^ POLINOMIO) >>> 0;
  }
  return (registro ^ 0xffffffff) >>> 0;
}

function conPadding(bitsDatos) {
  if (bitsDatos.length > BITS_CRC) return bitsDatos;
  return bitsDatos.padEnd(BITS_CRC + 1, "0");
}

function calcularIntegridad(bitsDatos) {
  if (!bitsDatos) throw new Error("El mensaje binario esta vacio");
  const datos = conPadding(bitsDatos);
  return datos + crc(datos).toString(2).padStart(BITS_CRC, "0");
}

// Recalcula el CRC y lo compara con el recibido. CRC-32 detecta, no corrige:
// estado es 'ok' o 'error'. `nDatos` es la longitud original del mensaje.
function verificarIntegridad(trama, nDatos) {
  if (trama.length <= BITS_CRC) {
    throw new Error("La trama debe tener mas de 32 bits");
  }
  const datos = trama.slice(0, -BITS_CRC);
  const crcRecibido = trama.slice(-BITS_CRC);
  const crcCalculado = crc(datos).toString(2).padStart(BITS_CRC, "0");
  if (crcCalculado !== crcRecibido) {
    return { estado: "error", bitsDatos: "" };
  }
  return {
    estado: "ok",
    bitsDatos: nDatos != null ? datos.slice(0, nDatos) : datos,
  };
}

module.exports = {
  NOMBRE,
  BITS_CRC,
  calcularIntegridad,
  verificarIntegridad,
};
