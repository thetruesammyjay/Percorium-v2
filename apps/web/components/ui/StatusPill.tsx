import { StateIcon } from "@/components/brand/StateIcon";

type Status = "success" | "warning" | "blocked" | "pending";
export function StatusPill({ status, children }: { status: Status; children: React.ReactNode }) {
  return <span className={`status status-${status}`}><StateIcon state={status} size={18} />{children}</span>;
}