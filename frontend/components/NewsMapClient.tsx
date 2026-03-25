"use client";

import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

type MapPoint = {
  id: string | number;
  latitude: number;
  longitude: number;
  title: string;
  location_name?: string;
  article_count?: number;
  confidence_score?: number;
};

const defaultIcon = L.icon({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

export default function NewsMapClient({ points }: { points: MapPoint[] }) {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) {
      return;
    }

    const map = L.map(mapRef.current).setView([20, 0], 2);
    mapInstanceRef.current = map;

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);

    markersLayerRef.current = L.layerGroup().addTo(map);

    return () => {
      markersLayerRef.current?.clearLayers();
      markersLayerRef.current = null;
      mapInstanceRef.current?.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapInstanceRef.current;
    const markerLayer = markersLayerRef.current;

    if (!map || !markerLayer) {
      return;
    }

    markerLayer.clearLayers();

    points.forEach((point) => {
      const marker = L.marker([point.latitude, point.longitude], { icon: defaultIcon });

      marker.bindPopup(
        `<strong>${point.title}</strong><br/>${point.location_name || "Unknown location"}<br/>Related articles: ${point.article_count ?? 1}<br/>Confidence: ${Math.round((point.confidence_score ?? 0) * 100)}%`,
      );

      marker.addTo(markerLayer);
    });

    if (points.length > 0) {
      const bounds = L.latLngBounds(points.map((point) => [point.latitude, point.longitude] as [number, number]));
      map.fitBounds(bounds.pad(0.2));
    } else {
      map.setView([20, 0], 2);
    }
  }, [points]);

  return <div ref={mapRef} style={{ height: "100vh", width: "100%" }} />;
}
