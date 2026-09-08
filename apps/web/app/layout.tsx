import type { Metadata } from "next";

export const metadata: Metadata = { title: "AURA — Engineering Intelligence", description: "Evidence-backed software engineering intelligence." };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
