"use client";

import { useMemo, useState } from "react";

import MapPanel from "./MapPanel";
import Sidebar from "./Sidebar";
import { fetchMapPoints, fetchSources, runIngest } from "../lib/api";

type FilterOption = { value: string; label: string };

type DashboardShellProps = {
  initialPoints: any[];
  initialSourceOptions: string[];
  filters: {
    query?: string;
    topic?: string;
    source?: string;
    timeWindow?: string;
  };
  topicOptions: FilterOption[];
  timeOptions: FilterOption[];
};

export default function DashboardShell({
  initialPoints,
  initialSourceOptions,
  filters,
  topicOptions,
  timeOptions,
}: DashboardShellProps) {
  const [points, setPoints] = useState(initialPoints);
  const [sourceOptions, setSourceOptions] = useState(initialSourceOptions);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshError, setRefreshError] = useState<string | null>(null);
  const [lastUpdatedAt, setLastUpdatedAt] = useState<string | null>(null);

  const filterQuery = useMemo(
    () => ({
      query: filters.query || "",
      topic: filters.topic || "all",
      source: filters.source || "all",
      timeWindow: filters.timeWindow || "all",
    }),
    [filters],
  );

  const handleRefresh = async () => {
    setIsRefreshing(true);
    setRefreshError(null);

    try {
      await runIngest();
      const [nextPoints, nextSources] = await Promise.all([
        fetchMapPoints(filterQuery),
        fetchSources(),
      ]);
      setPoints(nextPoints);
      setSourceOptions(nextSources);
      setLastUpdatedAt(new Date().toISOString());
    } catch (error) {
      const message = error instanceof Error ? error.message : "Refresh failed";
      setRefreshError(message);
    } finally {
      setIsRefreshing(false);
    }
  };

  return (
    <main className="dashboard-layout">
      <Sidebar
        points={points}
        filters={filters}
        topicOptions={topicOptions}
        timeOptions={timeOptions}
        sourceOptions={sourceOptions}
        onRefresh={handleRefresh}
        isRefreshing={isRefreshing}
        refreshError={refreshError}
        lastUpdatedAt={lastUpdatedAt}
      />
      <div className="map-column">
        <MapPanel points={points} />
      </div>
    </main>
  );
}
