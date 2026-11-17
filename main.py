#!/usr/bin/env python3
"""Forecast GTA VI's launch-day Twitch concurrent viewers, hour by hour.

Method (honest, kit data only -- no network, no invented numbers)
------------------------------------------------------------------
Grand Theft Auto VI launches on PlayStation 5 and Xbox Series X|S, unlocks
at midnight local time rolling around the world, single-player, no early
access. The forecast is built from the launch-day shapes of past launches
that look like it, taken from the case file's own `comparables`:

* Only real launches count: the "Grand Theft Auto VI category before
  release" comparable is pre-release hype, not a launch, and is left out.
* Only console-only launches (no PC in `platforms`) -- a PC launch unlocks
  simultaneously worldwide and its day shape is a different animal.
* Early-access-contaminated launches are left out (their release day is
  already half spent when the standard edition unlocks); "weak" tier
  launches count half.

For each comparable launch, take its release UTC day's hourly viewers and
form the shape log(viewers_h / viewers_1) for hours 2..24. For each hour,
the forecast's five quantiles are the weighted empirical quantiles of that
hour's shapes across the library, anchored on the case's own hour-1 print
p1: q_tau(h) = p1 * exp(quantile_tau(h)), rounded to 2 decimals.

One guard against overconfidence: with only 8-12 console launches in the
library, an empirical 5%-95% band can come out narrower than the day's own
noise. So the log-width q95 - q05 is floored at the house baseline's
random-walk width, 2 * 1.645 * 0.15 * sqrt(h - 1), expanded symmetrically
around the band's midpoint when the floor binds.

If the console library ever has fewer than 3 shapes for an hour (it has 8
in the practice cases and 12 in the final, which also holds the four
practice launches), the forecast falls back to the tier-weighted shapes of
all launches, and then to the house baseline's persistence forecast.

Validation (leave-one-comparable-out on the kit's own data, 37 launches):
mean pinball loss on the log scale 0.836493 (house baseline 0.929650); on
the console-only launches -- the ones GTA VI resembles -- 0.218282 against
the baseline's 0.322556. The kit's grade-local does not run for this
competition (program/v1: scorer and reference data are server-only), so
the leave-one-out score above is the local check. See VERIFICATION.md
for the full table and the determinism runs.

Program contract (from the kit's RULES.txt): read every <id>.in in the
input directory ($MAKEFUN_INPUT_DIR, else /input), write one <id>.out per
case to the output directory ($MAKEFUN_OUTPUT_DIR, else /output): exactly
23 rows, hours 2..24, each {"hour": h, "q": [q05, q25, q50, q75, q95]},
finite numbers above 0 and at most 1e9, non-decreasing. Standard library
only, deterministic (no randomness, sorted iteration), well under the
8-second cap.

Run locally:
  mkdir -p out && MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import json
import math
import os
from datetime import datetime

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = [-1.645, -0.674, 0, 0.674, 1.645]
# House baseline's per-root-hour log spread; used only as a width floor.
SIGMA = 0.15
MIN_SHAPES = 3


def parse_time(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def tier_of(comp):
    """'ea' for early-access-contaminated, 'weak' for weak tier, else 'ok'."""
    u = (comp.get("unlock") or "").lower()
    if "early-access-contaminated" in u:
        return "ea"
    if "tier: weak" in u:
        return "weak"
    return "ok"


def is_launch(comp):
    """False for the GTA VI category's own pre-release history."""
    return "before release" not in comp["name"].lower()


def is_console_only(comp):
    return "pc" not in (comp.get("platforms") or "").lower()


