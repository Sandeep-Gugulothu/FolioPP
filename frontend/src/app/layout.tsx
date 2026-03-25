import "./css/style.css";
import { Outfit, EB_Garamond } from "next/font/google";

const outfit = Outfit({
  subsets: ["latin"],
  variable: "--outfit-font",
  display: "swap",
});

const fontSerif = EB_Garamond({
  subsets: ["latin"],
  variable: "--font-serif",
  display: "swap",
});

export const metadata = {
  title: "FolioPP - The AI-Native Terminal",
  description: "The Reasoning Layer for Modern Finance and Autonomous Reasoning.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body
        className={`${outfit.variable} ${fontSerif.variable} bg-primary-bg tracking-tight text-primary-text antialiased`}
        style={{ fontFamily: 'var(--outfit-font), sans-serif' }}
      >
        <div className="flex min-h-screen flex-col overflow-hidden supports-[overflow:clip]:overflow-clip">
          {children}
        </div>
      </body>
    </html>
  );
}
