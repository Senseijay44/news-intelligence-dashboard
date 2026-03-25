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
  source_count?: number;
  confidence_score?: number;
};

const markerIcon = L.divIcon({
  className: "intel-marker-wrapper",
  html: '<span class="intel-marker"></span>',
  iconSize: [18, 18],
  iconAnchor: [9, 9],
  popupAnchor: [0, -10],
});

export default function NewsMapClient({ points }: { points: MapPoint[] }) {
  const mapRef = useRef<HTMLDivElement | null>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersLayerRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!mapRef.current || mapInstanceRef.current) {
      return;
    }

    const map = L.map(mapRef.current, { zoomControl: false }).setView([20, 0], 2);
    mapInstanceRef.current = map;

    L.control.zoom({ position: "bottomright" }).addTo(map);

    L.tileLayer("https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png", {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; CARTO',
      subdomains: "abcd",
      maxZoom: 20,
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
      const marker = L.marker([point.latitude, point.longitude], { icon: markerIcon });

      marker.bindPopup(`
        <div class="popup-card">
          <div class="popup-title">${point.title}</div>
          <div class="popup-subtitle">${point.location_name || "Unknown location"}</div>
          <div class="popup-metrics">
            <span>${point.article_count ?? 1} articles</span>
            ${point.source_count ? `<span>${point.source_count} sources</span>` : ""}
            <span>${Math.round((point.confidence_score ?? 0) * 100)}% confidence</span>
          </div>
        </div>
      `);

      marker.addTo(markerLayer);
    });

    if (points.length > 0) {
      const bounds = L.latLngBounds(points.map((point) => [point.latitude, point.longitude] as [number, number]));
      map.fitBounds(bounds.pad(0.2));
    } else {
      map.setView([20, 0], 2);
    }
  }, [points]);

  return <div ref={mapRef} className="map-canvas" />;
}
