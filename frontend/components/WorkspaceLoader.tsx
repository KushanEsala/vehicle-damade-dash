import {ShieldCheck} from "lucide-react";

export default function WorkspaceLoader({label = "Preparing your workspace"}: {label?: string}) {
  return (
    <div className="workspaceLoader" role="status" aria-live="polite" aria-label={label}>
      <div className="loaderGlow" aria-hidden="true"/>
      <div className="loaderMark" aria-hidden="true">
        <span className="loaderOrbit orbitOne"/>
        <span className="loaderOrbit orbitTwo"/>
        <span className="loaderShield"><ShieldCheck size={30}/></span>
      </div>
      <div className="loaderCopy">
        <strong>APEX ASSURANCE</strong>
        <span>{label}</span>
      </div>
      <div className="loaderTrack" aria-hidden="true"><span/></div>
    </div>
  );
}
