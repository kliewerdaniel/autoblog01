import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import Header from "../../components/Header";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Auto-Blog",
  description: "An automated blogging platform powered by AI for creating and managing content with ease.",
  keywords: ["Auto-Blog", "AI Blogging", "Automated Content", "AI Writer", "Blog Management"],
  authors: [{ name: "Auto-Blog Team" }],
  creator: "Auto-Blog Team",
  publisher: "Auto-Blog Team",
  openGraph: {
    title: "Auto-Blog",
    description: "An automated blogging platform powered by AI for creating and managing content with ease.",
    url: "https://example.com",
    siteName: "Auto-Blog",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Auto-Blog",
    description: "An automated blogging platform powered by AI for creating and managing content with ease.",
    creator: "@autoblog",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="h-full">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                if (typeof window !== 'undefined') {
                  if (window.location.pathname === '/') {
                    document.body.classList.add('home-page');
                  }
                  console.log('Body className:', document.body.className);
                }
              })();
            `,
          }}
        />
      </head>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-full flex flex-col`}
      >
        <Header />
        <main className="flex-1 pt-16">
          {children}
        </main>
      </body>
    </html>
  );
}
