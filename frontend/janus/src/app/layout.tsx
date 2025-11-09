import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Janus - AI GTM OS",
  description: "AI-powered Go-To-Market OS for technical founders",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
