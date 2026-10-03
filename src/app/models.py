"""Typed response models: the contract shown at /docs."""

from pydantic import BaseModel


class Curve(BaseModel):
    """Pile-up against luminosity, for the requested number of bunches."""

    lumi: list[float]
    mu: list[float]


class Constants(BaseModel):
    """The fixed inputs, shown on the page."""

    f_rev_hz: float
    sigma_inel_mb: float


class Rates(BaseModel):
    """Everything the page shows for one set of inputs."""

    lumi: float  # cm^-2 s^-1
    n_bunches: int
    sigma_cm2: float
    rate_hz: float
    events: float
    mu: float
    curve: Curve
    constants: Constants


class ErrorMessage(BaseModel):
    """A rejected request: one plain message naming the input and the reason."""

    detail: str
