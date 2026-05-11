import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Providers } from "./providers";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "VitaChain - Plateforme Agri-Alimentaire Marocaine",
  description: "Connectez les agriculteurs, restaurants et citoyens pour une alimentation durable au Maroc",
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000'),
  keywords: ['agriculture', 'maroc', 'bio', 'local', 'restaurant', 'citoyen'],
  authors: [{ name: 'VitaChain Team' }],
  openGraph: {
    title: 'VitaChain - Plateforme Agri-Alimentaire Marocaine',
    description: 'Connectez les agriculteurs, restaurants et citoyens pour une alimentation durable au Maroc',
    url: '/',
    siteName: 'VitaChain',
    locale: 'fr_FR',
    type: 'website',
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="theme-color" content="#16a34a" />
        <link rel="icon" href="/favicon.ico" />
      </head>
      <body className={`${inter.className} scroll-smooth`}>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  );
}
