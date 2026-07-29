"use client";
import {useEffect, useState} from "react";
import {api} from "@/lib/api";
import {Heading} from "@/components/PageParts";

export default function Dashboard() {
  const [data, setData] = useState<Record<string, unknown>>({});
  useEffect(() => { api<Record<string, unknown>>("/api/dashboard").then(setData).catch(() => null); }, []);
  const values = Object.entries(data).filter(([k, v]) => k !== "role" && ["number", "string"].includes(typeof v)).slice(0, 6);
  return <><Heading eyebrow="OVERVIEW" title={data.role === "customer" ? "Your vehicles and reports" : "Claims overview"} description={data.role === "customer" ? "Review completed assessments and available reports." : "Current records and assessment activity."}/>
    <section className="metricGrid">{values.map(([key, value]) => <article className="metric" key={key}><span>{key.replaceAll("_", " ")}</span><strong>{String(value)}</strong></article>)}</section>
    <section className="panel"><div><p className="eyebrow">WORK QUEUE</p><h2>{data.role === "customer" ? "Your latest records" : "Continue claims work"}</h2></div><p className="muted">Use the navigation to open vehicles, assessments and issued reports.</p></section>
  </>;
}