def day_hours(comp):
    """{hour: viewers} for the comparable's release UTC day, hours 1..24."""
    start = parse_time(comp["day_start"])
    hours = {}
    for point in comp["hourly"]:
        t = parse_time(point["from"])
        h = int((t - start).total_seconds() // 3600) + 1
        viewers = point.get("viewers")
        if 1 <= h <= 24 and viewers and viewers > 0:
            hours[h] = viewers
    return hours


def weighted_quantile(pairs, tau):
    """Weighted empirical quantile of [(value, weight)], linear interpolation."""
    pairs = sorted(pairs)
    total = sum(w for _, w in pairs)
    target = tau * total
    acc = 0.0
    for i, (value, weight) in enumerate(pairs):
        acc += weight
        if acc >= target:
            if i == 0 or weight <= 0:
                return value
            prev, _ = pairs[i - 1]
            frac = (target - (acc - weight)) / weight
            return prev + frac * (value - prev)
    return pairs[-1][0]


def weighted_median(pairs):
    return weighted_quantile(pairs, 0.5)


def baseline_row(p1, hour):
    return [round(p1 * math.exp(z * SIGMA * math.sqrt(hour - 1)), 2) for z in Z]


def shape_library(case):
    """[(shape {hour: log-ratio}, weight)] from the case's comparables."""
    console, broad = [], []
    for comp in case.get("comparables") or []:
        if not is_launch(comp):
            continue
        hours = day_hours(comp)
        if 1 not in hours or len(hours) < 20:
            continue
        shape = {h: math.log(hours[h] / hours[1]) for h in hours if h > 1}
        t = tier_of(comp)
        if t == "ea":
            continue
        w = 1.0 if t == "ok" else 0.5
        if is_console_only(comp):
            console.append((shape, w))
        broad.append((shape, w * (2.0 if is_console_only(comp) else 1.0)))
    return console, broad


def forecast_hours(p1, console, broad):
    """{hour: [q05, q25, q50, q75, q95]} for hours 2..24."""
    p1 = max(1, p1)
    out = {}
    for hour in range(2, 25):
        pairs = [(s[hour], w) for s, w in console if hour in s]
        if len(pairs) < MIN_SHAPES:
            pairs = [(s[hour], w) for s, w in broad if hour in s]
        if not pairs:
            out[hour] = baseline_row(p1, hour)
            continue
        median = weighted_median(pairs)
        quantiles = [weighted_quantile(pairs, tau) for tau in LEVELS]
        # Width floor: never narrower than the baseline's random-walk band.
        width = quantiles[4] - quantiles[0]
        need = 2 * 1.645 * SIGMA * math.sqrt(hour - 1)
        if width < need:
            mid = (quantiles[4] + quantiles[0]) / 2
            quantiles[0] = mid - need / 2
            quantiles[4] = mid + need / 2
            quantiles[1] = max(quantiles[0], min(quantiles[1], quantiles[4]))
            quantiles[2] = max(quantiles[1], min(quantiles[2], quantiles[4]))
            quantiles[3] = max(quantiles[2], min(quantiles[3], quantiles[4]))
        row = [round(p1 * math.exp(q), 2) for q in quantiles]
        for i in range(1, 5):
            row[i] = max(row[i], row[i - 1])
        out[hour] = [min(max(v, 0.01), 1e9) for v in row]
    return out


def forecast_case(case):
    if list(case["levels"]) != LEVELS:
        raise ValueError(f"case {case['id']} asks for levels {case['levels']}")
    known = next((k for k in case["known"] if k["hour"] == 1), None)
    if known is None:
        raise ValueError(f"case {case['id']} has no hour-1 print")
    console, broad = shape_library(case)
    hours = forecast_hours(max(1, known["viewers"]), console, broad)
    return {"hours": [{"hour": h, "q": hours[h]} for h in range(2, 25)]}


def main():
    input_dir = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(output_dir, exist_ok=True)
    for name in sorted(os.listdir(input_dir)):
        if not name.endswith(".in"):
            continue
        case_id = name[: -len(".in")]
        with open(os.path.join(input_dir, name), encoding="utf-8") as f:
            case = json.load(f)
        result = forecast_case(case)
        with open(os.path.join(output_dir, f"{case_id}.out"), "w", encoding="utf-8") as f:
            f.write(json.dumps(result) + "\n")


if __name__ == "__main__":
    main()
