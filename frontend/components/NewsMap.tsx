"use client";

import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const defaultIcon = L.icon({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

export default function NewsMap({ points }: { points: any[] }) {
  return (
    <MapContainer
      center={[20, 0]}
      zoom={2}
      scrollWheelZoom={true}
      style={{ height: "100vh", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {points.map((point) => (
        <Marker key={point.id} position={[point.latitude, point.longitude]} icon={defaultIcon}>
          <Popup>
            <strong>{point.title}</strong>
            <br />
            {point.location_name || "Unknown location"}
            <br />
            Related articles: {point.article_count ?? 1}
            <br />
            Confidence: {Math.round((point.confidence_score ?? 0) * 100)}%
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
