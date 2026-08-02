// Capa de Aplicacion del receptor (servidor bancario).
// Autor: Fernando Hernandez (23645)
//
// Recorre la pila del receptor de abajo hacia arriba para cada paquete:
// Enlace (verificar/corregir) -> Presentacion (decodificar) -> mostrar el
// mensaje y armar la respuesta del banco para el cajero. Si se detectaron
// errores no corregibles, lo indica con un mensaje de error.

const enlace = require("./enlace");
const presentacion = require("./presentacion");

// Muestra el mensaje al receptor (o el error) y devuelve la respuesta que la
// capa de Transmision enviara de vuelta al cajero.
function mostrarMensaje(paquete) {
  const { algoritmo, trama, n_datos: nDatos } = paquete;

  // ENLACE: verificar integridad y corregir si el algoritmo lo permite.
  let r;
  try {
    r = enlace.verificarIntegridad(trama, algoritmo, nDatos);
  } catch (e) {
    console.log(`[banco] paquete rechazado: ${e.message}`);
    return { estado: "error", mensaje: e.message };
  }
  if (r.estado === "error") {
    const detalle = r.bloquesConError != null ? ` (${r.bloquesConError} bloques)` : "";
    console.log(`[banco] error no corregible${detalle}`);
    return { estado: "error", mensaje: "Trama con errores no corregibles" };
  }

  // PRESENTACION: ASCII binario -> texto.
  let texto;
  try {
    texto = presentacion.decodificarMensaje(r.bitsDatos);
  } catch (e) {
    console.log(`[banco] error al decodificar: ${e.message}`);
    return { estado: "error", mensaje: `Error al decodificar: ${e.message}` };
  }

  // APLICACION: mostrar el mensaje y responder al cajero.
  console.log(`[banco] ${r.estado}: "${texto}" (corregidos=${r.bloquesCorregidos ?? 0})`);
  return { estado: r.estado, mensaje: `Recibido: ${texto}` };
}

module.exports = {
  mostrarMensaje,
};
