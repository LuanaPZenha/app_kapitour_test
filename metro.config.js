const { getDefaultConfig } = require("expo/metro-config");
const http = require("http");

const config = getDefaultConfig(__dirname);

const PORTAS_API = [
  process.env.KAPITOUR_API_PORT,
  "8000",
  "8080",
].filter(Boolean);

function tentarPorta(req, res, corpo, indicePorta) {
  const porta = PORTAS_API[indicePorta];
  if (!porta) {
    res.statusCode = 502;
    res.setHeader("Content-Type", "application/json");
    res.end(
      JSON.stringify({
        detail:
          "API indisponivel. Suba o backend: docker compose up -d gateway",
      })
    );
    return;
  }

  const headers = { ...req.headers, host: `127.0.0.1:${porta}` };
  delete headers.connection;

  const proxyReq = http.request(
    {
      hostname: "127.0.0.1",
      port: porta,
      path: req.url,
      method: req.method,
      headers,
    },
    (proxyRes) => {
      res.writeHead(proxyRes.statusCode || 502, proxyRes.headers);
      proxyRes.pipe(res);
    }
  );

  proxyReq.on("error", () => {
    tentarPorta(req, res, corpo, indicePorta + 1);
  });

  if (corpo.length) proxyReq.write(corpo);
  proxyReq.end();
}

config.server = {
  ...config.server,
  enhanceMiddleware: (middleware) => {
    return (req, res, next) => {
      const caminho = req.url?.split("?")[0] || "";
      if (caminho !== "/api" && !caminho.startsWith("/api/")) {
        return middleware(req, res, next);
      }

      const chunks = [];
      req.on("data", (parte) => chunks.push(parte));
      req.on("end", () => {
        tentarPorta(req, res, Buffer.concat(chunks), 0);
      });
    };
  },
};

module.exports = config;
