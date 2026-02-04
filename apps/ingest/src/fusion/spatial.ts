export function fuse(objects: any[], distance: number) {
  return objects.map((obj) => ({
    ...obj,
    distance_m: distance,
  }));
}
