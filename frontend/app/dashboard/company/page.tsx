"use client";

import {FormEvent, useEffect, useState} from "react";
import {Building2, FileText, Landmark, MapPin} from "lucide-react";
import {api} from "@/lib/api";
import {Heading} from "@/components/PageParts";

type Company = {
  company_name: string; registration_number: string; address_line_1: string; address_line_2: string | null;
  city: string; phone: string; email: string; website: string | null; currency_code: string;
  tax_label: string; tax_rate: number; report_footer: string | null;
};

export default function CompanySettings() {
  const [company, setCompany] = useState<Company | null>(null);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => { api<Company>("/api/company").then(setCompany).catch(reason => setError(reason.message)); }, []);

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSaving(true);
    setError("");
    const values = Object.fromEntries(new FormData(event.currentTarget));
    try {
      const updated = await api<Company>("/api/company", {
        method: "PATCH",
        body: JSON.stringify({...values, tax_rate: Number(values.tax_rate) / 100}),
      });
      setCompany(updated);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Company settings could not be saved.");
    } finally {
      setSaving(false);
    }
  }

  if (!company) return <div className="loadingScreen">{error || "Loading company settings…"}</div>;

  return <><Heading eyebrow="ADMINISTRATION" title="Company settings"
    description="Manage the company information printed on customer damage reports."/>
    <form className="companySettings" onSubmit={submit}>
      <section className="settingsSection">
        <div className="settingsTitle"><Building2/><div><h2>Company identity</h2><p>Legal and public company information.</p></div></div>
        <div className="formGrid">
          <label>Company name<input name="company_name" defaultValue={company.company_name} required/></label>
          <label>Registration number<input name="registration_number" defaultValue={company.registration_number} required/></label>
          <label>Email address<input name="email" type="email" defaultValue={company.email} required/></label>
          <label>Phone number<input name="phone" defaultValue={company.phone} required/></label>
          <label className="wide">Website<input name="website" type="url" defaultValue={company.website || ""}/></label>
        </div>
      </section>
      <section className="settingsSection">
        <div className="settingsTitle"><MapPin/><div><h2>Registered address</h2><p>Address displayed in reports and customer records.</p></div></div>
        <div className="formGrid">
          <label className="wide">Address line 1<input name="address_line_1" defaultValue={company.address_line_1} required/></label>
          <label>Address line 2<input name="address_line_2" defaultValue={company.address_line_2 || ""}/></label>
          <label>City<input name="city" defaultValue={company.city} required/></label>
        </div>
      </section>
      <section className="settingsSection">
        <div className="settingsTitle"><Landmark/><div><h2>Estimate settings</h2><p>Currency and tax applied to damage estimates.</p></div></div>
        <div className="formGrid">
          <label>Currency code<input name="currency_code" maxLength={3} defaultValue={company.currency_code} required/></label>
          <label>Tax label<input name="tax_label" defaultValue={company.tax_label} required/></label>
          <label>Tax rate (%)<input name="tax_rate" type="number" min="0" max="100" step=".01" defaultValue={company.tax_rate * 100} required/></label>
        </div>
      </section>
      <section className="settingsSection">
        <div className="settingsTitle"><FileText/><div><h2>Report footer</h2><p>Statement printed at the end of generated PDFs.</p></div></div>
        <label>Footer text<textarea name="report_footer" defaultValue={company.report_footer || ""}/></label>
      </section>
      {error && <div className="alert error">{error}</div>}
      <div className="settingsActions"><button className="primary" disabled={saving}>{saving ? "Saving settings…" : "Save company settings"}</button></div>
    </form>
  </>;
}
