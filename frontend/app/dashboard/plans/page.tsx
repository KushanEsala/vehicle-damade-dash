"use client";

import {FormEvent, useEffect, useState} from "react";
import {Edit3, Plus, ShieldCheck, Trash2, X} from "lucide-react";
import {api, User} from "@/lib/api";
import {Heading, Money} from "@/components/PageParts";

type Plan = {
  id: number; plan_code: string; name: string; description: string; deductible_amount: number;
  coverage_limit: number | null; currency_code: string; is_active: boolean;
};

export default function Plans() {
  const [plans, setPlans] = useState<Plan[]>([]);
  const [user, setUser] = useState<User | null>(null);
  const [editing, setEditing] = useState<Plan | "new" | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const canManage = user?.role === "admin";

  const load = () => api<Plan[]>("/api/plans").then(setPlans);
  useEffect(() => {
    Promise.all([load(), api<{user: User}>("/api/auth/session").then(result => setUser(result.user))])
      .catch(reason => setError(reason.message));
  }, []);

  async function save(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError("");
    const values = Object.fromEntries(new FormData(event.currentTarget));
    const body = {
      plan_code: String(values.plan_code),
      name: String(values.name),
      description: String(values.description),
      deductible_amount: Number(values.deductible_amount),
      coverage_limit: values.coverage_limit ? Number(values.coverage_limit) : null,
      currency_code: String(values.currency_code),
      is_active: values.is_active === "on",
    };
    try {
      if (editing === "new") await api("/api/plans", {method: "POST", body: JSON.stringify(body)});
      else if (editing) await api(`/api/plans/${editing.id}`, {method: "PATCH", body: JSON.stringify(body)});
      await load();
      setEditing(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Insurance plan could not be saved.");
    } finally {
      setBusy(false);
    }
  }

  async function remove(plan: Plan) {
    if (!window.confirm(`Delete insurance plan "${plan.name}"? This cannot be undone.`)) return;
    setError("");
    try {
      await api(`/api/plans/${plan.id}`, {method: "DELETE"});
      await load();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Insurance plan could not be deleted.");
    }
  }

  return <><Heading eyebrow="COVERAGE" title="Insurance plans"
    description="Create and maintain vehicle coverage plans, limits and deductibles."/>
    <div className="moduleToolbar">
      <div><span className="status ok">{plans.filter(plan => plan.is_active).length} active</span>
        <span className="status">{plans.length} total</span></div>
      {canManage && <button className="primary" onClick={() => setEditing("new")}><Plus/>New plan</button>}
    </div>
    {error && <div className="alert error">{error}</div>}
    {editing && <section className="settingsSection planEditor">
      <div className="settingsTitle"><ShieldCheck/><div><h2>{editing === "new" ? "Create insurance plan" : "Edit insurance plan"}</h2>
        <p>Configure coverage and availability.</p></div></div>
      <form className="formGrid" onSubmit={save}>
        <label>Plan code<input name="plan_code" defaultValue={editing === "new" ? "" : editing.plan_code} required/></label>
        <label>Plan name<input name="name" defaultValue={editing === "new" ? "" : editing.name} required/></label>
        <label className="wide">Description<textarea name="description" defaultValue={editing === "new" ? "" : editing.description} required/></label>
        <label>Coverage limit<input name="coverage_limit" type="number" min="0" step=".01"
          defaultValue={editing === "new" ? "" : editing.coverage_limit ?? ""}/></label>
        <label>Deductible amount<input name="deductible_amount" type="number" min="0" step=".01"
          defaultValue={editing === "new" ? 0 : editing.deductible_amount} required/></label>
        <label>Currency<input name="currency_code" maxLength={3} defaultValue={editing === "new" ? "LKR" : editing.currency_code} required/></label>
        <label className="checkField"><input name="is_active" type="checkbox"
          defaultChecked={editing === "new" || editing.is_active}/>Plan is active</label>
        <div className="editorActions"><button type="button" className="secondary" onClick={() => setEditing(null)}><X/>Cancel</button>
          <button className="primary" disabled={busy}>{busy ? "Saving…" : "Save plan"}</button></div>
      </form>
    </section>}
    <section className="planGrid">{plans.map(plan => <article className={`planCard ${!plan.is_active ? "inactive" : ""}`} key={plan.id}>
      <div className="planTop"><div><p className="eyebrow">{plan.plan_code}</p><h3>{plan.name}</h3></div>
        <span className={`status ${plan.is_active ? "ok" : ""}`}>{plan.is_active ? "Active" : "Inactive"}</span></div>
      <p>{plan.description}</p><dl>
        <div><dt>Coverage limit</dt><dd>{plan.coverage_limit != null ? <Money value={plan.coverage_limit} currency={plan.currency_code}/> : "Not set"}</dd></div>
        <div><dt>Deductible</dt><dd><Money value={plan.deductible_amount} currency={plan.currency_code}/></dd></div>
      </dl>
      {canManage && <div className="planActions"><button className="secondary" onClick={() => setEditing(plan)}><Edit3/>Edit</button>
        <button className="dangerButton" onClick={() => remove(plan)}><Trash2/>Delete</button></div>}
    </article>)}</section>
  </>;
}
