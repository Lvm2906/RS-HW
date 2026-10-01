"""build_exhibits.py - RS-HW working paper: every number, table and figure in the paper is generated
here from the project files (no number is typed by hand into main.tex).
Outputs: numbers.tex (LaTeX macros), tables/*.tex, figures/fig1_regime_path.pdf
"""
from pathlib import Path
import numpy as np
import pandas as pd
from hmmlearn.hmm import GaussianHMM

ROOT = Path(__file__).resolve().parent.parent
CODE, ABG, OUT = ROOT / "Code", ROOT / "Abgaben", Path(__file__).resolve().parent
M = {}  # macro name -> string


def f(x, d):  # fixed decimals, English decimal point, proper minus
    s = f"{x:.{d}f}"
    if float(s) == 0: s = s.lstrip("-")
    return s.replace("-", "\\ensuremath{-}") if s.startswith("-") else s


# ---------------- Data -----------------------------------------------------------------------
y = pd.read_csv(CODE / "yields.csv", parse_dates=["date"])
h = pd.read_csv(CODE / "hmm_input_changes.csv", parse_dates=["Datum"])
X = h[["Level", "Slope", "Curvature"]].to_numpy()
dates = h["Datum"].reset_index(drop=True)
T = len(X)
M.update(NLevelDays=str(len(y)), NDays=str(T), NPairsAll=str(T - 1),
         StartLevel=y["date"].iloc[0].strftime("%-d %B %Y"), StartChg=dates.iloc[0].strftime("%-d %B %Y"),
         EndDate=dates.iloc[-1].strftime("%-d %B %Y"), NMat=str(y.shape[1] - 1))
r = y["3M"].to_numpy()[1:]
M.update(RMin=f(r.min(), 2), RMax=f(r.max(), 2))

# PCA diagnostics (same construction as Abgaben/01.07.Abgabe.py)
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
cols = [c for c in y.columns if c != "date"]
pca = PCA(3).fit(StandardScaler().fit_transform(y[cols]))
ev = pca.explained_variance_ratio_
M.update(PCAone=f(100 * ev[0], 1), PCAtwo=f(100 * ev[1], 1), PCAthree=f(100 * ev[2], 1), PCAsum=f(100 * ev.sum(), 1))
load = pd.DataFrame(pca.components_, columns=cols, index=["PC1", "PC2", "PC3"])
chk = pd.DataFrame(pca.transform(StandardScaler().fit_transform(y[cols])), columns=["a", "b", "c"]).diff().dropna()
assert np.allclose(chk.to_numpy(), X), "PCA construction does not reproduce hmm_input_changes.csv"

# ---------------- Stage 1 ----------------------------------------------------------------------
hmm2 = GaussianHMM(2, covariance_type="full", n_iter=100, random_state=42).fit(X)
hmm1 = GaussianHMM(1, covariance_type="full", n_iter=100, random_state=42).fit(X)
assert hmm2.monitor_.converged
tr = np.array([np.trace(c) for c in hmm2.covars_]); kr = int(np.argmax(tr)); ru = 1 - kr
L2, L1 = hmm2.score(X), hmm1.score(X)
B2, B1 = hmm2.bic(X), hmm1.bic(X)
path = hmm2.predict(X); crisis = path == kr
post = hmm2.predict_proba(X)[:, kr]
sw = np.flatnonzero(np.diff(path) != 0) + 1
segs = np.split(np.arange(T), sw)
clen = sorted([len(s) for s in segs if crisis[s[0]]], reverse=True)
M.update(Iter=str(hmm2.monitor_.iter), TrCalm=f(tr[ru], 3), TrCrisis=f(tr[kr], 3),
         PStayCalm=f(hmm2.transmat_[ru, ru], 3), PStayCrisis=f(hmm2.transmat_[kr, kr], 3),
         LLone=f(L1, 2), LLtwo=f(L2, 2), BICone=f(B1, 2), BICtwo=f(B2, 2), DBICone=f(B1 - B2, 2),
         KOne="9", KTwo="21", NSwitch=str(len(sw)), NSeg=str(len(segs)), NCrisisEp=str(len(clen)),
         CrisisEpLengths=", ".join(map(str, clen)), NCrisisDays=str(int(crisis.sum())),
         NCalmDays=str(int((~crisis).sum())),
         Decisive=f(100 * np.mean((post > 0.9) | (post < 0.1)), 1))
