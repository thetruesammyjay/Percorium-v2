type BadgeProps = { children: React.ReactNode; tone?: "neutral" | "blue" | "yellow" | "violet" | "mint" };

export function Badge({ children, tone = "neutral" }: BadgeProps) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
