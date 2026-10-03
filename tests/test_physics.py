"""The truths in PROMPT.md, checked through the pipeline the API calls."""

import pytest

from app import physics
from app.pipeline import InputError, compute_rates

REL = 1e-12


def run(lumi="1", n_bunches="2808", sigma="1", unit="pb", int_lumi="1"):
    return compute_rates(lumi, n_bunches, sigma, unit, int_lumi)


def test_one_fb_times_one_inverse_fb_is_one_event():
    assert run(sigma="1", unit="fb", int_lumi="1").events == pytest.approx(1.0, rel=REL)


def test_one_pb_at_1e34_is_a_hundredth_of_a_hertz():
    assert run(lumi="1", sigma="1", unit="pb").rate_hz == pytest.approx(0.01, rel=REL)


def test_units_agree():
    mb, pb, fb = (
        run(sigma="1", unit="mb"),
        run(sigma="1e9", unit="pb"),
        run(sigma="1e12", unit="fb"),
    )
    for other in (pb, fb):
        assert other.rate_hz == pytest.approx(mb.rate_hz, rel=REL)
        assert other.events == pytest.approx(mb.events, rel=REL)


@pytest.mark.parametrize(
    "unit, cm2", [("fb", 1e-39), ("pb", 1e-36), ("nb", 1e-33), ("ub", 1e-30), ("mb", 1e-27)]
)
def test_each_unit_in_cm2(unit, cm2):
    assert physics.to_cm2(1.0, unit) == pytest.approx(cm2, rel=REL)


def test_nominal_pileup():
    assert run(lumi="1", n_bunches="2808").mu == pytest.approx(25.33, abs=0.01)


def test_pileup_scales_with_lumi_and_inversely_with_bunches():
    base = run(lumi="1", n_bunches="1000").mu
    assert run(lumi="2", n_bunches="1000").mu == pytest.approx(2 * base, rel=REL)
    assert run(lumi="1", n_bunches="2000").mu == pytest.approx(base / 2, rel=REL)


def test_hl_lhc_pileup():
    assert 190 <= run(lumi="7.5", n_bunches="2760").mu <= 200


def test_curve_spans_three_decades_at_20_points_per_decade():
    curve = run(n_bunches="2808").curve
    assert len(curve.lumi) == 61
    assert curve.lumi[0] == pytest.approx(1e32, rel=REL)
    assert curve.lumi[-1] == pytest.approx(1e35, rel=REL)
    assert curve.lumi[20] == pytest.approx(1e33, rel=REL)
    # The curve and the working point come from the same formula.
    i_1e34 = 40
    assert curve.mu[i_1e34] == pytest.approx(run(lumi="1", n_bunches="2808").mu, rel=REL)


@pytest.mark.parametrize("n_bunches", ["0", "3565", "2.5"])
def test_bad_bunch_counts_are_rejected(n_bunches):
    with pytest.raises(InputError, match="n_bunches"):
        run(n_bunches=n_bunches)


def test_edge_bunch_counts_are_accepted():
    assert run(n_bunches="1").n_bunches == 1
    assert run(n_bunches="3564").n_bunches == 3564


@pytest.mark.parametrize("field", ["lumi", "sigma", "int_lumi"])
@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf", "banana", ""])
def test_non_positive_or_non_numbers_are_rejected(field, value):
    with pytest.raises(InputError, match=field):
        run(**{field: value})


def test_unknown_unit_is_rejected():
    with pytest.raises(InputError, match="unit"):
        run(unit="barn")
