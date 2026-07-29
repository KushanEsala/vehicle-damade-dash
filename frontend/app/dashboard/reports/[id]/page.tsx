"use client";

import {useEffect, useState} from "react";
import {useParams} from "next/navigation";
import {Download, ExternalLink} from "lucide-react";
import {api, API_URL} from "@/lib/api";
import {Heading, Money} from "@/components/PageParts";

type Damage = {
  id: number; final_damage_class: string; vehicle_part: string; severity: string;
  confidence: number | null; description: string; estimated_cost: number;
};
type Detail = {
  id: number; report_number: string; analysis_number: string; generated_at: string; role_scope: string;
  customer: {full_name: string; customer_code: string};
  vehicle: {registration_number: string; make: string; model: string; manufactured_year: number; colour: string};
  damages: Damage[]; totals: {subtotal: number; tax: number; discount: number; total: number};
  currency_code: string; annotated_image_url: string | null; pdf_view_url: string; pdf_download_url: string;
};

export default function ReportDetail() {
  const {id} = useParams<{id: string}>();
  const [report, setReport] = useState<Detail | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { api<Detail>(`/api/reports/${id}`).then(setReport).catch(e => setError(e.message)); }, [id]);
  if (!report) return <div className="loadingScreen">{error || "Loading report…"}</div>;
  return <><Heading eyebrow={report.report_number} title={`${report.vehicle.registration_number} damage report`}
    description={`${report.customer.full_name} · ${report.vehicle.make} ${report.vehicle.model} · ${new Date(report.generated_at).toLocaleDateString()}`}/>
    <div className="reportToolbar">
      <a className="secondary" href={`${API_URL}${report.pdf_view_url}`} target="_blank"><ExternalLink size={17}/>Open printable report</a>
      <a className="primary" href={`${API_URL}${report.pdf_download_url}`}><Download size={17}/>Download PDF</a>
    </div>
    <section className="reportSummary">
      <div className="reportImage">{report.annotated_image_url
        ? <img src={`${API_URL}${report.annotated_image_url}`} alt={`Marked damage on ${report.vehicle.registration_number}`}/>
        : <div className="empty">Marked damage image unavailable</div>}</div>
      <div className="estimateBlock"><span>Total estimated repair cost</span><strong><Money value={report.totals.total} currency={report.currency_code}/></strong>
        <dl><div><dt>Subtotal</dt><dd><Money value={report.totals.subtotal} currency={report.currency_code}/></dd></div>
          <div><dt>Tax</dt><dd><Money value={report.totals.tax} currency={report.currency_code}/></dd></div>
          <div><dt>Discount</dt><dd><Money value={report.totals.discount} currency={report.currency_code}/></dd></div></dl>
      </div>
    </section>
    <section className="panel tablePanel"><h2>Confirmed damage and costs</h2><div className="tableWrap"><table><thead><tr><th>Damage</th><th>Vehicle part</th><th>Severity</th><th>Confidence</th><th>Description</th><th>Cost</th></tr></thead>
      <tbody>{report.damages.map(damage => <tr key={damage.id}><td><strong>{damage.final_damage_class.replaceAll("_", " ")}</strong></td><td>{damage.vehicle_part}</td><td><span className="status">{damage.severity}</span></td><td>{damage.confidence == null ? "Manual" : `${Math.round(damage.confidence * 100)}%`}</td><td>{damage.description || "—"}</td><td><strong><Money value={damage.estimated_cost} currency={report.currency_code}/></strong></td></tr>)}</tbody>
    </table></div></section>
    <section className="panel pdfPanel"><div className="pdfPanelHead"><div><p className="eyebrow">PRINT PREVIEW</p><h2>Report document</h2></div><a className="secondary" href={`${API_URL}${report.pdf_download_url}`}><Download size={17}/>Download</a></div>
      <iframe title={`PDF ${report.report_number}`} src={`${API_URL}${report.pdf_view_url}`}/></section>
  </>;
}
