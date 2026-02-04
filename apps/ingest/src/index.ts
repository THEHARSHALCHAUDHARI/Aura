import Fastify from "fastify";
import { registerIngestRoutes } from "./api/ingest.js";
import { registerContextRoutes } from "./api/context.js";

export const app = Fastify({ logger: true });

registerIngestRoutes(app);
registerContextRoutes(app);

app.listen({ port: 4000, host: "0.0.0.0" }, () => {
  console.log("Aura ingest running on port 4000");
});

app.get("/", async () => {
  return { status: "Aura ingest running" };
});