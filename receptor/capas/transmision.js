// Capa de Transmision del receptor.
// Autor: Fernando Hernandez (23645)
//
// Servidor TCP que escucha en el puerto elegido a la espera de recibir data.
// Usa JSON delimitado por salto de linea, el mismo protocolo que la capa de
// Transmision del emisor en Python, lo que permite la interoperabilidad.

const net = require("net");

const HOST_DEFECTO = "127.0.0.1";
const PUERTO_DEFECTO = 9100;

// Envia un objeto de respuesta al cajero como JSON terminado en salto de linea.
function enviarInformacion(socket, respuesta) {
  socket.write(JSON.stringify(respuesta) + "\n");
}

// Levanta el servidor y queda escuchando. Por cada paquete JSON recibido invoca
// `procesarPaquete(paquete)`, provisto por las capas superiores, y envia de
// vuelta el objeto de respuesta que este devuelva.
function recibirInformacion(procesarPaquete, host = HOST_DEFECTO, puerto = PUERTO_DEFECTO) {
  const server = net.createServer((socket) => {
    console.log("[banco] cajero conectado");
    let buffer = "";
    socket.on("data", (chunk) => {
      buffer += chunk.toString("utf8");
      let nl;
      while ((nl = buffer.indexOf("\n")) !== -1) {
        const linea = buffer.slice(0, nl);
        buffer = buffer.slice(nl + 1);
        if (!linea.trim()) continue;
        let respuesta;
        try {
          respuesta = procesarPaquete(JSON.parse(linea));
        } catch (e) {
          respuesta = { estado: "error", mensaje: `Paquete invalido: ${e.message}` };
        }
        enviarInformacion(socket, respuesta);
      }
    });
    socket.on("close", () => console.log("[banco] cajero desconectado"));
    socket.on("error", (e) => console.log(`[banco] error socket: ${e.message}`));
  });

  server.listen(puerto, host, () => {
    console.log(`[banco] escuchando en ${host}:${puerto}`);
  });
  return server;
}

module.exports = {
  HOST_DEFECTO,
  PUERTO_DEFECTO,
  enviarInformacion,
  recibirInformacion,
};
