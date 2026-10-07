import type { Metadata } from "next";

// "metadata" can only be exported from a SERVER component. Our page.tsx files
// are client components, so this tiny layout carries the title instead.
export const metadata: Metadata = {
  title: "Documents",
};

export default function DocumentsLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return children;
}