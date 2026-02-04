import { latestScene } from "../context/scene.js";

export function registerContextRoutes(app: any) {
  app.get("/context/latest", async () => {
    return latestScene.get();
  });
}
