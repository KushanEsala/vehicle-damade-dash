"use client";

import Link from "next/link";
import {usePathname, useRouter} from "next/navigation";
import {useEffect, useMemo, useState} from "react";
import {
  BarChart3, Building2, CarFront, ClipboardCheck, FileText, LogOut, Menu,
  Moon, PlusSquare, ShieldCheck, Sun, UserCircle, Users, WalletCards, X,
} from "lucide-react";
import {api, User} from "@/lib/api";
import WorkspaceLoader from "@/components/WorkspaceLoader";
import ToastViewport from "@/components/ToastViewport";

const navigation = {
  admin: [
    ["Overview", "/dashboard", BarChart3], ["New assessment", "/dashboard/new-assessment", PlusSquare],
    ["Assessment review", "/dashboard/assessments", ClipboardCheck], ["Damage reports", "/dashboard/reports", FileText],
    ["Customers", "/dashboard/customers", Users], ["Vehicles", "/dashboard/vehicles", CarFront],
    ["Insurance plans", "/dashboard/plans", WalletCards], ["Company settings", "/dashboard/company", Building2],
    ["User management", "/dashboard/users", Users],
    ["My profile", "/dashboard/profile", UserCircle],
  ],
  operator: [
    ["Overview", "/dashboard", BarChart3], ["New assessment", "/dashboard/new-assessment", PlusSquare],
    ["Assessment review", "/dashboard/assessments", ClipboardCheck], ["Damage reports", "/dashboard/reports", FileText],
    ["Customers", "/dashboard/customers", Users], ["Vehicles", "/dashboard/vehicles", CarFront],
    ["Insurance plans", "/dashboard/plans", WalletCards], ["My profile", "/dashboard/profile", UserCircle],
  ],
  customer: [
    ["My overview", "/dashboard", BarChart3], ["My assessments", "/dashboard/assessments", ClipboardCheck],
    ["My reports", "/dashboard/reports", FileText], ["My vehicles", "/dashboard/vehicles", CarFront],
    ["My profile", "/dashboard/profile", UserCircle],
  ],
} as const;

export default function AppShell({children}: {children: React.ReactNode}) {
  const router = useRouter(); const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false); const [open, setOpen] = useState(false);
  const [dark, setDark] = useState(true);
  useEffect(() => {
    const saved = localStorage.getItem("theme") !== "light";
    setDark(saved); document.documentElement.dataset.theme = saved ? "dark" : "light";
    api<{user: User}>("/api/auth/session").then(r => setUser(r.user)).catch(() => router.replace("/login")).finally(() => setReady(true));
  }, [router]);
  useEffect(() => setOpen(false), [pathname]);
  const links = useMemo(() => user ? navigation[user.role] : [], [user]);
  function theme() { const next = !dark; setDark(next); localStorage.setItem("theme", next ? "dark" : "light"); document.documentElement.dataset.theme = next ? "dark" : "light"; }
  async function logout() { await api("/api/auth/logout", {method: "POST"}).catch(() => null); router.replace("/login"); }
  if (!ready || !user) return <WorkspaceLoader/>;
  return (
    <div className="appFrame">
      <aside className={`sidebar ${open ? "open" : ""}`}>
        <div className="sideBrand"><div className="brandMark"><ShieldCheck size={22}/></div><div><strong>APEX</strong><small>ASSURANCE</small></div><button className="mobileClose" onClick={() => setOpen(false)}><X/></button></div>
        <nav>{links.map(([label, href, Icon]) => <Link key={href} className={pathname === href ? "active" : ""} href={href}><Icon size={18}/><span>{label}</span></Link>)}</nav>
        <div className="sideFooter">
          <div className="userBadge"><UserCircle/><div><strong>{user.username}</strong><small>{user.role}</small></div></div>
          <button className="signout" onClick={logout}><LogOut size={17}/>Sign out</button>
        </div>
      </aside>
      {open && <button className="scrim" aria-label="Close navigation" onClick={() => setOpen(false)}/>}
      <div className="workspace">
        <header className="topbar">
          <button className="menuButton" onClick={() => setOpen(true)}><Menu/></button>
          <span className="topTitle">Claims workspace</span>
          <button className="iconButton" onClick={theme} aria-label="Change colour theme">{dark ? <Sun/> : <Moon/>}</button>
        </header>
        <main className="content">{children}</main>
      </div>
      <ToastViewport/>
    </div>
  );
}