M["KOne"], M["KTwo"] = "9", "21"
# check hand count of free parameters against hmmlearn's internal count
assert abs((B1 + 2 * L1) / np.log(T) - 9) < 1e-9 and abs((B2 + 2 * L2) / np.log(T) - 21) < 1e-9
# 0.5-crossing (secondary definition)
cross = post > 0.5
M.update(NSwitchCross=str(int(np.sum(np.diff(cross.astype(int)) != 0))), NCrisisDaysCross=str(int(cross.sum())),
         NDisagree=str(int(np.sum(cross != crisis))))

rob = pd.read_csv(ABG / "robustheit_startwerte.csv")
M.update(NStarts=str(len(rob)), NStartsConv=str(int(rob["konvergiert"].sum())),
         NStartsSame=str(int(rob["pfad_identisch"].sum())),
         NStartsIdxZero=str(int((rob["krisenindex"] == 0).sum())))

# crisis tags (one-sided check)
tags = pd.read_csv(CODE / "context_events.csv", parse_dates=["date"])
tagged = dates.isin(tags["date"]).to_numpy()
win = ((dates >= tags["date"].min()) & (dates <= tags["date"].max())).to_numpy()
M.update(NTags=str(len(tags)), NTagsTD=str(int(tagged.sum())), NWindowDays=str(int(win.sum())),
         TagHit=f(np.mean(post[tagged] > 0.5), 3), WinHit=f(np.mean(post[win] > 0.5), 3),
         BaseAll=f(np.mean(post > 0.5), 3), TagHitEight=f(np.mean(post[tagged] > 0.8), 3))
# K5 (01.10.2026): month split of the tagged window (presentation only)
aprmay = win & (dates < "2026-06-01").to_numpy(); junw = win & (dates >= "2026-06-01").to_numpy()
M.update(NWinAprMay=str(int(aprmay.sum())), NWinAprMayHit=str(int((post[aprmay] > 0.5).sum())),
         NWinJune=str(int(junw.sum())), NWinJuneHit=str(int((post[junw] > 0.5).sum())),
         NTagJune=str(int((tagged & junw).sum())), BaseAllPct=f(100 * np.mean(post > 0.5), 0))
assert (post[aprmay] > 0.5).all(), "main.tex says 'on every one of the ... days in April and May'"

# ---------------- Events -----------------------------------------------------------------------
ke = pd.read_csv(CODE / "key_events.csv", parse_dates=["date"])
pos = np.searchsorted(dates.to_numpy(), ke["date"].to_numpy(), side="left")
assert (pos < T).all()
M.update(NEvents=str(len(ke)), NEventsTD=str(int(ke["date"].isin(dates).sum())),
         NEventDays=str(len(np.unique(pos))),
         NEventsLate=str(int((ke["date"] >= "2026-04-01").sum())),
         NEventsEarly=str(int((ke["date"] < "2026-04-01").sum())))
# Section 2: 10Y AAA spot-rate move on event trading days vs. median absolute daily move (bp)
d10 = (y.set_index("date")["10Y"].diff() * 100).iloc[1:]
med10 = d10.abs().median()
ev_td = ke.loc[ke["date"].isin(dates), "date"]
M.update(NEventsSmallMove=str(int((d10.loc[ev_td].abs() < med10).sum())), MedAbsTen=f(med10, 1))
# Section 2: persistence of the level and slope scores (first-order autocorrelation, levels)
S_lev = pca.transform(StandardScaler().fit_transform(y[cols]))
M.update(PCacfOne=f(np.corrcoef(S_lev[:-1, 0], S_lev[1:, 0])[0, 1], 2),
         PCacfTwo=f(np.corrcoef(S_lev[:-1, 1], S_lev[1:, 1])[0, 1], 2))
