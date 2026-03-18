import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Context7 India — AI Documentation for Indian APIs",
  description:
    "Razorpay, Zerodha Kite, ONDC, UPI, GST APIs instantly in Claude, Cursor, and VS Code. " +
    "Hindi documentation. Offline-first. Free to start.",
  keywords: "razorpay docs, zerodha kite api, ondc integration, upi api, indian api documentation, mcp server india",
  openGraph: {
    title: "Context7 India",
    description: "The documentation layer India's developers deserved.",
    url: "https://context7india.com",
    siteName: "Context7 India",
    locale: "en_IN",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
