// Capa de Presentacion del receptor.
// Autor: Fernando Hernandez (23645)
//
// Decodifica el ASCII binario (8 bits por caracter) de vuelta a texto, la
// operacion inversa a la capa de Presentacion del emisor. Si la cadena de bits
// es invalida lanza un error para que la capa de aplicacion lo senale.

const BITS_POR_CARACTER = 8;

// Convierte una cadena de bits ASCII de vuelta a texto. Ej.: '01000001' -> 'A'.
function decodificarMensaje(bits) {
  if (bits.length % BITS_POR_CARACTER !== 0) {
    throw new Error("La cantidad de bits no es multiplo de 8");
  }
  let texto = "";
  for (let i = 0; i < bits.length; i += BITS_POR_CARACTER) {
    texto += String.fromCharCode(parseInt(bits.slice(i, i + BITS_POR_CARACTER), 2));
  }
  return texto;
}

// Operacion inversa, incluida por simetria con el emisor (util en pruebas).
function codificarMensaje(texto) {
  let bits = "";
  for (const caracter of texto) {
    const codigo = caracter.charCodeAt(0);
    if (codigo > 0xff) {
      throw new Error(`Caracter fuera de rango (0-255): ${caracter} (${codigo})`);
    }
    bits += codigo.toString(2).padStart(BITS_POR_CARACTER, "0");
  }
  return bits;
}

module.exports = {
  BITS_POR_CARACTER,
  decodificarMensaje,
  codificarMensaje,
};
