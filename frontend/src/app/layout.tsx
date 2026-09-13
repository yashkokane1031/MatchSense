import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/common/Navbar";

export const metadata: Metadata = {
  title: "MatchSense | Premier League Predictive Intelligence",
  description: "Independent Dixon-Coles Poisson vs. CatBoost/XGBoost dual-model Premier League predictive intelligence dashboard.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="antialiased bg-[#0a0d14] text-slate-100 min-h-screen">
        <Navbar />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </body>
    </html>
  );
}
