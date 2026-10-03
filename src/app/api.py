"""Routes only: the API, the page from src/web/, and the frontend libraries under /vendor/."""

import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.models import ErrorMessage, Rates
from app.pipeline import InputError, compute_rates

WEB_DIR = Path(__file__).resolve().parents[1] / "web"
VENDOR_DIR = Path(os.environ.get("VENDOR_DIR", "/opt/vendor"))

app = FastAPI(title="LHC Rate Calculator", version="0.1.0")


@app.exception_handler(InputError)
async def input_error(_: Request, exc: InputError) -> JSONResponse:
    """Turn a rejected input into a 400 with its message."""
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(RequestValidationError)
async def missing_parameter(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Turn a missing query parameter into a 400 that names it, in the same shape."""
    names = ", ".join(str(e["loc"][-1]) for e in exc.errors())
    return JSONResponse(
        status_code=400, content={"detail": f"missing or invalid parameter: {names}"}
    )


@app.get("/api/rates", response_model=Rates, responses={400: {"model": ErrorMessage}})
def rates(lumi: str, n_bunches: str, sigma: str, unit: str, int_lumi: str) -> Rates:
    """Rates, events and pile-up; L in 1e34 cm⁻² s⁻¹, sigma in ``unit``, int_lumi in fb⁻¹."""
    return compute_rates(lumi, n_bunches, sigma, unit, int_lumi)


app.mount("/vendor", StaticFiles(directory=VENDOR_DIR, check_dir=False), name="vendor")
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
