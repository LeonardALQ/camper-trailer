"""Print every measured value at the end of the pytest run."""


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    try:
        from cad.tests.test_checks import RESULTS
    except Exception:  # the check module failed to import; pytest already reports why
        return
    tr = terminalreporter
    tr.section("measured values (data/checks.yaml)")
    for r in RESULTS:
        sub = f" [{r['sub']}]" if r["sub"] else ""
        tr.write_line(f"{r['id']:8s}{sub:30s} {r['status']:12s} {r['detail']}")
        for p in r.get("pairs", []) or []:
            tr.write_line(f"           {p['a']:>10s} / {p['b']:<10s} gap {p['gap_mm']:.3f} mm, overlap {p['overlap_mm3']:.4f} mm3")
        if r.get("fix"):
            f = r["fix"]
            tr.write_line(f"           smallest passing change: {f['param']} {f['baseline']:g} -> {f['value']:g} "
                          f"({f['change_mm']:+g} mm, {f['words']}), gives {f['measured_mm']} mm")
