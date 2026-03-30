# rel-15 soak 24h

## Status
- `rel-15`: in progress

## What is running
- Background monitor started:
  - `tools/release_soak_24h_monitor.py`
- Duration: `24h`
- Interval: `5m` per sample
- Data source: Prometheus API (`http://149.154.65.180:9090`)

## Collected signals per sample
- `p95_seconds`
- `five_xx_share`
- `firing_alerts_count`
- `firing_alerts[]`
- `freshness_seconds` by domain

## Live artifacts
- Samples: `docs/release/soak/soak-20260330_172810.samples.jsonl`
- Live log: `docs/release/soak/soak-live.log`
- Final summary (after 24h): `docs/release/soak/soak-20260330_172810.summary.json`

## Start baseline snapshot
- p95: `0.0475s`
- 5xx share: `0.0`
- firing alerts: `0`
- freshness (sec):
  - darkweb: `2339.45`
  - identity: `2346.22`
  - tracker: `2341.50`
  - location: `2343.68`
  - cleanup: `2340.39`

## PASS criteria for final report
- `p95_max < 0.5s`
- `five_xx_max < 0.01`
- `max_firing_alerts == 0`
- `freshness_within_thresholds == true`
