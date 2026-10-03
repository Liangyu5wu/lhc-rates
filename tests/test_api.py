"""The API contract: a result for good input, a 400 naming the problem for bad input."""

import pytest
from fastapi.testclient import TestClient

from app.api import app

client = TestClient(app)
GOOD = {"lumi": "1", "n_bunches": "2808", "sigma": "1", "unit": "pb", "int_lumi": "1"}


def test_good_request_returns_the_result():
    response = client.get("/api/rates", params=GOOD)
    assert response.status_code == 200
    body = response.json()
    assert body["mu"] == pytest.approx(25.33, abs=0.01)
    assert body["rate_hz"] == pytest.approx(0.01, rel=1e-12)
    assert body["constants"] == {"f_rev_hz": 11245.5, "sigma_inel_mb": 80.0}


@pytest.mark.parametrize(
    "field, value",
    [
        ("n_bunches", "0"),
        ("n_bunches", "3565"),
        ("n_bunches", "2.5"),
        ("lumi", "banana"),
        ("unit", "barn"),
    ],
)
def test_bad_input_is_a_400_that_names_the_field(field, value):
    response = client.get("/api/rates", params={**GOOD, field: value})
    assert response.status_code == 400
    assert field in response.json()["detail"]


def test_missing_parameter_is_a_400_that_names_it():
    params = {k: v for k, v in GOOD.items() if k != "sigma"}
    response = client.get("/api/rates", params=params)
    assert response.status_code == 400
    assert "sigma" in response.json()["detail"]


def test_page_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "LHC Rate Calculator" in response.text
