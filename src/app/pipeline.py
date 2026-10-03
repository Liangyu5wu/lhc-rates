"""The one pipeline: validate the raw inputs, then compute rates, events and pile-up."""

import math

from app import physics
from app.models import Constants, Curve, Rates

LUMI_INPUT_UNIT = 1e34  # the page asks for L in units of 1e34 cm^-2 s^-1


class InputError(ValueError):
    """An input the calculation cannot accept; the message names it and says why."""


def positive_number(name: str, text: str) -> float:
    """Parse a finite, positive number.

    Args:
        name: The parameter name, for the message.
        text: The raw value.

    Returns:
        The number.

    Raises:
        InputError: If it is not a finite number greater than 0.
    """
    try:
        value = float(text)
    except TypeError, ValueError:
        raise InputError(f"{name} must be a number, got {text!r}") from None
    if not math.isfinite(value) or value <= 0:
        raise InputError(f"{name} must be a finite number greater than 0, got {text!r}")
    return value


def bunch_count(text: str) -> int:
    """Parse the number of colliding bunches: an integer from 1 to 3564.

    Raises:
        InputError: If it is not a whole number in that range.
    """
    value = positive_number("n_bunches", text)
    if not value.is_integer() or not 1 <= value <= physics.MAX_BUNCHES:
        raise InputError(
            f"n_bunches must be a whole number from 1 to {physics.MAX_BUNCHES}, got {text!r}"
        )
    return int(value)


def cross_section_unit(text: str) -> str:
    """Check the cross-section unit against the supported list.

    Raises:
        InputError: If the unit is not supported.
    """
    if text not in physics.UNIT_CM2:
        raise InputError(f"unit must be one of {', '.join(physics.UNIT_CM2)}, got {text!r}")
    return text


def compute_rates(lumi: str, n_bunches: str, sigma: str, unit: str, int_lumi: str) -> Rates:
    """Validate the inputs and compute R, N, mu and the mu(L) curve.

    Args:
        lumi: Instantaneous luminosity, in units of 1e34 cm⁻² s⁻¹.
        n_bunches: Number of colliding bunches.
        sigma: Cross-section, in ``unit``.
        unit: fb, pb, nb, ub or mb.
        int_lumi: Integrated luminosity, in fb⁻¹.

    Returns:
        The results, with the constants used.

    Raises:
        InputError: For the first input that is not acceptable.
    """
    lumi_cgs = positive_number("lumi", lumi) * LUMI_INPUT_UNIT
    n_b = bunch_count(n_bunches)
    sigma_cm2 = physics.to_cm2(positive_number("sigma", sigma), cross_section_unit(unit))
    int_lumi_inv_fb = positive_number("int_lumi", int_lumi)
    curve_lumi, curve_mu = physics.pileup_curve(n_b)
    return Rates(
        lumi=lumi_cgs,
        n_bunches=n_b,
        sigma_cm2=sigma_cm2,
        rate_hz=physics.event_rate(sigma_cm2, lumi_cgs),
        events=physics.expected_events(sigma_cm2, int_lumi_inv_fb),
        mu=physics.pileup(lumi_cgs, n_b),
        curve=Curve(lumi=curve_lumi, mu=curve_mu),
        constants=Constants(f_rev_hz=physics.F_REV_HZ, sigma_inel_mb=physics.SIGMA_INEL_MB),
    )
