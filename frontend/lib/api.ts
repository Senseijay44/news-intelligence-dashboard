const INTERNAL_API_BASE_URL = process.env.INTERNAL_API_BASE_URL;
const PUBLIC_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

function getApiBaseUrl() {
  if (typeof window === "undefined") {
    return INTERNAL_API_BASE_URL || PUBLIC_API_BASE_URL || "http://backend:8000";
  }

  return PUBLIC_API_BASE_URL || "http://localhost:8000";
}

export async function fetchMapPoints() {
  const baseUrl = getApiBaseUrl();

  const articleRes = await fetch(`${baseUrl}/api/v1/articles/map`, {
    cache: "no-store",
  });

  if (!articleRes.ok) {
    throw new Error("Failed to fetch article map points");
  }

  const articlePoints = await articleRes.json();
  if (Array.isArray(articlePoints) && articlePoints.length > 0) {
    return articlePoints;
  }

  const eventRes = await fetch(`${baseUrl}/api/v1/events/map`, {
    cache: "no-store",
  });

  if (!eventRes.ok) {
    throw new Error("Failed to fetch event map points");
  }

  return eventRes.json();
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
