# LHC Rate Calculator

A small web app for back-of-the-envelope collider numbers: from a luminosity, a bunch count and a process cross-section, it gives the event rate, the expected number of events, and the mean pile-up. It also plots pile-up against luminosity.

## What it computes

| Output | Formula |
|---|---|
| Event rate | R = σ L |
| Expected events | N = σ ∫L dt |
| Mean pile-up | μ = σ_inel L / (n_b f_rev) |

Inputs:

- L, in 10³⁴ cm⁻² s⁻¹;
- n_b, the number of colliding bunches, from 1 to 3564;
- σ, in fb, pb, nb, µb or mb;
- ∫L dt, in fb⁻¹.

Fixed: f_rev = 11245.5 Hz and σ_inel = 80 mb (√s = 13.6 TeV).

**What it is fit for:** order-of-magnitude planning, such as how many events a process gives in a run, or what pile-up a luminosity and filling scheme imply. **What it is not:** a physics prediction. It assumes:

- one fixed σ_inel;
- equal bunches, with μ as an average over bunches and over the fill;
- no detector acceptance, efficiency or trigger;
- no luminosity levelling or decay through a fill.

## Run it

You need only Docker, Make and git.

```sh
make build    # build the image (once, and after dependencies change)
make up       # start it, then open http://127.0.0.1:8000
make down     # stop it
make verify   # lint, tests, and a smoke check of the running app
```

The API is documented at http://127.0.0.1:8000/docs. For example:

```text
GET /api/rates?lumi=1&n_bunches=2808&sigma=1&unit=pb&int_lumi=1
→ rate_hz 0.01, events 1000, mu 25.33
```

Bad input returns a 400 whose message names the parameter. For example, `n_bunches=0` gives "n_bunches must be a whole number from 1 to 3564".

## How it is checked

The tests encode the statements in `PROMPT.md`:

- 1 fb × 1 fb⁻¹ = 1 event.
- 1 pb at 10³⁴ cm⁻² s⁻¹ = 0.01 Hz.
- 1 mb, 10⁹ pb and 10¹² fb agree.
- μ = 25.33 at 10³⁴ cm⁻² s⁻¹ with 2808 bunches.
- μ is linear in L and inverse in n_b.
- μ is 190 to 200 at the HL-LHC point (7.5 × 10³⁴ cm⁻² s⁻¹, 2760 bunches).
- Bad inputs are rejected.

Each test was seen to fail on a deliberately injected bug before it passed:

- f_rev replaced by the bunch-crossing frequency;
- pb off by 10;
- fb⁻¹ off by 10³;
- the bunch limit at 3565;
- n_b dropped from μ.

## Not verified

- The constants (f_rev, σ_inel, the 3564 bunch slots) were checked by the author from domain knowledge, not against a cited source.
- The page has no automated browser tests. The smoke check confirms only that the page and Plotly are served.
