// Receptor: servidor bancario (version minima).
// Autor: Fernando Rueda (23748)
//
// Version minima para demostrar el algoritmo Hamming end-to-end. Recibe la trama
// por sockets, verifica/corrige con Hamming, decodifica el ASCII binario y
// responde al cajero.

const net = require("net");
const hamming = require("./algoritmos/hamming");

const HOST = "127.0.0.1";
const PORT = 9100;

// PRESENTACION: decodifica ASCII binario (8 bits por caracter) a texto.
function decodificarMensaje(bits) {
  let texto = "";
  for (let i = 0; i < bits.length; i += 8) {
    texto += String.fromCharCode(parseInt(bits.slice(i, i + 8), 2));
  }
  return texto;
}

// ENLACE: dispatch minimo, por ahora solo Hamming.
function verificar(algoritmo, trama) {
  if (algoritmo !== hamming.NOMBRE) {
    throw new Error(`Algoritmo no soportado aun: ${algoritmo}`);
  }
  return hamming.verificarYCorregir(trama);
}

// APLICACION: procesa la trama y arma la respuesta del banco.
function procesarPaquete(paquete) {
  const { algoritmo, trama } = paquete;
  const r = verificar(algoritmo, trama);
  if (r.estado === "error") {
    console.log(`[banco] error no corregible (${r.bloquesConError} bloques)`);
    return { estado: "error", mensaje: "Trama con errores no corregibles" };
  }
  const texto = decodificarMensaje(r.bitsDatos);
  console.log(`[banco] ${r.estado}: "${texto}" (corregidos=${r.bloquesCorregidos})`);
  return { estado: r.estado, mensaje: `Recibido: ${texto}` };
}

// TRANSMISION: servidor TCP con JSON delimitado por salto de linea.
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
      socket.write(JSON.stringify(respuesta) + "\n");
    }
  });
  socket.on("close", () => console.log("[banco] cajero desconectado"));
  socket.on("error", (e) => console.log(`[banco] error socket: ${e.message}`));
});

server.listen(PORT, HOST, () => {
  console.log(`[banco] escuchando en ${HOST}:${PORT}`);
});
