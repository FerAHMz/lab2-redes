// Capa de Enlace del receptor.
// Autor: Fernando Hernandez (23645)
//
// Selecciona el algoritmo de integridad segun el paquete recibido y verifica
// (y corrige, si el algoritmo lo permite) la trama. Espejo del dispatch de
// emisor/capas/enlace.py.

const hamming = require("../algoritmos/hamming");

const ALGORITMOS = {
  [hamming.NOMBRE]: hamming,
};

function algoritmosDisponibles() {
  return Object.keys(ALGORITMOS);
}

function obtener(algoritmo) {
  if (!(algoritmo in ALGORITMOS)) {
    throw new Error(
      `Algoritmo no soportado: ${algoritmo}. Disponibles: ${algoritmosDisponibles()}`
    );
  }
  return ALGORITMOS[algoritmo];
}

// Verifica la integridad de la trama con el algoritmo indicado. Devuelve un
// objeto con { estado: 'ok' | 'corregido' | 'error', bitsDatos, ... } segun
// reporte cada algoritmo. `nDatos` permite a los algoritmos de deteccion
// separar los bits de datos de la redundancia.
function verificarIntegridad(trama, algoritmo, nDatos) {
  const modulo = obtener(algoritmo);
  if (typeof modulo.verificarYCorregir === "function") {
    return modulo.verificarYCorregir(trama);
  }
  return modulo.verificarIntegridad(trama, nDatos);
}

module.exports = {
  ALGORITMOS,
  algoritmosDisponibles,
  verificarIntegridad,
};
