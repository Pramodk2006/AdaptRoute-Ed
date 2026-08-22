import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--font-outfit",
  display: "swap",
});

export const metadata: Metadata = {
  title: {
    default: "AdaptRoute-Edu | AI-Powered Adaptive Learning",
    template: "%s | AdaptRoute-Edu",
  },
  description:
    "AdaptRoute-Edu: Your personalised AI tutor. Get a custom learning roadmap, study materials, and quizzes tailored to your goals.",
  keywords: ["adaptive learning", "AI tutor", "personalised education", "roadmap"],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} ${outfit.variable} font-sans bg-surface-900 text-slate-100 antialiased`}
      >
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
