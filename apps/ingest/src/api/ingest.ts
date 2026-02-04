import { spawn } from "child_process";
import { latestScene } from "../context/scene.js";

export function registerIngestRoutes(app: any) {
  // ESP32 sends image URL
  app.post("/frame", async (req: any) => {
    const { imageUrl, lidarDistance } = req.body;

    return new Promise((resolve) => {
      const py = spawn("python3", [
        "python/vision_worker.py",
        imageUrl,
        String(lidarDistance || 2.0),
      ]);

      py.stdout.on("data", (data) => {
        const scene = JSON.parse(data.toString());
        latestScene.set(scene);
        resolve({ status: "ok" });
      });
    });
  });

  // LiDAR-only updates
  app.post("/lidar", async (req: any) => {
    const { distance } = req.body;
    latestScene.updateDistance(distance);
    return { status: "lidar updated" };
  });
}
