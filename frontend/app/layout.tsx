import type {Metadata} from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Apex Assurance",
  description: "Vehicle claims and assessment portal",
};

export default function RootLayout({children}: Readonly<{children: React.ReactNode}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>{children}</body>
    </html>
  );
}
