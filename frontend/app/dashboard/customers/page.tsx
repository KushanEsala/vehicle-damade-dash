"use client";
import {FormEvent, useEffect, useState} from "react";
import {api} from "@/lib/api";
import {Heading, Empty} from "@/components/PageParts";

type Customer = {id:number; customer_code:string; full_name:string; phone_primary:string; email:string; city:string; portal_account:boolean};
export default function Customers() {
  const [rows,setRows]=useState<Customer[]>([]); const [message,setMessage]=useState("");
  const load=()=>api<Customer[]>("/api/customers").then(setRows).catch(e=>setMessage(e.message));
  useEffect(()=>{void load()},[]);
  async function submit(e:FormEvent<HTMLFormElement>){e.preventDefault(); const fd=new FormData(e.currentTarget);
    try { const r=await api<{username:string;temporary_password:string}>("/api/customers",{method:"POST",body:JSON.stringify(Object.fromEntries(fd))}); setMessage(`Customer saved. Username: ${r.username} · Temporary password: ${r.temporary_password}`); e.currentTarget.reset(); load(); } catch(err){setMessage(err instanceof Error?err.message:"Unable to save customer.");}}
  return <><Heading eyebrow="CUSTOMERS" title="Customer records" description="Register policyholders and issue their portal access."/>
    <section className="panel"><h2>Register customer</h2><form className="formGrid" onSubmit={submit}>
      <label>Full name<input name="full_name" required/></label><label>Email<input name="email" type="email" required/></label>
      <label>Primary phone<input name="phone_primary" required/></label><label>NIC or passport<input name="nic_or_passport"/></label>
      <label>Address<input name="address_line_1" required/></label><label>City<input name="city" required/></label>
      <button className="primary">Create customer account</button></form>{message&&<div className="alert">{message}</div>}</section>
    <section className="panel tablePanel"><h2>Registered customers</h2>{rows.length?<div className="tableWrap"><table><thead><tr><th>Customer</th><th>Contact</th><th>City</th><th>Portal</th></tr></thead><tbody>{rows.map(r=><tr key={r.id}><td><strong>{r.full_name}</strong><small>{r.customer_code}</small></td><td>{r.phone_primary}<small>{r.email}</small></td><td>{r.city}</td><td><span className={`status ${r.portal_account?"ok":""}`}>{r.portal_account?"Active":"Not issued"}</span></td></tr>)}</tbody></table></div>:<Empty title="No customers yet" text="Register the first customer above."/>}</section></>;
}
