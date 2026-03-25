"use client";

import { MapContainer, Marker, Popup, TileLayer } from "react-leaflet";
import "leaflet/dist/leaflet.css";

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
        <Marker key={point.id} position={[point.latitude, point.longitude]}>
          <Popup>
            <strong>{point.title}</strong>
            <br />
            {point.location_name || "Unknown location"}
            <br />
            <a href={point.url} target="_blank">Open article</a>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}