// Algoritmo de Hamming (12,8) para correccion de errores.
// Autor: Fernando Rueda (23748)
//
// Mismo esquema que emisor/algoritmos/hamming.py: 4 bits de paridad en las
// posiciones 1, 2, 4 y 8 (1-indexado). Corrige 1 bit por bloque de 12 y senala
// como no corregible un sindrome fuera de rango.

const NOMBRE = "hamming";
const BITS_DATOS = 8;
const BITS_BLOQUE = 12;
const POSICIONES_PARIDAD = [1, 2, 4, 8];
const POSICIONES_DATOS = [3, 5, 6, 7, 9, 10, 11, 12];

function codificarBloque(datos8) {
  const cw = new Array(BITS_BLOQUE + 1).fill(0); // posiciones 1..12
  POSICIONES_DATOS.forEach((pos, i) => {
    cw[pos] = Number(datos8[i]);
  });
  for (const pp of POSICIONES_PARIDAD) {
    let paridad = 0;
    for (let j = 1; j <= BITS_BLOQUE; j++) {
      if (j !== pp && (j & pp)) paridad ^= cw[j];
    }
    cw[pp] = paridad;
  }
  return cw.slice(1).join("");
}

function decodificarBloque(bloque12) {
  const cw = [0, ...bloque12.split("").map(Number)]; // 1-indexado
  let sindrome = 0;
  for (const pp of POSICIONES_PARIDAD) {
    let paridad = 0;
    for (let j = 1; j <= BITS_BLOQUE; j++) {
      if (j & pp) paridad ^= cw[j];
    }
    if (paridad) sindrome += pp;
  }
  let estado = "ok";
  if (sindrome !== 0) {
    if (sindrome <= BITS_BLOQUE) {
      cw[sindrome] ^= 1; // corrige el bit senalado por el sindrome
      estado = "corregido";
    } else {
      estado = "error"; // sindrome fuera de rango: no corregible
    }
  }
  const datos8 = POSICIONES_DATOS.map((pos) => cw[pos]).join("");
  return { datos8, estado };
}

function calcularIntegridad(bitsDatos) {
  if (bitsDatos.length % BITS_DATOS !== 0) {
    throw new Error("La cantidad de bits de datos no es multiplo de 8");
  }
  let trama = "";
  for (let i = 0; i < bitsDatos.length; i += BITS_DATOS) {
    trama += codificarBloque(bitsDatos.slice(i, i + BITS_DATOS));
  }
  return trama;
}

function verificarYCorregir(trama) {
  if (trama.length % BITS_BLOQUE !== 0) {
    throw new Error("La trama no es multiplo de 12");
  }
  let datos = "";
  let corregidos = 0;
  let conError = 0;
  for (let i = 0; i < trama.length; i += BITS_BLOQUE) {
    const { datos8, estado } = decodificarBloque(trama.slice(i, i + BITS_BLOQUE));
    datos += datos8;
    if (estado === "corregido") corregidos++;
    else if (estado === "error") conError++;
  }
  let estado = "ok";
  if (conError) estado = "error";
  else if (corregidos) estado = "corregido";
  return {
    estado,
    bitsDatos: datos,
    bloquesCorregidos: corregidos,
    bloquesConError: conError,
  };
}

module.exports = {
  NOMBRE,
  BITS_DATOS,
  BITS_BLOQUE,
  calcularIntegridad,
  verificarYCorregir,
};
