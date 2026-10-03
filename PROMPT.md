Follow AGENTS.md.

Build a small web app, the LHC Rate Calculator, for the rates and pile-up of a proton-proton collider.

The user enters four inputs:

- the instantaneous luminosity L, in units of 10³⁴ cm⁻² s⁻¹;
- the number of colliding bunches n_b;
- a process cross-section σ, as a number and a unit chosen from fb, pb, nb, µb and mb;
- the integrated luminosity ∫L dt, in fb⁻¹.

The backend returns:

- the event rate R = σ L, in Hz;
- the expected number of events N = σ ∫L dt;
- the mean pile-up μ = σ_inel L / (n_b f_rev);
- the curve μ(L) for the given n_b, from 10³² to 10³⁵ cm⁻² s⁻¹, at 20 points per decade.

The page shows the three numbers and plots μ against L on log-log axes, with the user's working point marked. The two constants are fixed and shown on the page: f_rev = 11245.5 Hz and σ_inel = 80 mb (√s = 13.6 TeV).

The backend rejects, and the page shows its message for:

- any number that is not finite and positive;
- an n_b that is not an integer from 1 to 3564 (the number of 25 ns bunch slots);
- a unit not in the list.

Units: 1 b = 10⁻²⁴ cm², and 1 fb⁻¹ = 10³⁹ cm⁻².

It must satisfy:

- σ = 1 fb and ∫L dt = 1 fb⁻¹ give N = 1, within a relative 10⁻¹².
- σ = 1 pb and L = 10³⁴ cm⁻² s⁻¹ give R = 0.01 Hz, within a relative 10⁻¹².
- 1 mb, 10⁹ pb and 10¹² fb give the same R and N, within a relative 10⁻¹².
- L = 10³⁴ cm⁻² s⁻¹ and n_b = 2808 give μ = 25.33, within 0.01.
- Doubling L doubles μ, and doubling n_b halves it, within a relative 10⁻¹².
- L = 7.5 × 10³⁴ cm⁻² s⁻¹ and n_b = 2760 (HL-LHC) give μ between 190 and 200.
- n_b = 0, 3565 and 2.5 are each rejected with a 400 that names n_b.
