import json
import os
import requests

BASE = os.environ.get("ALADDIN_BASE_URL", "http://149.154.65.180:8002")

def fetch(path: str):
    r = requests.get(BASE + path, timeout=10)
    assert r.status_code == 200
    return r.json()

def test_dw_stats_snapshot(snapshot):
    data = fetch('/api/reports/dark-web/stats')
    snapshot.assert_match(
        json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2),
        'dw_stats.json'
    )

def test_identity_stats_snapshot(snapshot):
    data = fetch('/api/reports/identity-theft/stats')
    snapshot.assert_match(
        json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2),
        'identity_stats.json'
    )

def test_tracker_stats_snapshot(snapshot):
    data = fetch('/api/reports/privacy/tracker/stats')
    snapshot.assert_match(
        json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2),
        'tracker_stats.json'
    )

def test_location_stats_snapshot(snapshot):
    data = fetch('/api/reports/privacy/location/stats')
    snapshot.assert_match(
        json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2),
        'location_stats.json'
    )

def test_cleanup_stats_snapshot(snapshot):
    data = fetch('/api/reports/privacy/cleanup/stats')
    snapshot.assert_match(
        json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2),
        'cleanup_stats.json'
    )

