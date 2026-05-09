import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "VitaChain - Plateforme Agri-Alimentaire Marocaine",
  description: "Connectez les agriculteurs, restaurants et citoyens pour une alimentation durable au Maroc",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="fr">
      <body className={`${inter.className} scroll-smooth`}>
        {children}
      </body>
    </html>
  );
}
