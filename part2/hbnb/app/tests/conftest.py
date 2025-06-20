import pytest

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    passed_reports = terminalreporter.stats.get('passed', [])
    failed = len(terminalreporter.stats.get('failed', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    xfailed = len(terminalreporter.stats.get('xfailed', []))
    warnings = len(terminalreporter.stats.get('warnings', []))

    passed = len(passed_reports)
    terminalreporter.write_sep("=", "Test Suite Summary")
    terminalreporter.write_line(f"✅ Passed:   {passed}")
    terminalreporter.write_line(f"❌ Failed:   {failed}")
    terminalreporter.write_line(f"⚠️  Skipped:  {skipped}")
    terminalreporter.write_line(f"✳️  XFailed:  {xfailed}")
    terminalreporter.write_line(f"⚠️  Warnings: {warnings}")

    terminalreporter.write_sep("-", "Sections tested")
    terminalreporter.write_line(" • Users")
    terminalreporter.write_line(" • Hosts")
    terminalreporter.write_line(" • Amenities")
    terminalreporter.write_line(" • Places")
    terminalreporter.write_line(" • Bookings (guest-count & overlap bounds)")
    terminalreporter.write_line(" • Reviews (rating bounds)")
    terminalreporter.write_sep("-", "End of Sections")

    if failed == 0:
        terminalreporter.write_line("\nAll tests passed successfully! 🎉\n")
        terminalreporter.write_line("Executed Tests:")
        for rep in passed_reports:
            name = rep.nodeid.split("::")[-1]
            terminalreporter.write_line(f" - {name}")
    else:
        terminalreporter.write_line("\nSome tests failed or skipped. Please review above.\n")

    terminalreporter.write_sep("=", "End of Test Suite Summary")
