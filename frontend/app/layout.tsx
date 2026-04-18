import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Shaka-Security-Scanner | SOC Dashboard",
  description: "AI-assisted penetration testing and vulnerability intelligence platform"
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
