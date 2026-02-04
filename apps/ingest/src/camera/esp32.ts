import fetch from "node-fetch";

export async function fetchFrame(ip: string) {
  const res = await fetch(`http://${ip}/capture`);
  return Buffer.from(await res.arrayBuffer());
}
