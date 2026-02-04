class SceneStore {
  private scene: any = null;

  set(scene: any) {
    this.scene = scene;
  }

  get() {
    return this.scene ?? { status: "no data" };
  }

  updateDistance(distance: number) {
    if (!this.scene) return;
    this.scene.people?.forEach((p: any) => {
      p.distance_m = distance;
    });
    this.scene.objects?.forEach((o: any) => {
      o.distance_m = distance;
    });
  }
}

export const latestScene = new SceneStore();