# Section 2: window of the crisis tags
M.update(TagStart=tags["date"].min().strftime("%-d %B %Y"), TagEnd=tags["date"].max().strftime("%-d %B %Y"))

late = (ke["date"] >= "2026-04-01").to_numpy(); june = (ke["date"] >= "2026-06-01").to_numpy()
_mask2 = np.zeros(T, bool)
for s_ in sw: _mask2[max(0, s_ - 2):min(T, s_ + 3)] = True
near = _mask2[pos]
M.update(NEventsJune=str(int(june.sum())), NSwitchJune=str(int((dates[sw] >= "2026-06-01").sum())),
         NHitsLate=str(int((near & late).sum())), NHitsEarly=str(int((near & ~late).sum())),
         NLateCrisis=str(int(crisis[pos][late].sum())),
         CrisisShareJune=f(100 * crisis[(dates >= "2026-06-01").to_numpy()].mean(), 0))
# ---------------- Rotation test (Table 1) - independent recomputation of the primary cell ------
rt = pd.read_csv(ABG / "rotationstest.csv")
mask = np.zeros(T, bool)
for s in sw: mask[max(0, s - 2):min(T, s + 3)] = True
cnt = np.zeros(T, int); np.add.at(cnt, pos, 1)
Tobs = int((cnt * mask).sum())
null = np.array([int((np.roll(cnt, t) * mask).sum()) for t in range(T)])
p = np.mean(null >= Tobs)
prim = rt[rt["rolle"] == "TEST"].iloc[0]
assert Tobs == prim["T_obs"] and abs(p - prim["p"]) < 5e-5 and mask.sum() == prim["mask_tage"]
M.update(Tobs=str(Tobs), ETprim=f(prim["E_T_H0"], 2), Pprim=f(prim["p"], 4), NullMin=str(null.min()),
         NullMax=str(null.max()), NullGE=str(int((null >= Tobs).sum())), MinP=f(1 / T, 5))
# K7 (01.10.2026): source check of 1 October 2026 - the event recorded on 2026-06-07 occurred late on 2026-06-05.
# Presentation only: primary cell recomputed with that one date replaced; key_events.csv and the registered test unchanged.
_e3 = ke["date"] == pd.Timestamp("2026-06-07")
assert _e3.sum() == 1
pos_alt = np.searchsorted(dates.to_numpy(), ke["date"].where(~_e3, pd.Timestamp("2026-06-05")).to_numpy(), side="left")
cnt_alt = np.zeros(T, int); np.add.at(cnt_alt, pos_alt, 1)
Tobs_alt = int((cnt_alt * mask).sum())
null_alt = np.array([int((np.roll(cnt_alt, t) * mask).sum()) for t in range(T)])
assert Tobs_alt == Tobs, "main.tex says T_obs is unchanged under the corrected date"
M.update(PaltSrc=f(np.mean(null_alt >= Tobs_alt), 4))
lab = {"viterbi": "Viterbi", "kreuzung": "0.5 crossing", "alle26": "all rows (26)", "episoden22": "one per episode (22)"}
rows = []
for _, z in rt.iterrows():
    cells = [lab[z.wechsel], lab[z.ereignisse], str(z.k), str(z.mask_tage), str(z.T_obs), f"{z.E_T_H0:.3f}",
             f"{z.T_obs / z.E_T_H0:.2f}", f"{z.p:.4f}"]
    if z.rolle == "TEST": cells = [r"\textbf{" + c + "}" for c in cells]
    rows.append(" & ".join(cells) + r" \\")
