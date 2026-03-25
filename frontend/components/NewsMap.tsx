"use client";

import dynamic from "next/dynamic";

const NewsMapClient = dynamic(() => import("./NewsMapClient"), {
  ssr: false,
  loading: () => <div style={{ padding: 16 }}>Loading map...</div>,
});

type MapPoint = {
  id: string | number;
  latitude: number;
  longitude: number;
  title: string;
  location_name?: string;
  article_count?: number;
  confidence_score?: number;
};

export default function NewsMap({ points }: { points: MapPoint[] }) {
  return <NewsMapClient points={points} />;
}
