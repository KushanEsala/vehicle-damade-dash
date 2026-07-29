"use client";

import {FormEvent, useEffect, useState} from "react";
import {useRouter} from "next/navigation";
import {LockKeyhole, ShieldCheck, Sun, Moon} from "lucide-react";
import {api} from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [dark, setDark] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem("theme") !== "light";
    setDark(saved);
    document.documentElement.dataset.theme = saved ? "dark" : "light";
    const authNotice = sessionStorage.getItem("auth_notice");
    if (authNotice) {
      setError(authNotice);
      sessionStorage.removeItem("auth_notice");
    }
    api("/api/auth/session").then(() => router.replace("/dashboard")).catch(() => null);
  }, [router]);

  function toggleTheme() {
    const next = !dark;
    setDark(next);
    localStorage.setItem("theme", next ? "dark" : "light");
    document.documentElement.dataset.theme = next ? "dark" : "light";
  }

  async function submit(event: FormEvent) {
    event.preventDefault(); setBusy(true); setError("");
    try {
      await api("/api/auth/login", {method: "POST", body: JSON.stringify({identifier, password})});
      router.replace("/dashboard");
    } catch (err) { setError(err instanceof Error ? err.message : "Sign in failed."); }
    finally { setBusy(false); }
  }

  return (
    <main className="loginPage">
      <button className="themeFloating" onClick={toggleTheme} aria-label="Change colour theme">
        {dark ? <Sun size={19}/> : <Moon size={19}/>}
      </button>
      <section className="loginBrand">
        <div className="brandMark"><ShieldCheck size={28}/></div>
        <p className="eyebrow">APEX ASSURANCE</p>
        <h1>Vehicle claims,<br/>kept clear.</h1>
        <p className="lead">Register vehicles, assess damage and manage reports from one secure workspace.</p>
        <div className="loginFacts">
          <span>Controlled access</span><span>Traceable reports</span><span>Customer portal</span>
        </div>
      </section>
      <section className="loginPanel">
        <form className="loginCard" onSubmit={submit}>
          <div className="iconTile"><LockKeyhole size={22}/></div>
          <p className="eyebrow">ACCOUNT ACCESS</p>
          <h2>Sign in</h2>
          <p className="muted">Use your registered username or email address.</p>
          <label>Username or email<input autoFocus required value={identifier} onChange={e => setIdentifier(e.target.value)}/></label>
          <label>Password<input required type="password" value={password} onChange={e => setPassword(e.target.value)}/></label>
          {error && <div className="alert error">{error}</div>}
          <button className="primary" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
          <p className="loginHelp">Customer access is issued when an operator registers the customer.</p>
        </form>
      </section>
    </main>
  );
}
