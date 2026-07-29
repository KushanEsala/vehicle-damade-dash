"use client";

import Link from "next/link";
import {useEffect, useState} from "react";
import {Download, Eye} from "lucide-react";
import {api, API_URL} from "@/lib/api";
import {Heading, Empty, Money} from "@/components/PageParts";

type Report = {
  id: number; report_number: string; analysis_number: string; registration_number: string;
  generated_at: string; total_estimated_cost: number; currency_code: string; customer_name: string | null;
};
type ReportResponse = {scope: "company" | "assigned_operations" | "customer"; reports: Report[]};

export default function Reports() {
  const [data, setData] = useState<ReportResponse>({scope: "customer", reports: []});
  useEffect(() => { api<ReportResponse>("/api/reports").then(setData).catch(() => null); }, []);
  const title = data.scope === "company" ? "Company damage reports" : data.scope === "customer" ? "My damage reports" : "Assessment reports";
  const description = data.scope === "company"
    ? "All finalized reports across the company."
    : data.scope === "customer" ? "Reports issued for your registered vehicles." : "Finalized reports available to claims operators.";
  return <><Heading eyebrow="REPORTS" title={title} description={description}/>
    <section className="cardGrid">{data.reports.map(report => <article className="reportCard" key={report.id}>
      <p className="eyebrow">{report.report_number}</p><h3>{report.registration_number}</h3>
      {report.customer_name && <p>{report.customer_name}</p>}<p>{report.analysis_number}</p>
      <strong><Money value={report.total_estimated_cost} currency={report.currency_code}/></strong>
      <div className="reportActions">
        <Link className="primary" href={`/dashboard/reports/${report.id}`}><Eye size={17}/>View report</Link>
        <a className="secondary" href={`${API_URL}/api/reports/${report.id}/download`}><Download size={17}/>Download</a>
      </div>
    </article>)}</section>
    {!data.reports.length && <Empty title="No reports available" text="A report is created when an assessment is finalized."/>}
  </>;
}
