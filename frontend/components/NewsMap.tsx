"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const NewsMapLeaflet = dynamic(() => import("./NewsMapClient"), {
  ssr: false,
  loading: () => <div className="map-loading">Loading map intelligence...</div>,
});

type MapPoint = {
  id: string | number;
  latitude: number;
  longitude: number;
  title: string;
  location_name?: string;
  article_count?: number;
  source_count?: number;
  confidence_score?: number;
};

export default function NewsMap({ points }: { points: MapPoint[] }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div className="map-loading">Loading map intelligence...</div>;
  }

  return <NewsMapLeaflet points={points} />;
}
