"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { BrandMark } from "@/components/brand/BrandMark";
import { Marquee } from "@/components/layout/Marquee";
import { WalletButton } from "@/components/layout/WalletButton";
import { Button } from "@/components/ui/Button";

const links = [["Overview", "/dashboard"], ["Trade", "/trade"], ["Discover", "/assets"], ["News", "/news"], ["Watchlist", "/watchlist"], ["Baskets", "/baskets"], ["Portfolio", "/portfolio"], ["Social", "/leaderboard"], ["More", "/more"]] as const;

export function AppShell({ children }: Readonly<{ children: React.ReactNode }>) {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => setMenuOpen(false), [pathname]);
  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [menuOpen]);

  return <div className="site-frame"><Marquee /><header className="site-header"><Link href="/" aria-label="Percorium home"><BrandMark /></Link><nav id="primary-navigation" className={`header-center nav-pills${menuOpen ? " menu-open" : ""}`} aria-label="Primary navigation">{links.map(([label, href]) => <Link className={`nav-pill${pathname === href || pathname.startsWith(`${href}/`) ? " active" : ""}`} href={href} key={href} onClick={() => setMenuOpen(false)}>{label}</Link>)}</nav><div className="header-end"><WalletButton /><Button href="/trade">Launch trade</Button><button className={`menu-toggle${menuOpen ? " is-open" : ""}`} type="button" aria-label={menuOpen ? "Close navigation" : "Open navigation"} aria-expanded={menuOpen} aria-controls="primary-navigation" onClick={() => setMenuOpen((open) => !open)}><span /><span /><span /></button></div></header><main>{children}</main><footer className="site-footer"><p>© 2026 Percorium · Solana first · 50 bps</p><div className="footer-links"><Link href="/more">More</Link><Link href="/gifts">Send a gift</Link></div></footer></div>;
}
