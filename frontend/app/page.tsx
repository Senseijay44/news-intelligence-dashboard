import MapPanel from "../components/MapPanel";
import Sidebar from "../components/Sidebar";
import { fetchMapPoints, fetchSources } from "../lib/api";

type SearchParams = {
  q?: string;
  topic?: string;
  source?: string;
  timeWindow?: string;
};

const TOPIC_OPTIONS = [
  { value: "all", label: "All topics" },
  { value: "conflict", label: "Conflict" },
  { value: "politics", label: "Politics" },
  { value: "economy", label: "Economy" },
  { value: "climate", label: "Climate" },
  { value: "technology", label: "Technology" },
];

const TIME_OPTIONS = [
  { value: "all", label: "Any time" },
  { value: "24h", label: "Last 24 hours" },
  { value: "7d", label: "Last 7 days" },
  { value: "30d", label: "Last 30 days" },
];

export default async function HomePage({ searchParams }: { searchParams?: Promise<SearchParams> }) {
  const params = (await searchParams) || {};

  const filters = {
    query: params.q || "",
    topic: params.topic || "all",
    source: params.source || "all",
    timeWindow: params.timeWindow || "all",
  };

  const [points, sourceOptions] = await Promise.all([
    fetchMapPoints(filters),
    fetchSources(),
  ]);

  return (
    <main className="dashboard-layout">
      <Sidebar
        points={points}
        filters={filters}
        topicOptions={TOPIC_OPTIONS}
        timeOptions={TIME_OPTIONS}
        sourceOptions={sourceOptions}
      />
      <div className="map-column">
        <MapPanel points={points} />
      </div>
    </main>
  );
}
