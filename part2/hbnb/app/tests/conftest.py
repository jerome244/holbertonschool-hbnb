import pytest

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    passed_reports = terminalreporter.stats.get('passed', [])
    failed = len(terminalreporter.stats.get('failed', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    xfailed = len(terminalreporter.stats.get('xfailed', []))
    warnings = len(terminalreporter.stats.get('warnings', []))
    terminalreporter.write_sep("=", "Test Suite Summary")
    terminalreporter.write_line(f"✅ Passed:   {len(passed_reports)}")
    terminalreporter.write_line(f"❌ Failed:   {failed}")
    terminalreporter.write_line(f"⚠️  Skipped:  {skipped}")
    terminalreporter.write_line(f"✳️  XFailed:  {xfailed}")
    terminalreporter.write_line(f"⚠️  Warnings: {warnings}")
    terminalreporter.write_sep("-", "Sections tested")
    # … your static section list …
    terminalreporter.write_sep("-", "End of Sections")

    # Now: grouped “Executed Tests” lists
    terminalreporter.write_line("\nExecuted Tests:")
    groups = {"API": [], "Facade": [], "Persistence": []}
    for rep in passed_reports:
        nid = rep.nodeid
        if "test_api.py" in nid:
            groups["API"].append(nid.split("::")[-1])
        elif "test_facade_and_repo.py" in nid:
            groups["Facade"].append(nid.split("::")[-1])
        elif "test_repository" in nid or "test_repo" in nid:
            groups["Persistence"].append(nid.split("::")[-1])
    for section, names in groups.items():
        terminalreporter.write_line(f"  {section} ({len(names)}):")
        for n in names:
            terminalreporter.write_line(f"    - {n}")

    if failed == 0:
        terminalreporter.write_line("\nAll tests passed! 🎉")
    else:
        terminalreporter.write_line("\nSome tests failed or were skipped; see above.")

    terminalreporter.write_sep("=", "End of Test Suite Summary")
