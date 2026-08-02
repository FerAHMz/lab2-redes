// Receptor: servidor bancario.
// Autores: Fernando Rueda (23748), Fernando Hernandez (23645)
//
// Entry point del receptor. Levanta la capa de Transmision, que queda
// escuchando tramas del cajero, y delega cada paquete a la capa de Aplicacion,
// la cual recorre la pila de abajo hacia arriba (Transmision -> Enlace ->
// Presentacion -> Aplicacion) y devuelve la respuesta del banco.
//
// Uso:
//     node receptor/receptor.js

const aplicacion = require("./capas/aplicacion");
const transmision = require("./capas/transmision");

transmision.recibirInformacion(aplicacion.mostrarMensaje);
