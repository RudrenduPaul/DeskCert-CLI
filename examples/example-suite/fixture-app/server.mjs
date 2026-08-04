#!/usr/bin/env node
// Zero-dependency static server for the DeskCert fixture app. Binds to
// localhost only -- this is a local demo fixture, never expose it publicly.
import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const PORT = Number(process.env.DESKCERT_FIXTURE_PORT ?? 4310);

const server = createServer(async (req, res) => {
  try {
    const html = await readFile(path.join(__dirname, "index.html"), "utf-8");
    res.writeHead(200, { "content-type": "text/html; charset=utf-8" });
    res.end(html);
  } catch (err) {
    res.writeHead(500, { "content-type": "text/plain" });
    res.end("fixture app failed to load");
  }
});

server.listen(PORT, "127.0.0.1", () => {
  console.log(`DeskCert fixture app listening on http://127.0.0.1:${PORT}`);
});
