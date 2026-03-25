import MapPanel from "../components/MapPanel";
import Sidebar from "../components/Sidebar";
import { fetchMapPoints } from "../lib/api";

export default async function HomePage() {
  const points = await fetchMapPoints();

  return (
    <main style={{ display: "flex", minHeight: "100vh" }}>
      <Sidebar points={points} />
      <div style={{ flex: 1 }}>
        <MapPanel points={points} />
      </div>
    </main>
  );
}
