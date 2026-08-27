"use client";

import {FormEvent, useEffect, useState} from "react";
import {Check, Copy, KeyRound, Power, PowerOff, Trash2, UserPlus, X} from "lucide-react";
import {api, User} from "@/lib/api";
import {Heading} from "@/components/PageParts";

type Account = {id: number; username: string; email: string; role: string; is_active: boolean; customer_id: number | null};
type PassModal = {username: string; password: string};

export default function Users() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);
  const [passModal, setPassModal] = useState<PassModal | null>(null);
  const [copied, setCopied] = useState(false);

  const load = () => api<Account[]>("/api/users").then(setAccounts);
  useEffect(() => {
    Promise.all([load(), api<{user: User}>("/api/auth/session").then(result => setCurrentUser(result.user))])
      .catch(reason => setError(reason.message));
  }, []);

  function copyToClipboard(text: string) {
    if (typeof navigator !== "undefined" && navigator.clipboard) {
      navigator.clipboard.writeText(text).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  }

  async function createAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    setError("");
    setMessage("");
    const values = Object.fromEntries(new FormData(form));
    try {
      const result = await api<{temporary_password: string}>("/api/users", {
        method: "POST", body: JSON.stringify(values),
      });
      const username = String(values.username || "Account");
      setMessage(`Account created. Temporary password: ${result.temporary_password}`);
      setPassModal({username, password: result.temporary_password});
      form.reset();
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create account.");
    }
  }

  async function generatePassword(account: Account) {
    if (!window.confirm(`Generate new temporary password for "${account.username}"?`)) return;
    setBusyId(account.id);
    setError("");
    setMessage("");
    try {
      const result = await api<{temporary_password: string}>(`/api/users/${account.id}/reset-password`, {
        method: "POST",
      });
      setMessage(`New temporary password for ${account.username}: ${result.temporary_password}`);
      setPassModal({username: account.username, password: result.temporary_password});
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to generate password.");
    } finally {
      setBusyId(null);
    }
  }

  async function changeStatus(account: Account) {
    if (account.is_active && !window.confirm(`Deactivate "${account.username}"? Their active sessions will end immediately.`)) return;
    setBusyId(account.id);
    setError("");
    try {
      await api(`/api/users/${account.id}/status`, {
        method: "PATCH", body: JSON.stringify({is_active: !account.is_active}),
      });
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to update the account.");
    } finally {
      setBusyId(null);
    }
  }

  async function deleteAccount(account: Account) {
    if (!window.confirm(`Permanently delete "${account.username}"? This cannot be undone.`)) return;
    setBusyId(account.id);
    setError("");
    try {
      await api(`/api/users/${account.id}`, {method: "DELETE"});
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to delete the account.");
    } finally {
      setBusyId(null);
    }
  }

  return <><Heading eyebrow="ADMINISTRATION" title="User management"
    description="Create staff accounts and control access for registered users."/>
    
    {/* Password Modal Popup */}
    {passModal && (
      <div style={{
        position: "fixed", inset: 0, background: "rgba(0, 0, 0, 0.65)",
        backdropFilter: "blur(4px)", display: "grid", placeItems: "center", zIndex: 1000, padding: "1rem"
      }}>
        <div style={{
          background: "var(--surface)", border: "1px solid var(--line)", borderRadius: "16px",
          padding: "1.75rem", maxWidth: "480px", width: "100%", boxShadow: "var(--shadow)"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <div style={{ width: "40px", height: "40px", borderRadius: "12px", background: "var(--accent)", color: "#032b2a", display: "grid", placeItems: "center" }}>
                <KeyRound style={{ width: "22px", height: "22px" }} />
              </div>
              <div>
                <h3 style={{ margin: 0, fontSize: "1.15rem" }}>Temporary Password</h3>
                <span style={{ fontSize: "0.84rem", color: "var(--muted)" }}>User: <strong>{passModal.username}</strong></span>
              </div>
            </div>
            <button className="secondary" onClick={() => setPassModal(null)} style={{ padding: "0.3rem 0.5rem" }}>
              <X style={{ width: "16px", height: "16px" }} />
            </button>
          </div>

          <p style={{ fontSize: "0.88rem", color: "var(--muted)", margin: "0 0 1rem" }}>
            Copy and share this temporary password with the user.
          </p>

          <div style={{
            display: "flex", alignItems: "center", gap: "0.6rem", background: "var(--surface2)",
            border: "1px solid var(--line)", padding: "0.75rem 1rem", borderRadius: "10px", marginBottom: "1.25rem"
          }}>
            <code style={{ fontSize: "1.15rem", fontWeight: "700", fontFamily: "monospace", letterSpacing: "0.05em", flex: 1, color: "var(--accent)" }}>
              {passModal.password}
            </code>
            <button className="primary" onClick={() => copyToClipboard(passModal.password)} style={{ padding: "0.45rem 0.85rem", fontSize: "0.82rem" }}>
              {copied ? <Check style={{ width: "16px", height: "16px" }} /> : <Copy style={{ width: "16px", height: "16px" }} />}
              {copied ? "Copied!" : "Copy"}
            </button>
          </div>

          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <button className="primary" onClick={() => setPassModal(null)}>
              Done
            </button>
          </div>
        </div>
      </div>
    )}

    <section className="panel"><div className="sectionHeading"><UserPlus/><div><h2>Create staff account</h2>
      <p>Customer portal accounts are created automatically from Customer registration.</p></div></div>
      <form className="formGrid" onSubmit={createAccount}>
        <label>Username<input name="username" required/></label>
        <label>Email<input name="email" type="email" required/></label>
        <label>Role<select name="role_code"><option value="operator">Operator</option><option value="admin">Administrator</option></select></label>
        <button className="primary">Create account</button>
      </form>
      {message && (
        <div className="alert" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>{message}</span>
          {passModal && (
            <button className="secondary" onClick={() => copyToClipboard(passModal.password)} style={{ padding: "0.3rem 0.6rem", fontSize: "0.78rem" }}>
              {copied ? <Check style={{ width: "14px", height: "14px" }} /> : <Copy style={{ width: "14px", height: "14px" }} />}
              {copied ? "Copied" : "Copy password"}
            </button>
          )}
        </div>
      )}
      {error && <div className="alert error">{error}</div>}
    </section>

    <section className="panel tablePanel"><div className="tableWrap"><table><thead><tr>
      <th>User</th><th>Email</th><th>Role</th><th>Status</th><th>Access controls</th>
    </tr></thead><tbody>{accounts.map(account => {
      const isSelf = account.id === currentUser?.id;
      return <tr key={account.id}>
        <td><strong>{account.username}</strong>{isSelf && <small>Current account</small>}</td>
        <td>{account.email}</td><td><span className="status">{account.role}</span></td>
        <td><span className={`status ${account.is_active ? "ok" : ""}`}>{account.is_active ? "Active" : "Deactivated"}</span></td>
        <td><div className="rowActions">
          <button className="secondary" disabled={busyId === account.id} onClick={() => generatePassword(account)}>
            <KeyRound/>Generate password
          </button>
          <button className="secondary" disabled={isSelf || busyId === account.id} onClick={() => changeStatus(account)}>
            {account.is_active ? <PowerOff/> : <Power/>}{account.is_active ? "Deactivate" : "Activate"}
          </button>
          <button className="dangerButton" disabled={isSelf || busyId === account.id} onClick={() => deleteAccount(account)}>
            <Trash2/>Delete
          </button>
        </div></td>
      </tr>;
    })}</tbody></table></div></section>
  </>;
}
