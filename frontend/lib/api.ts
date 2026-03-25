const INTERNAL_API_BASE_URL = process.env.INTERNAL_API_BASE_URL;
const PUBLIC_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL;

export type DashboardFilters = {
  query?: string;
  topic?: string;
  source?: string;
  timeWindow?: string;
};

function getApiBaseUrl() {
  if (typeof window === "undefined") {
    return INTERNAL_API_BASE_URL || PUBLIC_API_BASE_URL || "http://backend:8000";
  }

  return PUBLIC_API_BASE_URL || "http://localhost:8000";
}

function buildQueryParams(filters?: DashboardFilters) {
  const params = new URLSearchParams();

  if (filters?.query) params.set("query", filters.query);
  if (filters?.topic && filters.topic !== "all") params.set("topic", filters.topic);
  if (filters?.source && filters.source !== "all") params.set("source", filters.source);
  if (filters?.timeWindow && filters.timeWindow !== "all") params.set("time_window", filters.timeWindow);

  const serialized = params.toString();
  return serialized ? `?${serialized}` : "";
}

export async function fetchMapPoints(filters?: DashboardFilters) {
  const baseUrl = getApiBaseUrl();
  const query = buildQueryParams(filters);

  const articleRes = await fetch(`${baseUrl}/api/v1/articles/map${query}`, {
    cache: "no-store",
  });

  if (!articleRes.ok) {
    throw new Error("Failed to fetch article map points");
  }

  const articlePoints = await articleRes.json();
  if (Array.isArray(articlePoints) && articlePoints.length > 0) {
    return articlePoints;
  }

  const eventRes = await fetch(`${baseUrl}/api/v1/events/map${query}`, {
    cache: "no-store",
  });

  if (!eventRes.ok) {
    throw new Error("Failed to fetch event map points");
  }

  return eventRes.json();
}

export async function fetchSources() {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/articles/sources`, {
    cache: "no-store",
  });

  if (!res.ok) {
    return [];
  }

  const sources = await res.json();
  return Array.isArray(sources) ? sources : [];
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


export async function runIngest() {
  const res = await fetch(`${getApiBaseUrl()}/api/v1/ingest/run`, {
    method: "POST",
  });

  if (!res.ok) {
    throw new Error("Failed to run ingest");
  }

  return res.json();
}
