import pytest

# Custom Pytest terminal summary with user-friendly formatting

def pytest_terminal_summary(terminalreporter, exitstatus, config):
    passed_reports = terminalreporter.stats.get('passed', [])
    failed = len(terminalreporter.stats.get('failed', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    xfailed = len(terminalreporter.stats.get('xfailed', []))
    warnings = len(terminalreporter.stats.get('warnings', []))

    passed = len(passed_reports)
    # Detailed counts
    terminalreporter.write_sep("=", "Test Suite Summary")
    terminalreporter.write_line(f"✅ Passed:   {passed}")
    terminalreporter.write_line(f"❌ Failed:   {failed}")
    terminalreporter.write_line(f"⚠️  Skipped:  {skipped}")
    terminalreporter.write_line(f"✳️  XFailed:  {xfailed}")
    terminalreporter.write_line(f"⚠️  Warnings: {warnings}")
    terminalreporter.write_sep("-", "")

    # Contextual notes
    if skipped:
        terminalreporter.write_line("Note: Skipped tests mark unimplemented or conditionally unavailable features.")
    if xfailed:
        terminalreporter.write_line("Note: XFailed tests mark known gaps awaiting implementation.")
    if warnings:
        terminalreporter.write_line("Note: Warnings are deprecation notices or minor issues.")

    # Friendly summary message
    if failed == 0:
        terminalreporter.write_line("\nAll tests passed successfully! 🎉\n")
        if passed_reports:
            terminalreporter.write_line("Executed Tests:")
            for rep in passed_reports:
                # Show just function name for brevity
                name = rep.nodeid.split("::")[-1]
                terminalreporter.write_line(f" - {name}")
    else:
        terminalreporter.write_line("\nSome tests failed or skipped. Check details above.")
    terminalreporter.write_sep("=", "End of Summary")