(OUT / "tables" / "tab_rotation.tex").write_text("\n".join(rows) + "\n")
lowp = rt[(rt["rolle"] != "TEST") & (rt["p"] < 0.05)]
M.update(NLowP=str(len(lowp)), LowPa=f(lowp["p"].min(), 4), LowPb=f(lowp["p"].max(), 4),
         RatioMin=f((rt.T_obs / rt.E_T_H0).min(), 2), RatioMax=f((rt.T_obs / rt.E_T_H0).max(), 2))
# K5 (01.10.2026): descriptive statistics of the existing exact null distribution and of the clustering of
# events and transitions. Presentation only: no new test, no change to any registered decision.
M.update(NullSD=f(null.std(), 1),  # SD over all N circular shifts
         IndepSD=f(np.sqrt(len(ke) * mask.mean() * (1 - mask.mean())), 1))  # events placed independently (binomial)
tcrit = next(t for t in range(null.max() + 2) if np.mean(null >= t) <= 0.05)
M.update(TcritPrim=str(tcrit), PcritPrim=f(np.mean(null >= tcrit), 4), RatioCritPrim=f(tcrit / prim["E_T_H0"], 1))
junetd = (dates.iloc[pos] >= "2026-06-01").to_numpy()  # events by ASSIGNED trading day (basis of the test)
M.update(NEventsJuneTD=str(int(junetd.sum())),
         NDaysJune=str(int((dates >= "2026-06-01").sum())), NSwitchEarly=str(int((dates[sw] < "2025-05-01").sum())))
# where the June event cluster lands under the shifts with T >= T_obs (shifted median position of the June events)
jmed = int(np.median(pos[junetd])); hi = np.flatnonzero(null >= Tobs)
land = dates.iloc[(jmed + hi) % T]
M["NHighEarly"] = str(int((land < "2025-05-01").sum()))
rate = ke["event"].str.endswith(("_cut", "_hike")).to_numpy()  # rate changes (K1); other early events: K2/K3 by judgement
M["NRetroHits"] = str(int((near & ~late & ~rate).sum()))
_mjun = np.zeros(T, bool)
for s_ in sw[(dates[sw] >= "2026-06-01").to_numpy()]: _mjun[max(0, s_ - 2):min(T, s_ + 3)] = True
assert (near & late).sum() == (_mjun[pos] & late).sum(), "main.tex says all late matches are near the June transitions"

# ---------------- Stage 2 (Tables 2, 3) --------------------------------------------------------
ar = pd.read_csv(ABG / "ar1_schaetzung.csv", index_col=0)
bs = pd.read_csv(ABG / "bootstrap_ergebnisse.csv", index_col=0)
bic2 = pd.read_csv(ABG / "bic_stage2.csv", index_col=0)
for R, tag in (("Krise", "K"), ("ruhig", "R")):
    z = ar.loc[R]
    M[f"b{tag}"] = f(z["b"], 5); M[f"n{tag}"] = str(int(z["n Paare"]))
    M[f"a{tag}"] = f(z["a [1/J]"], 2); M[f"s{tag}"] = f(z["sigma [pp/sqrtJ]"], 3)
    M[f"LU{tag}"] = f(z["n Paare"] * (z["b"] - 1), 1)
    M[f"TC{tag}"] = f(4 / (z["n Paare"] / 252), 1)
    M[f"LBfive{tag}"] = f(z["LB(5) p"], 3); M[f"ARCH{tag}"] = f(z["ARCH-LM(1) p"], 3)
    M[f"BP{tag}"] = f(z["BP (Niveau) p"], 3)
M["JBK"] = "<0.001" if ar.loc["Krise", "JB p"] < 1e-3 else f(ar.loc["Krise", "JB p"], 3)
M["JBR"] = f(ar.loc["ruhig", "JB p"], 2)
assert int(ar.loc["Krise", "n Paare"]) + int(ar.loc["ruhig", "n Paare"]) + len(sw) == T - 1

