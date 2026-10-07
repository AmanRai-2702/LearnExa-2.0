"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

// One list drives the whole menu. To add a page later, add one line here.
const NAV_LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/documents", label: "Documents" },
  { href: "/chat", label: "Chat" },
];

// Styling is kept in named constants so the JSX below stays readable.
const LINK_BASE = "rounded-md px-3 py-1.5 text-sm font-medium transition-colors";
const LINK_ACTIVE = "bg-zinc-100 text-zinc-900 dark:bg-zinc-800 dark:text-zinc-50";
const LINK_INACTIVE =
  "text-zinc-600 hover:text-zinc-900 dark:text-zinc-400 dark:hover:text-zinc-50";

// "/" is a prefix of every path, so it must match exactly.
// Other links match any path that starts with them (e.g. /documents/123).
function isActive(pathname: string, href: string): boolean {
  return href === "/" ? pathname === "/" : pathname.startsWith(href);
}

export default function Navbar() {
  // The hook gives us the current URL path, e.g. "/documents".
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-10 border-b border-zinc-200 bg-background/80 backdrop-blur dark:border-zinc-800">
      <nav className="mx-auto flex h-14 max-w-5xl items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2 font-semibold tracking-tight">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-indigo-600 text-sm text-white">
            L
          </span>
          LearnExa
        </Link>

        <ul className="flex items-center gap-1">
          {NAV_LINKS.map((link) => {
            const active = isActive(pathname, link.href);
            return (
              <li key={link.href}>
                <Link
                  href={link.href}
                  aria-current={active ? "page" : undefined}
                  className={`${LINK_BASE} ${active ? LINK_ACTIVE : LINK_INACTIVE}`}
                >
                  {link.label}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
    </header>
  );
}