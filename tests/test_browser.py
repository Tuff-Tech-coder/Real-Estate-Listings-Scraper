"""Optional real Chromium coverage. Enable with RUN_BROWSER_TESTS=1."""

import os

import pytest

from realestate_scraper import run_demo


@pytest.mark.skipif(
    os.environ.get("RUN_BROWSER_TESTS") != "1", reason="Optional Chromium fixture test"
)
def test_javascript_rendered_pages_match_html_fixture_results():
    rendered, stats = run_demo(browser=True)
    plain, _ = run_demo()
    assert rendered == plain
    assert len(rendered) == 25
    assert stats["pages"] == 3
    assert stats["duplicates"] == 2
