// Draws what the backend computes. Nothing here computes a result: it formats
// numbers for display and plots the curve the API returns.

const form = document.getElementById("inputs");
const errorBox = document.getElementById("error");
const plot = document.getElementById("plot");
const SUPERSCRIPT = { "-": "⁻", 0: "⁰", 1: "¹", 2: "²", 3: "³", 4: "⁴", 5: "⁵", 6: "⁶", 7: "⁷", 8: "⁸", 9: "⁹" };

function sci(x, digits = 3) {
  if (x === 0) return "0";
  const [mantissa, exponent] = x.toExponential(digits - 1).split("e");
  const exp = Number(exponent);
  if (exp >= -2 && exp <= 3) return Number(x.toPrecision(digits)).toLocaleString("en-US");
  const sup = String(exp).split("").map((c) => SUPERSCRIPT[c]).join("");
  return `${mantissa} × 10${sup}`;
}

function css(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function clearResults() {
  for (const id of ["rate", "events", "mu"]) document.getElementById(id).textContent = "–";
  Plotly.purge(plot);
}

function showError(message) {
  clearResults(); // a stale plot never sits beside an error
  errorBox.textContent = message;
  errorBox.hidden = false;
}

function draw(r) {
  errorBox.hidden = true;
  document.getElementById("rate").textContent = `${sci(r.rate_hz)} Hz`;
  document.getElementById("events").textContent = sci(r.events);
  document.getElementById("mu").textContent = sci(r.mu);
  document.getElementById("constants").textContent =
    `Fixed: f_rev = ${r.constants.f_rev_hz} Hz, σ_inel = ${r.constants.sigma_inel_mb} mb (√s = 13.6 TeV). ` +
    `Curve for n_b = ${r.n_bunches}.`;

  const axis = {
    type: "log",
    gridcolor: css("--grid"),
    zeroline: false,
    color: css("--muted"),
    tickfont: { color: css("--ink-2") },
    exponentformat: "power",
  };
  const curve = {
    x: r.curve.lumi,
    y: r.curve.mu,
    mode: "lines",
    line: { color: css("--series-1"), width: 2 },
    hovertemplate: "L = %{x:.2e} cm⁻²s⁻¹<br>μ = %{y:.3g}<extra></extra>",
    showlegend: false,
  };
  const point = {
    x: [r.lumi],
    y: [r.mu],
    mode: "markers+text",
    marker: { color: css("--series-2"), size: 10, line: { color: css("--surface"), width: 2 } },
    text: [`your point: μ = ${sci(r.mu)}`],
    textposition: "middle left",
    textfont: { color: css("--ink-2") },
    hovertemplate: "Your point<br>L = %{x:.2e} cm⁻²s⁻¹<br>μ = %{y:.3g}<extra></extra>",
    showlegend: false,
  };
  const layout = {
    margin: { l: 64, r: 20, t: 16, b: 52 },
    paper_bgcolor: css("--surface"),
    plot_bgcolor: css("--surface"),
    font: { family: "system-ui, sans-serif", color: css("--ink-2") },
    xaxis: { ...axis, title: { text: "Luminosity L [cm⁻² s⁻¹]" } },
    yaxis: { ...axis, title: { text: "Pile-up μ" } },
    hovermode: "closest",
  };
  Plotly.react(plot, [curve, point], layout, { displaylogo: false, responsive: true });
}

async function calculate(event) {
  if (event) event.preventDefault();
  const params = new URLSearchParams(new FormData(form));
  try {
    const response = await fetch(`/api/rates?${params}`);
    const body = await response.json();
    if (!response.ok) return showError(body.detail);
    draw(body);
  } catch {
    showError("Could not reach the backend. Is it running? Try `make up`.");
  }
}

form.addEventListener("submit", calculate);
calculate();
