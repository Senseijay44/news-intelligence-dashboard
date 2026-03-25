import "./globals.css";
import "leaflet/dist/leaflet.css";

export const metadata = {
  title: "News Intelligence Dashboard",
  description: "Map-first news intelligence dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
