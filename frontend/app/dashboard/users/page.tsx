"use client";

import {FormEvent, useEffect, useState} from "react";
import {Power, PowerOff, Trash2, UserPlus} from "lucide-react";
import {api, User} from "@/lib/api";
import {Heading} from "@/components/PageParts";

type Account = {id: number; username: string; email: string; role: string; is_active: boolean; customer_id: number | null};

export default function Users() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState<number | null>(null);

  const load = () => api<Account[]>("/api/users").then(setAccounts);
  useEffect(() => {
    Promise.all([load(), api<{user: User}>("/api/auth/session").then(result => setCurrentUser(result.user))])
      .catch(reason => setError(reason.message));
  }, []);

  async function createAccount(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    const values = Object.fromEntries(new FormData(event.currentTarget));
    try {
      const result = await api<{temporary_password: string}>("/api/users", {
        method: "POST", body: JSON.stringify(values),
      });
      setMessage(`Account created. Temporary password: ${result.temporary_password}`);
      event.currentTarget.reset();
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to create account.");
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
    <section className="panel"><div className="sectionHeading"><UserPlus/><div><h2>Create staff account</h2>
      <p>Customer portal accounts are created from Customer registration.</p></div></div>
      <form className="formGrid" onSubmit={createAccount}>
        <label>Username<input name="username" required/></label>
        <label>Email<input name="email" type="email" required/></label>
        <label>Role<select name="role_code"><option value="operator">Operator</option><option value="admin">Administrator</option></select></label>
        <button className="primary">Create account</button>
      </form>
      {message && <div className="alert">{message}</div>}
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
