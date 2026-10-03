"""Collider rates and pile-up, in CGS units: cross-sections in cm², luminosity in cm⁻² s⁻¹."""

F_REV_HZ = 11245.5  # LHC revolution frequency
SIGMA_INEL_MB = 80.0  # inelastic pp cross-section at sqrt(s) = 13.6 TeV
MAX_BUNCHES = 3564  # 25 ns bunch slots in one LHC turn

BARN_CM2 = 1e-24
INV_FB_CM2 = 1e39  # 1 fb^-1 = 1e39 cm^-2
UNIT_CM2 = {
    "fb": 1e-15 * BARN_CM2,
    "pb": 1e-12 * BARN_CM2,
    "nb": 1e-9 * BARN_CM2,
    "ub": 1e-6 * BARN_CM2,
    "mb": 1e-3 * BARN_CM2,
}
SIGMA_INEL_CM2 = SIGMA_INEL_MB * UNIT_CM2["mb"]

CURVE_LUMI_DECADES = (32, 35)  # 1e32 to 1e35 cm^-2 s^-1
CURVE_POINTS_PER_DECADE = 20


def to_cm2(value: float, unit: str) -> float:
    """Convert a cross-section to cm².

    Args:
        value: The cross-section in ``unit``.
        unit: One of the keys of ``UNIT_CM2``.

    Returns:
        The cross-section in cm².
    """
    return value * UNIT_CM2[unit]


def event_rate(sigma_cm2: float, lumi: float) -> float:
    """Event rate R = sigma L, in Hz, for luminosity in cm⁻² s⁻¹."""
    return sigma_cm2 * lumi


def expected_events(sigma_cm2: float, int_lumi_inv_fb: float) -> float:
    """Expected number of events N = sigma times integrated luminosity, given in fb⁻¹."""
    return sigma_cm2 * int_lumi_inv_fb * INV_FB_CM2


def pileup(lumi: float, n_bunches: int) -> float:
    """Mean number of inelastic interactions per bunch crossing.

    mu = sigma_inel L / (n_b f_rev).
    """
    return SIGMA_INEL_CM2 * lumi / (n_bunches * F_REV_HZ)


def pileup_curve(n_bunches: int) -> tuple[list[float], list[float]]:
    """mu(L) for fixed n_b, log-spaced from 1e32 to 1e35 cm⁻² s⁻¹ at 20 points per decade.

    Args:
        n_bunches: Number of colliding bunches.

    Returns:
        The luminosities and the pile-up at each.
    """
    first, last = CURVE_LUMI_DECADES
    n = (last - first) * CURVE_POINTS_PER_DECADE + 1
    lumis = [10 ** (first + i / CURVE_POINTS_PER_DECADE) for i in range(n)]
    return lumis, [pileup(lumi, n_bunches) for lumi in lumis]
