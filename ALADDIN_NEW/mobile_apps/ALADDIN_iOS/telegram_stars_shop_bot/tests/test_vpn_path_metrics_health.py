from __future__ import annotations

from bot.services.vpn_path_metrics_health import (
    PathRow,
    build_plain_language_report,
    parse_path_csv,
)


_SAMPLE = """ts_utc,host_role,hostname,cf_bps,cf_mbs,listen_port,sessions,mem_total_m,mem_used_m,mem_avail_m,swap_total_m,swap_used_m,load1,wg_rtt_ms,wg_tx,wg_rx
2026-07-23T19:32:03Z,main149,h,11165455,11.165,8444,249,3813,1905,1907,1906,1877,1.09,436.620,1,2
2026-07-23T19:36:33Z,contabo,c,3698546,3.699,8446,282,11960,1261,10698,0,0,5.14,148.143,3,4
"""


def test_parse_path_csv_latest() -> None:
    rows = parse_path_csv(_SAMPLE)
    assert len(rows) == 2
    assert rows[0].host_role == "main149"
    assert rows[0].swap_used_m == 1877
    assert rows[1].cf_mbs == 3.699


def test_plain_report_has_five_sections() -> None:
    r149 = PathRow(
        ts_utc="t",
        host_role="main149",
        cf_mbs=11.0,
        sessions=200,
        swap_total_m=1906,
        swap_used_m=1877,
        load1=1.0,
        wg_rtt_ms=120.0,
    )
    r_c = PathRow(
        ts_utc="t",
        host_role="contabo",
        cf_mbs=14.0,
        sessions=100,
        swap_total_m=0,
        swap_used_m=0,
        load1=1.0,
        wg_rtt_ms=70.0,
    )
    v = build_plain_language_report(
        row_149=r149,
        row_contabo=r_c,
        contabo_recent_cf=[2.5, 14.0, 5.0, 12.0],
    )
    text = "\n".join(v.lines_html)
    assert "Мост RTT" in text
    assert "Мост обратно" in text
    assert "Contabo CF" in text
    assert "Плавает" in text
    assert "Swap на 149" in text
    assert "swap_149_high" in v.issue_codes
    assert v.severity >= 1


def test_verdict_contabo_cf_low() -> None:
    r149 = PathRow(
        ts_utc="t",
        host_role="main149",
        cf_mbs=10.0,
        sessions=10,
        swap_total_m=1906,
        swap_used_m=100,
        load1=0.2,
        wg_rtt_ms=90.0,
    )
    r_c = PathRow(
        ts_utc="t",
        host_role="contabo",
        cf_mbs=1.2,
        sessions=50,
        swap_total_m=0,
        swap_used_m=0,
        load1=1.0,
        wg_rtt_ms=100.0,
    )
    v = build_plain_language_report(row_149=r149, row_contabo=r_c)
    assert "contabo_cf_low" in v.issue_codes


def test_verdict_rtt_high() -> None:
    r149 = PathRow(
        ts_utc="t",
        host_role="main149",
        cf_mbs=10.0,
        sessions=10,
        swap_total_m=1906,
        swap_used_m=100,
        load1=0.2,
        wg_rtt_ms=437.0,
    )
    v = build_plain_language_report(row_149=r149, row_contabo=None)
    assert "wg_rtt_high" in v.issue_codes
