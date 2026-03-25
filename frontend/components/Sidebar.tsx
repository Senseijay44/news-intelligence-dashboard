export default function Sidebar({ points }: { points: any[] }) {
  return (
    <div style={{ width: 420, height: "100vh", overflowY: "auto", borderRight: "1px solid #ddd", padding: 16 }}>
      <h2>Latest Geolocated News</h2>
      {points.map((item) => (
        <div key={item.id} style={{ marginBottom: 16 }}>
          <div style={{ fontWeight: 700 }}>{item.title}</div>
          <div>{item.location_name || "Unknown location"}</div>
          <div style={{ fontSize: 12, opacity: 0.7 }}>{item.published_at || "No date"}</div>
        </div>
      ))}
    </div>
  );
}