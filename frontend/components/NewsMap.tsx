"use client";

import L from "leaflet";
import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const LeafletMapContainer = MapContainer as any;
const LeafletTileLayer = TileLayer as any;
const LeafletMarker = Marker as any;
const LeafletPopup = Popup as any;

const defaultIcon = L.icon({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
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
  return (
    <LeafletMapContainer
      center={[20, 0]}
      zoom={2}
      scrollWheelZoom={true}
      style={{ height: "100vh", width: "100%" }}
    >
      <LeafletTileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {points.map((point) => (
        <LeafletMarker key={point.id} position={[point.latitude, point.longitude]} icon={defaultIcon}>
          <LeafletPopup>
            <strong>{point.title}</strong>
            <br />
            {point.location_name || "Unknown location"}
            <br />
            Related articles: {point.article_count ?? 1}
            <br />
            Confidence: {Math.round((point.confidence_score ?? 0) * 100)}%
          </LeafletPopup>
        </LeafletMarker>
      ))}
    </LeafletMapContainer>
  );
}
