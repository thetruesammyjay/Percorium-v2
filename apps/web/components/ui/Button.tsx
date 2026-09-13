import Link from "next/link";

type ButtonProps = { children: React.ReactNode; href?: string; variant?: "primary" | "secondary" };

export function Button({ children, href, variant = "primary" }: ButtonProps) {
  const className = `button button-${variant}`;
  return href ? <Link className={className} href={href}>{children}</Link> : <button className={className}>{children}</button>;
}