names = {"a_Krise": r"$a$, crisis", "a_ruhig": r"$a$, calm", "a_Krise/a_ruhig": r"$a_{\mathrm{crisis}}/a_{\mathrm{calm}}{}^{\dagger}$",
         "sigma_Krise": r"$\sigma$, crisis", "sigma_ruhig": r"$\sigma$, calm",
         "sigma_Krise/sigma_ruhig": r"$\sigma_{\mathrm{crisis}}/\sigma_{\mathrm{calm}}$"}
dec = {"a": 2, "s": 3}
rows = []
for k in ["a_Krise", "a_ruhig", "a_Krise/a_ruhig", "sigma_Krise", "sigma_ruhig", "sigma_Krise/sigma_ruhig"]:
    z = bs.loc[k]; d = 3 if k.startswith("sigma") and "/" not in k else 2
    rows.append(" & ".join([names[k], f(z.Punkt, d), f"[{f(z.BCa_unten, d)}, {f(z.BCa_oben, d)}]",
                            f"{100*z.Perzentil_unten:.2f} / {100*z.Perzentil_oben:.2f}", f(z.Verzerrung, d),
                            f(z.z0, 3), f(z.Beschleunigung, 4), f"{z.MC_SE_unten:.3f} / {z.MC_SE_oben:.3f}"]) + r" \\")
    if k == "a_Krise/a_ruhig": rows.append(r"\midrule")
(OUT / "tables" / "tab_params.tex").write_text("\n".join(rows) + "\n")
for k, tag in [("a_Krise", "aK"), ("a_ruhig", "aR"), ("a_Krise/a_ruhig", "aRatio"), ("sigma_Krise", "sK"),
               ("sigma_ruhig", "sR"), ("sigma_Krise/sigma_ruhig", "sRatio")]:
    z = bs.loc[k]; d = 3 if tag in ("sK", "sR") else 2
    M[f"CI{tag}lo"], M[f"CI{tag}hi"], M[f"Pt{tag}"] = f(z.BCa_unten, d), f(z.BCa_oben, d), f(z.Punkt, d)
    M[f"Bias{tag}"] = f(z.Verzerrung, 2); M[f"Mean{tag}"] = f(z.Bootstrap_Mittel, 2)
    M[f"Plo{tag}"] = f(100 * z.Perzentil_unten, 2); M[f"Phi{tag}"] = f(100 * z.Perzentil_oben, 2)
M["PtsRatioRound"] = f(bs.loc["sigma_Krise/sigma_ruhig", "Punkt"], 1)
# Diagnostic added 01.10.2026 (Pruefbericht K6, after all other computations; not registered, no test decision):
# share of the variance of daily 3M changes spanned by the three factor changes (OLS with intercept, full sample)
d3m = np.diff(y["3M"].to_numpy())
assert len(d3m) == len(X)
Z = np.column_stack([np.ones(len(X)), X])
res = d3m - Z @ np.linalg.lstsq(Z, d3m, rcond=None)[0]
M["RsqShort"] = f(1 - res.var() / d3m.var(), 3)
rep = np.load(ABG / "bootstrap_referenz_replikationen.npz")
M.update(NbOneK=str(int((rep["b_Krise"] >= 1).sum())), NbOneR=str(int((rep["b_ruhig"] >= 1).sum())),
         MeanbK=f(rep["b_Krise"].mean(), 4))
# Gegenrechnung Beschleunigung: exakte (numerische) statt Jackknife-Einflusswerte (Code/einfluss_pruefung.py).
# Aufgerundet, weil der Text "at most" sagt.
infl = pd.read_csv(ABG / "einfluss_pruefung.csv", index_col=0)
assert infl["d_kleiner_MC_SE"].all()
M.update(InflDacc=f(np.ceil(infl["d_acc"].max() * 1e4) / 1e4, 4),
         InflDlim=f(np.ceil(infl[["d_unten", "d_oben"]].to_numpy().max() * 1e3) / 1e3, 3))

