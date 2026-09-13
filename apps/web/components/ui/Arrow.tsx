export function Arrow({ direction = "right" }: { direction?: "right" | "up" }) {
  return <span className="arrow" aria-hidden="true">{direction === "up" ? "↗" : "→"}</span>;
}
