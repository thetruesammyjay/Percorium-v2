export function DashboardCard({ title, children }: { title: string; children: React.ReactNode }) {
  return <article className="card"><p className="eyebrow">{title}</p>{children}</article>;
}
