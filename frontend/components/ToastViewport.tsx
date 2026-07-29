"use client";

import {useEffect, useState} from "react";
import {CheckCircle2, CircleAlert, X} from "lucide-react";

type Toast = {id: number; type: "success" | "error"; message: string};

export default function ToastViewport() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  useEffect(() => {
    function receive(event: Event) {
      const detail = (event as CustomEvent<Omit<Toast, "id">>).detail;
      const id = Date.now() + Math.random();
      setToasts(current => [...current.slice(-2), {...detail, id}]);
      window.setTimeout(() => setToasts(current => current.filter(toast => toast.id !== id)), 4200);
    }
    window.addEventListener("apex:toast", receive);
    return () => window.removeEventListener("apex:toast", receive);
  }, []);

  return <div className="toastViewport" aria-live="polite" aria-atomic="false">
    {toasts.map(toast => <div className={`toast ${toast.type}`} role={toast.type === "error" ? "alert" : "status"} key={toast.id}>
      {toast.type === "success" ? <CheckCircle2/> : <CircleAlert/>}
      <span>{toast.message}</span>
      <button aria-label="Dismiss notification" onClick={() => setToasts(current => current.filter(item => item.id !== toast.id))}><X/></button>
    </div>)}
  </div>;
}
