import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "LectureIQ",
  description: "Cited, timestamped answers over your lectures",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
