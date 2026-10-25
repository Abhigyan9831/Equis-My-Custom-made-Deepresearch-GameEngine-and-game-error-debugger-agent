import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Agent UI",
  description: "Dark glassmorphic AI agent interface",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="dark">
      <body>{children}</body>
    </html>
  );
}
