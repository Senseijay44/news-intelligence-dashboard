const INTERNAL_API_BASE_URL = process.env.INTERNAL_API_BASE_URL;
const PUBLIC_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

function getApiBaseUrl() {
  if (typeof window === "undefined") {
    return INTERNAL_API_BASE_URL || PUBLIC_API_BASE_URL || "http://backend:8000";
  }

  return PUBLIC_API_BASE_URL || "http://localhost:8000";
}

export async function fetchMapPoints() {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/events/map`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch event map points");
  }

  return res.json();
}

export async function fetchRawArticleMapPoints() {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/articles/map`, {
    cache: "no-store",
  });

  if (!res.ok) {
    throw new Error("Failed to fetch raw article map points");
  }

  return res.json();
}
