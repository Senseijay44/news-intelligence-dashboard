"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

const NewsMapLeaflet = dynamic(() => import("./NewsMapClient"), {
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
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return <div style={{ padding: 16 }}>Loading map...</div>;
  }

  return <NewsMapLeaflet points={points} />;
}
