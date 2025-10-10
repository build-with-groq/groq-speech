import type { Metadata, Viewport } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
    title: "Groq Speech Recognition Demo",
    description: "Real-time speech transcription and translation with performance metrics using Groq API",
    keywords: ["speech recognition", "transcription", "translation", "groq", "ai", "nextjs"],
    authors: [{ name: "Groq Speech Demo" }],
};

export const viewport: Viewport = {
    width: "device-width",
    initialScale: 1,
};

export default function RootLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <html lang="en">
            <body className={inter.className} suppressHydrationWarning={true}>
                {children}
            </body>
        </html>
    );
}
