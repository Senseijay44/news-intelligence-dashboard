"use client";

type FilterOption = { value: string; label: string };

type SidebarProps = {
  points: any[];
  filters: {
    query?: string;
    topic?: string;
    source?: string;
    timeWindow?: string;
  };
  topicOptions: FilterOption[];
  timeOptions: FilterOption[];
  sourceOptions: string[];
  onRefresh: () => Promise<void>;
  isRefreshing: boolean;
  refreshError: string | null;
  lastUpdatedAt: string | null;
};

function toConfidenceBadge(confidence: number | undefined) {
  const value = Math.round((confidence ?? 0) * 100);
  if (value >= 75) return "high";
  if (value >= 50) return "medium";
  return "low";
}

function formatTimestamp(value: string | null) {
  if (!value) return "Not refreshed yet";

  return new Intl.DateTimeFormat(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

export default function Sidebar({
  points,
  filters,
  topicOptions,
  timeOptions,
  sourceOptions,
  onRefresh,
  isRefreshing,
  refreshError,
  lastUpdatedAt,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <p className="eyebrow">Global Monitor</p>
        <h1>News Intelligence</h1>
        <p className="subtitle">Map-first situational awareness with geolocated stories and event confidence signals.</p>
      </div>

      <form className="filters" method="get">
        <label>
          Search
          <input name="q" defaultValue={filters.query || ""} placeholder="Keyword, region, incident..." />
        </label>

        <div className="filter-grid">
          <label>
            Topic
            <select name="topic" defaultValue={filters.topic || "all"}>
              {topicOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            Time
            <select name="timeWindow" defaultValue={filters.timeWindow || "all"}>
              {timeOptions.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
        </div>

        <label>
          Source
          <select name="source" defaultValue={filters.source || "all"}>
            <option value="all">All sources</option>
            {sourceOptions.map((source) => (
              <option key={source} value={source}>
                {source}
              </option>
            ))}
          </select>
        </label>

        <div className="filter-actions">
          <button type="submit">Apply filters</button>
          <a href="/">Reset</a>
        </div>
      </form>

      <div className="refresh-panel">
        <button type="button" className="refresh-button" onClick={onRefresh} disabled={isRefreshing}>
          {isRefreshing ? "Refreshing…" : "Refresh News"}
        </button>
        <p className="refresh-meta">Last updated: {formatTimestamp(lastUpdatedAt)}</p>
        {refreshError ? <p className="refresh-error">{refreshError}</p> : null}
      </div>

      <div className="results-meta">{points.length} mapped stories</div>

      <div className="event-list">
        {points.length === 0 ? (
          <div className="empty-state">
            <p>No stories match your filters.</p>
            <span>Try broadening keywords, time window, or source.</span>
          </div>
        ) : (
          points.map((item) => (
            <article key={item.id} className="event-card" tabIndex={0}>
              <div className="card-title">{item.title}</div>
              <div className="card-location">{item.location_name || "Unknown location"}</div>
              <div className="badge-row">
                <span className="badge">{item.article_count ?? 1} articles</span>
                {item.source_count ? <span className="badge">{item.source_count} sources</span> : null}
                <span className={`badge confidence ${toConfidenceBadge(item.confidence_score)}`}>
                  {Math.round((item.confidence_score ?? 0) * 100)}% confidence
                </span>
              </div>
            </article>
          ))
        )}
      </div>
    </aside>
  );
}
