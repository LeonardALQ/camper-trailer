"""Print every measured value at the end of the pytest run, and write the ute garage's checks for the site."""


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    tr = terminalreporter
    try:
        from cad.tests.test_ute import GARAGE_RESULTS, RESULTS as UTE_RESULTS
    except Exception:  # the module failed to import; pytest already reports why
        UTE_RESULTS, GARAGE_RESULTS = [], []
    if UTE_RESULTS:
        tr.section("ute and bike box checks (data/ute/ute.yaml, data/ute/garage-checks.yaml)")
        for r in UTE_RESULTS + GARAGE_RESULTS:
            sub = f" [{r['sub']}]" if r.get("sub") else ""
            tr.write_line(f"{r['id']:8s}{sub:30s} {r['status']:12s} {r['detail']}")
    try:
        from cad.tests.test_trailer import RESULTS as TRAILER_RESULTS
    except Exception:
        return
    tr.section("whole-trailer checks (data/checks.yaml, trailer_checks)")
    for r in TRAILER_RESULTS:
        tr.write_line(f"{r['id']:8s} {r['status']:12s} {r['detail']}")
