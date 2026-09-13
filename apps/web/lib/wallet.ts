export type WalletState = { connected: boolean; address?: string; provider?: "privy" | "phantom" | "backpack" };

// Privy and wallet-adapter wiring is intentionally isolated here for the first integration pass.
export const initialWalletState: WalletState = { connected: false };
