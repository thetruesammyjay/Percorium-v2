export function shortenAddress(address: string, edge = 4) {
  return address.length > edge * 2 + 3 ? `${address.slice(0, edge)}…${address.slice(-edge)}` : address;
}
