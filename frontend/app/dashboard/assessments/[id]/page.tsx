"use client";

import {FormEvent, useEffect, useState} from "react";
import {useParams, useRouter} from "next/navigation";
import {CalendarDays, CarFront, CheckCircle2, FileSearch, RotateCcw, ShieldAlert, Trash2, X} from "lucide-react";
import {api, API_URL, User} from "@/lib/api";
import {Heading, Money} from "@/components/PageParts";

type Damage = {
  id: number; damage_class: string; vehicle_part: string; severity: string;
  confidence: number | null; description: string; estimated_cost: number; review_status: string;
};
type Assessment = {
  id: number; analysis_number: string; registration_number: string; vehicle_name: string;
  status: string; vehicle_confirmed: boolean; accepted_damage_count: number; currency_code: string;
  damage_confidence: number; vehicle_confidence: number; require_vehicle_confirmation: boolean;
  subtotal_cost: number; tax_amount: number; total_estimated_cost: number; analyzed_at: string;
  finalized_at: string | null; annotated_image_url: string | null; damages: Damage[];
};

export default function AssessmentReview() {
  const {id} = useParams<{id: string}>();
  const router = useRouter();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [error, setError] = useState("");
  const [savingId, setSavingId] = useState<number | null>(null);
  const [deletingId, setDeletingId] = useState<number | null>(null);
  const [finalizing, setFinalizing] = useState(false);
  const [showReanalysis, setShowReanalysis] = useState(false);
  const [reanalyzing, setReanalyzing] = useState(false);
  const [newDamageConfidence, setNewDamageConfidence] = useState(0.30);
  const [newVehicleConfidence, setNewVehicleConfidence] = useState(0.25);

  const loadAssessment = () => api<Assessment>(`/api/analyses/${id}`).then(setAssessment);
  useEffect(() => {
    Promise.all([
      loadAssessment(),
      api<{user: User}>("/api/auth/session").then(result => setUser(result.user)),
    ]).catch(reason => setError(reason.message));
  }, [id]);

  if (!assessment) return <div className="loadingScreen">{error || "Loading assessment record…"}</div>;
  const canEdit = user?.role !== "customer" && ["analyzed", "under_review"].includes(assessment.status);

  async function saveCost(event: FormEvent<HTMLFormElement>, damage: Damage) {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget));
    setSavingId(damage.id);
    try {
      await api(`/api/analyses/${id}/damages/${damage.id}`, {
        method: "PATCH",
        body: JSON.stringify({
          final_class: String(values.final_class || damage.damage_class),
          vehicle_part: String(values.vehicle_part || damage.vehicle_part || "General panel"),
          severity: String(values.severity || damage.severity),
          description: String(values.description || ""),
          estimated_cost: Number(values.estimated_cost),
        }),
      });
      await loadAssessment();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The repair estimate could not be saved.");
    } finally {
      setSavingId(null);
    }
  }

  async function finalizeAssessment() {
    setFinalizing(true);
    try {
      await api(`/api/analyses/${id}/finalize`, {
        method: "POST",
        body: JSON.stringify({notes: "Damage findings and repair estimates reviewed."}),
      });
      await loadAssessment();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The report could not be finalized.");
    } finally {
      setFinalizing(false);
    }
  }

  async function deleteFinding(damage: Damage) {
    if (!window.confirm(`Delete the "${damage.damage_class.replaceAll("_", " ")}" finding? The marked image and totals will be updated.`)) return;
    setDeletingId(damage.id);
    setError("");
    try {
      await api(`/api/analyses/${id}/damages/${damage.id}`, {method: "DELETE"});
      await loadAssessment();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The damage finding could not be deleted.");
    } finally {
      setDeletingId(null);
    }
  }

  function openReanalysis() {
    if (!assessment) return;
    setNewDamageConfidence(assessment.damage_confidence);
    setNewVehicleConfidence(assessment.vehicle_confidence);
    setShowReanalysis(true);
  }

  async function runReanalysis(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget));
    setReanalyzing(true);
    setError("");
    try {
      const replacement = await api<Assessment>(`/api/analyses/${id}/reanalyze`, {
        method: "POST",
        body: JSON.stringify({
          damage_confidence: newDamageConfidence,
          vehicle_confidence: newVehicleConfidence,
          require_vehicle: values.require_vehicle === "on",
          reason: String(values.reason),
        }),
      });
      router.replace(`/dashboard/assessments/${replacement.id}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The assessment could not be rerun.");
    } finally {
      setReanalyzing(false);
    }
  }

  return <><Heading eyebrow="ASSESSMENT REVIEW" title={assessment.analysis_number}
    description={canEdit ? "Review detected damage, enter repair estimates and finalize the report." : "Completed inspection record and confirmed repair estimates."}/>
    {error && <div className="alert error">{error}</div>}

    <section className="reviewHeader">
      <div className="reviewIdentity">
        <div className="reviewIcon"><FileSearch/></div>
        <div><span>Vehicle</span><h2>{assessment.registration_number}</h2><p>{assessment.vehicle_name}</p></div>
      </div>
      <div className="reviewMeta">
        <span className={`status ${assessment.vehicle_confirmed ? "ok" : ""}`}>
          {assessment.vehicle_confirmed ? <CheckCircle2/> : <ShieldAlert/>}
          {assessment.vehicle_confirmed ? "Vehicle confirmed" : "Confirmation required"}
        </span>
        <span className={`status ${assessment.status === "finalized" ? "ok" : ""}`}>{assessment.status}</span>
        {canEdit && <button className="secondary" onClick={openReanalysis}><RotateCcw/>Reanalyze</button>}
        {canEdit && <button className="primary" onClick={finalizeAssessment} disabled={finalizing}>
          {finalizing ? "Finalizing…" : "Finalize report"}
        </button>}
      </div>
    </section>

    {showReanalysis && <section className="reanalysisPanel">
      <div className="reanalysisHead"><div><p className="eyebrow">RUN AGAIN</p><h2>Adjust detection thresholds</h2>
        <p>The original uploaded image will be processed again from the beginning. This assessment will remain in history as superseded.</p></div>
        <button className="iconButton" onClick={() => setShowReanalysis(false)} aria-label="Close reanalysis settings"><X/></button></div>
      <form onSubmit={runReanalysis}>
        <div className="confidenceGrid">
          <label className="rangeField"><span>Damage confidence <output>{Math.round(newDamageConfidence * 100)}%</output></span>
            <input type="range" min=".05" max=".95" step=".05" value={newDamageConfidence}
              onChange={event => setNewDamageConfidence(Number(event.target.value))}/>
            <small>Higher values remove uncertain damage findings.</small>
          </label>
          <label className="rangeField"><span>Vehicle confidence <output>{Math.round(newVehicleConfidence * 100)}%</output></span>
            <input type="range" min=".05" max=".95" step=".05" value={newVehicleConfidence}
              onChange={event => setNewVehicleConfidence(Number(event.target.value))}/>
            <small>Higher values require stronger vehicle confirmation.</small>
          </label>
        </div>
        <label>Reason for reanalysis<input name="reason" defaultValue="Confidence thresholds adjusted before finalization." required minLength={5}/></label>
        <label className="checkField"><input name="require_vehicle" type="checkbox"
          defaultChecked={assessment.require_vehicle_confirmation}/>Require vehicle confirmation</label>
        {reanalyzing && <div className="processingPanel"><div className="processingText"><span>Reanalyzing original image</span>
          <strong>“Generating revised findings”</strong></div><div className="processingTrack"><span/></div></div>}
        <div className="editorActions"><button type="button" className="secondary" onClick={() => setShowReanalysis(false)}>Cancel</button>
          <button className="primary" disabled={reanalyzing}>{reanalyzing ? "Running full analysis…" : "Run full analysis again"}</button></div>
      </form>
    </section>}

    <section className="reviewStats">
      <article><CarFront/><span>Accepted damage</span><strong>{assessment.accepted_damage_count}</strong></article>
      <article><CalendarDays/><span>Analyzed</span><strong>{new Date(assessment.analyzed_at).toLocaleDateString()}</strong></article>
      <article><span>Subtotal</span><strong><Money value={assessment.subtotal_cost} currency={assessment.currency_code}/></strong></article>
      <article className="reviewTotal"><span>Total estimate</span><strong><Money value={assessment.total_estimated_cost} currency={assessment.currency_code}/></strong></article>
    </section>

    <section className="reviewImagePanel">
      <div className="reviewSectionTitle"><p className="eyebrow">INSPECTION IMAGE</p><h2>Marked damage areas</h2></div>
      {assessment.annotated_image_url
        ? <img src={`${API_URL}${assessment.annotated_image_url}`} alt={`Marked damage on ${assessment.registration_number}`}/>
        : <div className="empty">No marked inspection image is available.</div>}
    </section>

    <section className="panel tablePanel reviewFindings">
      <div className="reviewSectionTitle"><p className="eyebrow">VERIFIED FINDINGS</p><h2>Damage summary</h2></div>
      <div className="reviewDamageGrid">{assessment.damages.map(damage =>
        <form className="reviewDamageRow" key={damage.id} onSubmit={event => saveCost(event, damage)}>
          <div className="reviewDamageName">
            <label className="partField">Damage finding
              <input name="final_class" defaultValue={damage.damage_class.replaceAll("_", " ")} disabled={!canEdit}/>
            </label>
            <label className="partField">Vehicle part
              <input name="vehicle_part" defaultValue={damage.vehicle_part || "General panel"} disabled={!canEdit}/>
            </label>
          </div>
          <label className="compactReviewField">Severity
            <select name="severity" defaultValue={damage.severity} disabled={!canEdit}>
              <option value="minor">Minor</option>
              <option value="moderate">Moderate</option>
              <option value="severe">Severe</option>
            </select>
          </label>
          <div><small>Confidence</small><strong>{damage.confidence == null ? "Manual" : `${Math.round(damage.confidence * 100)}%`}</strong></div>
          <label className="reviewDescription">Description
            <textarea name="description" defaultValue={damage.description || ""} disabled={!canEdit}
              placeholder="Describe the visible damage"/>
          </label>
          <label className="costField">Repair estimate
            <span><b>{assessment.currency_code}</b><input name="estimated_cost" type="number" min="0" step="0.01"
              defaultValue={damage.estimated_cost} disabled={!canEdit}/></span>
          </label>
          {canEdit && <div className="findingActions">
            <button className="secondary" disabled={savingId === damage.id || deletingId === damage.id}>
              {savingId === damage.id ? "Saving…" : "Save changes"}
            </button>
            <button type="button" className="dangerButton" disabled={savingId === damage.id || deletingId === damage.id}
              onClick={() => deleteFinding(damage)}><Trash2/>{deletingId === damage.id ? "Deleting…" : "Delete"}</button>
          </div>}
        </form>)}</div>
    </section>

    <p className="readOnlyNotice">{canEdit
      ? "Enter and save each repair estimate before finalizing the report."
      : "This assessment is finalized. Its confirmed values are locked."}</p>
  </>;
}
