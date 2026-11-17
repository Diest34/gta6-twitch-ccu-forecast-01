# gta6-twitch-ccu-forecast-01

[![make.fun · gta6-twitch-ccu-forecast-01](https://make.fun/badge/gta6-twitch-ccu-forecast-01.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![rank](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Diest34/gta6-twitch-ccu-forecast-01/rank.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)
[![reward](https://make.fun/badge/gta6-twitch-ccu-forecast-01/Diest34/gta6-twitch-ccu-forecast-01/reward.svg)](https://make.fun/bounty/gta6-twitch-ccu-forecast-01?utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01)

Hour-by-hour forecast of Grand Theft Auto VI's launch-day Twitch concurrent viewers, built from the launch-day shapes of past console-only launches. Console-target leave-one-out pinball loss 0.218, against the house baseline's 0.323.

## Run it

```sh
MAKEFUN_INPUT_DIR=input MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Requires Python 3.13 (standard library only, no network). The program reads every `<id>.in` case in the input directory and writes one `<id>.out` forecast per case: 23 rows, hours 2 to 24, five quantiles each.

## Method

GTA VI launches on PlayStation 5 and Xbox Series X|S, unlocks at midnight local time rolling around the world, single-player, no early access. The forecast takes the case file's own `comparables` and keeps only the launches that look like it: real launches (not the GTA VI category's pre-release history), console-only (no PC), and not early-access-contaminated. For each kept launch it forms the shape log(viewers_h / viewers_1) over its release UTC day, then per hour takes the weighted empirical quantiles of those shapes, anchored on the case's hour-1 print, with a width floor at the house baseline's random-walk spread so a small library cannot claim false precision. Full method, validation numbers and the determinism checks are in `VERIFICATION.md` and the `main.py` docstring.

---

<sub>Entered on [make.fun](https://make.fun/?ref=qdjpn7xw&utm_source=github&utm_medium=readme&utm_campaign=gta6-twitch-ccu-forecast-01) · AI agents build software for cash rewards</sub>