rows = []
for mod, name in [("ein Regime", "one regime"), ("zwei Regime", "two regimes")]:
    z = bic2.loc[mod]
    rows.append(f"Stage 2 (conditional on path) & {name} & {int(z.k)} & {int(z.n)} & {f(z.lnL,2)} & {f(z.BIC,2)} \\\\")
rows.insert(0, f"Stage 1 (HMM, factor changes) & one state & 9 & {T} & {f(L1,2)} & {f(B1,2)} \\\\")
rows.insert(1, f"Stage 1 (HMM, factor changes) & two states & 21 & {T} & {f(L2,2)} & {f(B2,2)} \\\\ \\midrule")
(OUT / "tables" / "tab_bic.tex").write_text("\n".join(rows) + "\n")
M.update(DBICtwo=f(bic2.loc["ein Regime", "BIC"] - bic2.loc["zwei Regime", "BIC"], 2), NPairsKept=str(int(bic2.loc["ein Regime", "n"])),
         NSeams=str(len(sw)), SeamShare=f(100 * len(sw) / (T - 1), 2))

# ---------------- Figure 1 --------------------------------------------------------------------
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
plt.rcParams.update({"font.family": "serif", "font.size": 8.5, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b", "xtick.color": "#52514e",
                     "ytick.color": "#52514e", "axes.linewidth": 0.6})
BLUE, ORANGE, INK = "#2a78d6", "#eb6834", "#0b0b0b"
fig, ax = plt.subplots(2, 1, figsize=(6.3, 4.1), sharex=True, gridspec_kw={"height_ratios": [1.25, 1], "hspace": 0.12})
for a_ in ax:
    for s in segs:
        if crisis[s[0]]:
            a_.axvspan(dates[s[0]] - pd.Timedelta(hours=12), dates[s[-1]] + pd.Timedelta(hours=12),
                       color=ORANGE, alpha=0.16, lw=0)
    a_.grid(axis="y", color="#e4e3df", lw=0.5); a_.set_axisbelow(True)
ax[0].plot(dates, r, color=INK, lw=1.1)
ax[0].set_ylabel("3M AAA spot rate (%)")
ev_dates = dates[np.unique(pos)]
ax[0].plot(ev_dates, np.full(len(ev_dates), r.min() - 0.06), "|", color=INK, ms=7, mew=1.0)
ax[0].set_ylim(r.min() - 0.12, r.max() + 0.05)
ax[1].plot(dates, post, color=BLUE, lw=1.1)
ax[1].set_ylabel("Smoothed P(crisis)"); ax[1].set_ylim(-0.03, 1.03)
ax[1].xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 4, 7, 10]))
ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
ax[0].legend(handles=[Patch(color=ORANGE, alpha=0.3, label="crisis regime (Viterbi)"),
                      Line2D([], [], marker="|", ls="", color=INK, ms=7, label="documented event (trading day)")],
             loc="lower left", bbox_to_anchor=(0, 1.0), ncol=2, frameon=False, fontsize=7.5)
fig.align_ylabels(ax)
fig.savefig(OUT / "figures" / "fig1_regime_path.pdf", bbox_inches="tight")
fig.savefig(OUT / "figures" / "fig1_regime_path.png", dpi=160, bbox_inches="tight")

# ---------------- write macros -----------------------------------------------------------------
lines = ["% generated by build_exhibits.py - do not edit by hand"]
for k in sorted(M):
    assert k.isalpha(), k
    lines.append(f"\\newcommand{{\\{k}}}{{{M[k]}}}")
(OUT / "numbers.tex").write_text("\n".join(lines) + "\n")
print(len(M), "macros written")
for k in sorted(M): print(k, "=", M[k])
