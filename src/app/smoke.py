"""Smoke test of the running app, run by `make smoke`: a real result, not just a status code."""

import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
NOMINAL = "/api/rates?lumi=1&n_bunches=2808&sigma=1&unit=pb&int_lumi=1"


def get(path: str) -> tuple[int, bytes]:
    """GET a path from the app, returning the status and body, including for 4xx."""
    try:
        with urllib.request.urlopen(BASE + path, timeout=5) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def main() -> None:
    """Wait for the app, then check mu, a rejection, and that the page and Plotly are served."""
    for _ in range(50):
        try:
            get("/")
            break
        except OSError:
            time.sleep(0.2)
    else:
        sys.exit("smoke: the app did not start")

    status, body = get(NOMINAL)
    mu = json.loads(body)["mu"]
    assert status == 200 and abs(mu - 25.33) < 0.01, (status, body[:200])
    status, body = get("/api/rates?lumi=1&n_bunches=0&sigma=1&unit=pb&int_lumi=1")
    assert status == 400 and b"n_bunches" in body, (status, body)
    status, body = get("/")
    assert status == 200 and b"LHC Rate Calculator" in body, status
    status, body = get("/vendor/plotly.min.js")
    assert status == 200 and len(body) > 100_000, (status, len(body))
    print(
        f"smoke ok: mu = {mu:.3f} at L = 1e34, n_b = 2808; n_b = 0 rejected; page and Plotly served"
    )


if __name__ == "__main__":
    main()
