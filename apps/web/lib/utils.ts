export function shortenAddress(address: string, edge = 4) {
  return address.length > edge * 2 + 3 ? address.slice(0, edge) + "…" + address.slice(-edge) : address;
}

export function toAtomicAmount(value: string, decimals: number): string | null {
  const normalized = value.trim();
  if (!/^(?:\d+(?:\.\d*)?|\.\d+)$/.test(normalized)) return null;
  const [wholePart, fractionPart = ""] = normalized.split(".");
  if (fractionPart.length > decimals && /[1-9]/.test(fractionPart.slice(decimals))) return null;
  const whole = (wholePart || "0").replace(/^0+(?=\d)/, "");
  const fraction = fractionPart.padEnd(decimals, "0").slice(0, decimals);
  const atomic = BigInt(whole + fraction);
  return atomic > BigInt(0) ? atomic.toString() : null;
}

export function formatAtomicAmount(value: string | null | undefined, decimals: number) {
  if (!value) return "—";
  try {
    const raw = BigInt(value).toString().padStart(decimals + 1, "0");
    const whole = raw.slice(0, -decimals) || "0";
    const fraction = raw.slice(-decimals).replace(/0+$/, "");
    return fraction ? whole + "." + fraction : whole;
  } catch {
    return "—";
  }
}

export function decodeBase64(value: string): Uint8Array {
  const binary = window.atob(value);
  return Uint8Array.from(binary, (character) => character.charCodeAt(0));
}

export function encodeBase58(bytes: Uint8Array): string {
  const alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
  let value = BigInt(0);
  for (const byte of bytes) value = value * BigInt(256) + BigInt(byte);
  let encoded = "";
  while (value > BigInt(0)) {
    const remainder = Number(value % BigInt(58));
    encoded = alphabet[remainder] + encoded;
    value /= BigInt(58);
  }
  for (const byte of bytes) {
    if (byte !== 0) break;
    encoded = "1" + encoded;
  }
  return encoded || "1";
}