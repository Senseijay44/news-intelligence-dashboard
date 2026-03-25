export async function fetchMapPoints() {
  const res = await fetch("http://localhost:8000/api/v1/articles/map", {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch map points");
  }

  return res.json();
}