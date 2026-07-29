"use client";

import {ChangeEvent, FormEvent, useEffect, useMemo, useState} from "react";
import {useRouter} from "next/navigation";
import {ScanLine, Upload} from "lucide-react";
import {api} from "@/lib/api";
import {Heading} from "@/components/PageParts";

type Customer = {id: number; customer_code: string; full_name: string};
type Vehicle = {id: number; customer_id: number; registration_number: string; make: string; model: string};

export default function NewAssessment() {
  const router = useRouter();
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [customerId, setCustomerId] = useState("");
  const [vehicleId, setVehicleId] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const [damageConfidence, setDamageConfidence] = useState(0.30);
  const [vehicleConfidence, setVehicleConfidence] = useState(0.25);
  const [imagePreview, setImagePreview] = useState("");
  const [imageName, setImageName] = useState("");
  const [processingStep, setProcessingStep] = useState(0);

  const processingMessages = [
    "Checking vehicle context",
    "Locating visible damage",
    "Measuring detection confidence",
    "Cross-checking detected regions",
    "Preparing the assessment results",
  ];

  useEffect(() => {
    Promise.all([
      api<Customer[]>("/api/customers"),
      api<Vehicle[]>("/api/vehicles"),
    ]).then(([customerRows, vehicleRows]) => {
      setCustomers(customerRows);
      setVehicles(vehicleRows);
    }).catch(error => setMessage(error.message));
  }, []);

  useEffect(() => {
    if (!busy) {
      setProcessingStep(0);
      return;
    }
    const timer = window.setInterval(
      () => setProcessingStep(step => (step + 1) % processingMessages.length),
      1800,
    );
    return () => window.clearInterval(timer);
  }, [busy, processingMessages.length]);

  useEffect(() => () => {
    if (imagePreview) URL.revokeObjectURL(imagePreview);
  }, [imagePreview]);

  const customerVehicles = useMemo(
    () => vehicles.filter(vehicle => vehicle.customer_id === Number(customerId)),
    [customerId, vehicles],
  );

  function changeCustomer(value: string) {
    setCustomerId(value);
    setVehicleId("");
    setMessage("");
  }

  function selectImage(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (imagePreview) URL.revokeObjectURL(imagePreview);
    if (!file) {
      setImagePreview("");
      setImageName("");
      return;
    }
    setImagePreview(URL.createObjectURL(file));
    setImageName(file.name);
  }

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    const form = new FormData(event.currentTarget);
    form.set("require_vehicle", "true");
    try {
      const result = await api<
        {accepted: false; message: string} | {id: number}
      >("/api/analyses", {method: "POST", body: form});
      if (!("id" in result)) {
        setMessage(result.message || "Please attach a vehicle image.");
        return;
      }
      router.push(`/dashboard/assessments/${result.id}`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Assessment failed.");
    } finally {
      setBusy(false);
    }
  }

  return <><Heading eyebrow="NEW ASSESSMENT" title="Inspect vehicle damage"
    description="Select the customer and registered vehicle, then upload one clear damage image."/>
    <section className="analysisLayout">
      <form className="panel analysisForm" onSubmit={submit}>
        <div className="iconTile"><ScanLine/></div>
        <div className="assessmentSelectors">
          <label>Customer
            <select value={customerId} onChange={event => changeCustomer(event.target.value)} required>
              <option value="">Select customer</option>
              {customers.map(customer =>
                <option value={customer.id} key={customer.id}>{customer.full_name} · {customer.customer_code}</option>
              )}
            </select>
          </label>
          <label>Registered vehicle
            <select name="vehicle_id" value={vehicleId} onChange={event => setVehicleId(event.target.value)}
              disabled={!customerId || customerVehicles.length === 0} required>
              <option value="">{!customerId ? "Select a customer first" :
                customerVehicles.length === 0 ? "No vehicles registered for this customer" : "Select vehicle"}</option>
              {customerVehicles.map(vehicle =>
                <option value={vehicle.id} key={vehicle.id}>{vehicle.registration_number} · {vehicle.make} {vehicle.model}</option>
              )}
            </select>
          </label>
        </div>
        {customerId && customerVehicles.length === 0 &&
          <div className="alert">This customer has no registered vehicles. Register a vehicle before starting an assessment.</div>}
        <label className={`dropzone ${imagePreview ? "hasPreview" : ""}`}>
          {imagePreview
            ? <><img src={imagePreview} alt="Selected vehicle damage preview"/><span className="previewMeta"><strong>{imageName}</strong><small>Click to replace image</small></span></>
            : <><Upload/><strong>Choose vehicle image</strong><span>JPG, PNG or WEBP</span></>}
          <input name="image" type="file" accept="image/jpeg,image/png,image/webp" required disabled={!vehicleId}
            onChange={selectImage}/>
        </label>
        <div className="confidenceGrid">
          <label className="rangeField"><span>Damage confidence <output>{Math.round(damageConfidence * 100)}%</output></span>
            <input name="damage_confidence" type="range" min=".05" max=".95" step=".05"
              value={damageConfidence} onChange={event => setDamageConfidence(Number(event.target.value))}/>
            <small>Minimum confidence required for a damage finding.</small>
          </label>
          <label className="rangeField"><span>Vehicle confidence <output>{Math.round(vehicleConfidence * 100)}%</output></span>
            <input name="vehicle_confidence" type="range" min=".05" max=".95" step=".05"
              value={vehicleConfidence} onChange={event => setVehicleConfidence(Number(event.target.value))}/>
            <small>Minimum confidence required to confirm the vehicle.</small>
          </label>
        </div>
        {message && <div className="alert error">{message}</div>}
        {busy && <div className="processingPanel" role="status" aria-live="polite">
          <div className="processingText"><span>Generating results</span><strong>“{processingMessages[processingStep]}”</strong></div>
          <div className="processingTrack" aria-hidden="true"><span/></div>
          <small>Keep this page open while the image is processed.</small>
        </div>}
        <button className="primary" disabled={busy || !customerId || !vehicleId || !imagePreview}>
          {busy ? "Analyzing image…" : "Analyze damage"}
        </button>
      </form>
      <aside className="notePanel"><h3>Image checklist</h3><ol>
        <li>Keep the damaged area in focus.</li>
        <li>Include enough vehicle body for confirmation.</li>
        <li>Avoid screenshots, heavy filters and extreme crops.</li>
      </ol><p>The result must be reviewed before a report is issued.</p></aside>
    </section>
  </>;
}
