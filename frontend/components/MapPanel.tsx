"use client";

import dynamic from "next/dynamic";

const NewsMap = dynamic(() => import("./NewsMap"), {
  ssr: false,
  loading: () => <div style={{ padding: 16 }}>Loading map...</div>,
});

export default function MapPanel({ points }: { points: any[] }) {
  return <NewsMap points={points} />;
}
