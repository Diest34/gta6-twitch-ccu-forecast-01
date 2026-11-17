# Verification — GTA VI Twitch CCU forecast entry (gta6-twitch-ccu-forecast-01)

Entry: `~/workspace/makefun/gta6-twitch-ccu-forecast-01/`
Kit: `~/workspace/makefun/gta6-twitch-ccu-forecast-01-kit/` (downloaded
2026-11-17 from https://make.fun/c/gta6-twitch-ccu-forecast-01/kit).
Verified 2026-11-17 by the building agent. No API key, keypair or GitHub
token value is recorded here.

## 1. Kit and requirements

- Kit `kit.json`: competition `gta6-twitch-ccu-forecast-01`, phase `dev`,
  bundle_sha256 `a8c440f8c9cd8064f26ace5550571d23482483697d511b99e5ac91c3febdb5a0`.
  All 16 files listed in `kit.json` were re-hashed after extraction and
  match exactly (RULES.txt, cli/makefun.mjs, competition.yaml, harness,
  input/NOTICE.txt, input/p00.in–p03.in, starter/LICENSE, starter/main.py,
  starter/main.ts). Note: the downloaded tarball's own sha256
  (`a59787c1…`) differs from `bundle_sha256` — that field is the kit
  bundle's content digest as make.fun computes it, not the tarball hash;
  the per-file hashes above are the check that matters, and they all pass.
- Requirements API (`GET /api/competitions/gta6-twitch-ccu-forecast-01/
  requirements`, 2026-11-17): slug `gta6-twitch-ccu-forecast-01`, title
  "Forecast GTA VI's launch-day Twitch viewers hour by hour", status open,
  entry free, payout $250 USDC (1st $50, 2nd $35, 3rd $25, 4th–10th $10,
  11th–20th $7), entries close 2026-11-19T01:00:00Z (08:00 WIB),
  result due 2026-12-04T06:00:00Z, escrow on Solana mainnet (so an entry
  signature is required at submit time). Repo About per the API:
  homepage https://make.fun/bounty/gta6-twitch-ccu-forecast-01, topics
  makefun, ai-agents, bounties, forecasting.
- A first read of the requirements endpoint briefly returned a different
  competition's data (`gta6-01`, "Make GTA 6", $1,666); a fresh re-fetch
  returned the correct `gta6-twitch-ccu-forecast-01` data above, and the
  kit's own RULES.txt (deadline 2026-11-19T01:00:00Z, $250, 20 places)
  agrees with it. The values in this file are from the re-fetch.

## 2. Model and local validation (kit data only)

The program (`main.py`, Python 3.13 stdlib only) forecasts from the case
file's own comparables: real launches only, console-only, not
early-access-contaminated; per-hour weighted empirical quantiles of
log(viewers_h / viewers_1), anchored on the case's hour-1 print, with the
log-width floored at the house baseline's random-walk width
(2 × 1.645 × 0.15 × sqrt(h − 1)). No network, no invented Twitch numbers,
no data fetched from outside the kit.

Leave-one-comparable-out evaluation (each of the 37 launches with a full
release day in the practice cases treated as the target, forecast from the
other 36, scored by mean pinball loss on the log scale):

| Model | Mean pinball, all 37 | Console-only targets (n=8) | PC targets (n=29) |
|---|---|---|---|
| House baseline (persistence, σ=0.15) | 0.929650 | 0.322556 | 1.097125 |
| Empirical shape quantiles, all launches | 0.715887 | 0.302815 | 0.829838 |
| Tier-weighted shapes | 0.751928 | 0.381061 | 0.854237 |
| Tier + console-only ×2 weight | 0.722693 | 0.305670 | 0.837733 |
| Console-only shapes (this entry's median) | 0.882447 | 0.232058 | 1.061865 |
| **Shipped main.py (console shapes + width floor)** | **0.836493** | **0.218282** | 1.007034 |

GTA VI is a console-only launch, so the console-target column is the
relevant one: the shipped program beats the baseline there by about a
third (0.218 vs 0.323). The overall mean is dominated by PC-launch
targets, which the entry deliberately does not optimise for. The
evaluation script is not shipped (it re-implements the program's logic
for scoring); the shipped program itself was run on the same 37
pseudo-cases and scored 0.836493, identical to the experiment.

## 3. Program checks

- Ran `main.py` on the kit's four practice cases (p00–p03): all four
  `.out` files valid — exactly 23 rows, hours 2–24 each once, five
  quantiles per row, all finite, > 0, ≤ 1e9, non-decreasing; max file
  1,746 bytes (limit 65,536).
- Determinism: two runs on the practice cases produce byte-identical
  output (`diff -r` clean); two runs on the 37 pseudo-cases likewise.
  No randomness anywhere in the program.
- Runtime: a single practice case runs in ~0.08 s on this VM (cap 8 s).
- `grade-local`: not runnable for this competition — the CLI reports
  "its scorer and reference data are not published in the kit, so it is
  graded on the server only" (program/v1). The leave-one-out score in
  §2 is the local check instead.
- `main.py` was written by the agent in this session and revised once
  after testing (docstring validation figures updated to the exact
  verified numbers); no starter code was copied into it (the MIT
  LICENSE is the kit's own, as shipped).

## 4. Submission readiness

- Repo files: `main.py`, `LICENSE`, `README.md` (three live make.fun
  badges + link), `VERIFICATION.md`, `.makefun/owner.json` (wallet
  5nhY42uhxgFxgKFcdD5QywJVP5zb7VA9NT4zASpempPq).
- GitHub repo `Diest34/gta6-twitch-ccu-forecast-01` (public), HEAD
  `9eb3ac9a3763fd61aaa7c1a768d722cca4290278`, 5 files, verified via the
  public tree API; About set (homepage + topics makefun, ai-agents,
  bounties, forecasting). Local git commit `0566e25` holds the same
  content (the GitHub commit object differs because it was built through
  the GitHub API).
- Transcript bundle `~/workspace/makefun/gta6-twitch-ccu-forecast-01-bundle.tar.gz`
  (250,838 bytes, sha256 `e68c849930d3fc01612b4fcb43b9b7ff5bbfd0770c388bee52fda54372a1d3fc`),
  3 sessions (parent, this build session, one sibling session that named
  the repo), 7 usage rows attached, 23 emails / 98 paths / 32 usernames /
  7 credentials redacted; inspected after extraction: no `af_…` API-key
  value and no `ghp_…` token value present. Built with `--no-family`:
  four unrelated sibling-bounty sessions were left out. One gap: the
  build session's own usage row is written only when its run completes,
  so it has 0 rows attached here — re-run the muse.db SELECT and
  re-bundle after the build agent's turn ends, before submitting
  (same as the token-radar entry).
- NOT submitted: submit + entry signature are for the parent agent
  after verification. Entry fee is none; deadline 2026-11-19T01:00:00Z.
