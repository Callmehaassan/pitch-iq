import type { Metadata } from "next";
import "./globals.css";
import Navbar from "@/components/Navbar";

export const metadata: Metadata = {
  title: "Pitch IQ",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="relative min-h-screen text-slate-100 overflow-x-hidden">
        {/* Full-bleed stadium background image, fixed so it stays put while scrolling */}
        <div className="fixed inset-0 -z-20">
          <div
            className="absolute inset-0 bg-cover bg-center"
            style={{ backgroundImage: "url('/images/stadium-bg.jpg')" }}
          />
          {/* Diagonal color tint overlay, teal to purple like UCL/FIFA style dashboards */}
          <div className="absolute inset-0 bg-gradient-to-br from-teal-900/80 via-slate-950/85 to-fuchsia-950/80" />
          {/* Extra darken so text stays readable */}
          <div className="absolute inset-0 bg-black/40" />
        </div>

        <Navbar />
        {children}
      </body>
    </html>
  );
}
