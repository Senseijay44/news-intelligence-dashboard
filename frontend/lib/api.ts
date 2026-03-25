const API_BASE_URL = process.env.API_BASE_URL || "http://localhost:8000";

export async function fetchMapPoints() {
  const res = await fetch(`${API_BASE_URL}/api/v1/articles/map`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch map points");
  }

  return res.json();
}
