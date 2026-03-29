import json
import os
import requests

BASE = os.environ.get("ALADDIN_BASE_URL", "http://149.154.65.180:8002")

def fetch(path: str):
    r = requests.get(BASE + path, timeout=10)
    assert r.status_code == 200
    return r.json()

def test_darkweb_leaks_list_snapshot(snapshot):
    data = fetch('/api/reports/dark-web/leaks?limit=5')
    snapshot.assert_match(
        json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2),
        'darkweb_leaks_list.json'
    )

def test_identity_attempts_list_snapshot(snapshot):
    data = fetch('/api/reports/identity-theft/attempts?limit=5')
    snapshot.assert_match(
        json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2),
        'identity_attempts_list.json'
    )

def test_tracker_top_list_snapshot(snapshot):
    data = fetch('/api/reports/privacy/tracker/top?limit=5')
    snapshot.assert_match(
        json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2),
        'tracker_top_list.json'
    )

def test_location_requests_list_snapshot(snapshot):
    data = fetch('/api/reports/privacy/location/requests?limit=5')
    snapshot.assert_match(
        json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2),
        'location_requests_list.json'
    )

def test_cleanup_records_list_snapshot(snapshot):
    data = fetch('/api/reports/privacy/cleanup/records?limit=5')
    snapshot.assert_match(
        json.dumps(data, sort_keys=True, ensure_ascii=False, indent=2),
        'cleanup_records_list.json'
    )

