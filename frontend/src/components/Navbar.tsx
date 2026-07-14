"use client";

import { useState } from "react";
import { usePathname } from "next/navigation";
import Link from "next/link";

const NAV_LINKS = [
  { href: "/", label: "Dashboard" },
  { href: "/league", label: "Standings" },
  { href: "/players", label: "Players" },
  { href: "/scout", label: "Scout AI" },
  { href: "/transfer", label: "Transfer Sim" },
  { href: "/ucl", label: "UCL Bracket" },
  { href: "/predictions", label: "2026/27" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <nav className="sticky top-0 z-50 backdrop-blur-md bg-black/30 border-b border-white/10">
      <div className="max-w-7xl mx-auto px-6 flex items-center justify-between h-16">
        <Link href="/" className="flex items-center gap-2 group">
          <span className="w-8 h-8 flex items-center justify-center rounded-md bg-gradient-to-br from-teal-400 to-fuchsia-600 shadow-[0_0_18px_rgba(45,212,191,0.5)] font-black text-sm text-white tracking-tighter">
            IQ
          </span>

          <span className="font-black text-xl tracking-tight uppercase text-white">
            Pitch <span className="text-teal-300">IQ</span>
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-stretch gap-1 h-full">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={
                "px-4 flex items-center text-[13px] font-bold uppercase tracking-wide transition-colors border-b-2 " +
                (pathname === link.href
                  ? "border-teal-300 text-white"
                  : "border-transparent text-slate-300 hover:text-teal-200 hover:border-teal-400/40")
              }
            >
              {link.label}
            </Link>
          ))}
        </div>

        {/* Mobile Menu Button */}
        <button
          type="button"
          className="md:hidden text-slate-300 hover:text-white p-2"
          onClick={() => setOpen(!open)}
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              clipRule="evenodd"
              d="M3 5a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 10a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM3 15a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"
            />
          </svg>
        </button>
      </div>

      {/* Mobile Navigation */}
      {open && (
        <div className="md:hidden border-t border-white/10 px-6 py-3 flex flex-col gap-1 bg-black/50">
          {NAV_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setOpen(false)}
              className={
                "px-3 py-2 rounded-md text-sm font-bold uppercase tracking-wide transition-colors " +
                (pathname === link.href
                  ? "bg-teal-900/30 text-teal-300 border-l-2 border-l-teal-400"
                  : "text-slate-300 hover:text-teal-200 hover:bg-white/5")
              }
            >
              {link.label}
            </Link>
          ))}
        </div>
      )}
    </nav>
  );
}