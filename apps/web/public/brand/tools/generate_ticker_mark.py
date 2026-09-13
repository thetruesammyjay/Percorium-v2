#!/usr/bin/env python3
# Generate flat Percorium ticker monogram SVGs.
# Usage: python tools/generate_ticker_mark.py AAPL stock public/brand/assets/generated/AAPL.svg
import sys, html
COLORS=["#4da2ff","#55db9c","#ffd731","#fb4903","#5c4ade","#e9ccff"]

def stable_color(ticker):
    return COLORS[sum(map(ord,ticker.upper())) % len(COLORS)]

def main():
    if len(sys.argv) < 4:
        raise SystemExit("usage: generate_ticker_mark.py TICKER stock|etf OUTPUT.svg")
    ticker, typ, out = sys.argv[1].upper(), sys.argv[2].lower(), sys.argv[3]
    color=stable_color(ticker)
    fs=24 if len(ticker)<=3 else 19 if len(ticker)==4 else 15
    marker = '<path d="M10 51H26" stroke="#000" stroke-width="3.5" stroke-linecap="round"/>' if typ=='stock' else '<circle cx="18" cy="51" r="3" fill="#fff"/><circle cx="27" cy="51" r="3" fill="#fff"/>'
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="{html.escape(ticker)} {html.escape(typ)} mark">
<rect x="3" y="3" width="58" height="58" rx="17" fill="{color}" stroke="#000" stroke-width="3"/>
<text x="32" y="39" text-anchor="middle" font-family="Inter,Arial,sans-serif" font-size="{fs}" font-weight="900" fill="#fff">{html.escape(ticker)}</text>
{marker}
</svg>'''
    open(out,'w',encoding='utf-8').write(svg)

if __name__=='__main__': main()
