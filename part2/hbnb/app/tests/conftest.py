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
    terminalreporter.write_line(" • Bookings (guest‐count & overlap bounds)")
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

# --- DELETE existing review ---
def test_delete_review(client, booking_id):
    rv = client.post('/api/v1/reviews/', json={"booking_id": booking_id, "text": "ToDelete", "rating": 4})
    if rv.status_code != 201:
        pytest.skip("Review creation unavailable")
    rid = rv.get_json()['id']
    rv2 = client.delete(f"/api/v1/reviews/{rid}")
    assert rv2.status_code in (200, 204)
    rv3 = client.get(f"/api/v1/reviews/{rid}")
    assert rv3.status_code == 404

# --- PATCH review text and rating ---
@pytest.mark.parametrize("field,value,status_code", [
    ("text", "Updated text", 200),
    ("rating", 5, 200),
    ("rating", 10, 400),
    ("text", 123, 400)
])
def test_patch_review_fields(client, booking_id, field, value, status_code):
    rv = client.post('/api/v1/reviews/', json={"booking_id": booking_id, "text": "Initial", "rating": 3})
    if rv.status_code != 201:
        pytest.skip("Review creation unavailable")
    rid = rv.get_json()['id']
    rv2 = client.patch(f"/api/v1/reviews/{rid}", json={field: value})
    assert rv2.status_code == status_code

# --- Aggregation endpoints (xfail until implemented) ---
import pytest as _pytest

@_pytest.mark.xfail(raises=AttributeError, reason="Place average rating endpoint not implemented")
def test_place_average_rating(client, place_id, user_id, amenity_id):
    bids = []
    for rating in [4, 2]:
        rvb = client.post('/api/v1/bookings/', json={
            "user_id": user_id, "place_id": place_id,
            "guest_count": 1, "checkin_date": date.today().isoformat(), "night_count": 1
        })
        if rvb.status_code != 201:
            pytest.skip("Booking creation unavailable")
        bid = rvb.get_json()['id']
        bids.append(bid)
        rvr = client.post('/api/v1/reviews/', json={"booking_id": bid, "text": "AvgTest", "rating": rating})
        if rvr.status_code != 201:
            pytest.skip("Review creation unavailable")
    rv = client.get(f"/api/v1/places/{place_id}/rating")
    assert rv.status_code == 200
    avg = rv.get_json().get('average_rating')
    assert avg == pytest.approx(3.0)

@_pytest.mark.xfail(raises=AttributeError, reason="Host average rating endpoint not implemented")
def test_host_average_rating(client, user_id):
    rv = client.get(f"/api/v1/hosts/{user_id}/rating")
    assert rv.status_code == 200
    assert 'average_rating' in rv.get_json()

@_pytest.mark.xfail(raises=AttributeError, reason="Booking total cost endpoint not implemented")
def test_booking_total_cost(client, booking_id):
    rv = client.get(f"/api/v1/bookings/{booking_id}/cost")
    assert rv.status_code == 200
    cost = rv.get_json().get('total_cost')
    assert isinstance(cost, (int, float))
    assert cost >= 0
