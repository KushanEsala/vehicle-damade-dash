export function Heading({eyebrow, title, description}: {eyebrow: string; title: string; description: string}) {
  return <header className="pageHeading"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{description}</p></header>;
}
export function Empty({title, text}: {title: string; text: string}) {
  return <div className="empty"><h3>{title}</h3><p>{text}</p></div>;
}
export function Money({value, currency = "LKR"}: {value: number; currency?: string}) {
  return <>{new Intl.NumberFormat("en-LK", {style: "currency", currency, maximumFractionDigits: 0}).format(value)}</>;
}
