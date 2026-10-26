# Source Map: B3 Atomic Physics — P. Ewart
**File:** `lecture_notes_pdf/B3_Atomic_Physics_(Ewart).pdf` (62 pp., LaTeX, 2011/2020)
**Merged TeX:** `sources/B3_Atomic_Physics_(Ewart).defaultmethod.tex`
**Locator:** [[sources/B3_Atomic_Physics_(Ewart)_Locator]]
**Course label:** B2.III Atomic Physics (Ewart's naming; Oxford now calls this B3)

---

## §1: Introduction (p.3)
Two-level atom model. Oscillating charge cloud → electric dipole radiation. Motivation for selection rules (preview only).

---

## §2: Radiation and Atoms (pp.3–8)

### §2.1 Width and Shape of Spectral Lines (pp.3–5)
- **Homogeneous broadening:** affects all atoms identically
  - **Lifetime (natural) broadening** (§2.1.1, p.3–4): $\Delta\omega \sim 1/\tau$. Lorentzian lineshape. $\tau \sim 10^{-8}$ s typical.
  - **Collision/pressure broadening** (§2.1.2, p.4–5): phase disruption. Also Lorentzian. $\tau_c \sim 10^{-10}$ s at atm pressure.
- **Inhomogeneous broadening:** affects different atoms differently
  - **Doppler broadening** (§2.1.3, p.5): velocity spread → Gaussian lineshape. Often dominates.

### §2.2 Atomic Orders of Magnitude (pp.5–6)
Key atomic scales: Bohr radius $a_0$, Rydberg $R$, fine structure constant $\alpha$, Bohr magneton $\mu_B$. Useful for estimating relative sizes of effects.

### §2.3–2.5: Central Field Approximation — introduction (pp.6–8)
Preview of the central field idea. Full treatment in §3.

---

## §3: The Central Field Approximation (pp.9–16)

### §3.1 Physics of the Wavefunctions (pp.9–12)
- Energy depends on both $n$ and $l$ (unlike hydrogen). Lower $l$ = more core penetration = lower energy.
- Angular momentum: same $Y_l^m$ as hydrogen. Good QNs: $n, l, m_l$.
- Radial wavefunctions: $\tilde{R}_{nl}(r)$ — solve via $P(r) = r\tilde{R}(r)$ with effective potential.
- Parity: $(-1)^l$ from $Y_l^m$.

### §3.2 Multi-electron Atoms (pp.12–14)
- N-electron Hamiltonian → central field $H_{CF}$ + residual electrostatic $\Delta H_{RE}$.
- Effective potential $U(r)$: $\to -Ze^2/4\pi\epsilon_0 r$ as $r\to 0$; $\to -e^2/4\pi\epsilon_0 r$ as $r\to\infty$.
- Separability of $H_{CF}$ → electron configuration e.g. $[1s^22s^22p^6]3s$ for Na.
- Pauli exclusion: wavefunction antisymmetry → Slater determinant.
- Periodic table: shells fill in order of increasing energy (dependent on $n$ AND $l$).

### §3.3 Quantum Defect — Alkalis (pp.15–16)
$$E(n,l) = -\frac{R}{(n-\delta_l)^2}, \quad n^* \equiv n - \delta_l$$
$\delta_l$ depends mostly on $l$, not $n$. Explains why alkali ionisation energies are similar across the series.

---

## §4: Spin-Orbit Interaction (pp.17–29)

### §4.1–4.2 Physics and derivation (pp.17–24)
- Electron orbiting nucleus sees B field via Lorentz: $\mathbf{B} = -\mathbf{v}\times\mathbf{E}/c^2$
- Interaction Hamiltonian: $\Delta H_{SO} = \beta(r)\hat{l}\cdot\hat{s}$ (after Thomas precession factor of ½)
- Need DPT because states with same $n,l$ are degenerate.
- **Vector model:** $\hat{l}, \hat{s}$ precess around $\hat{j} = \hat{l}+\hat{s}$. Good QNs: $n,l,s,j,m_j$.

### §4.3 Spin-Orbit Summary (p.25)
$$\Delta E_{SO} = \frac{1}{2}\beta[j(j+1) - l(l+1) - s(s+1)]$$
$$\beta = \frac{Z^4\alpha^2 R}{n^3 l(l+\tfrac{1}{2})(l+1)}$$
**Interval rule:** $E(j) - E(j-1) = \beta j$

### §4.4 Spin-Orbit Splitting in Alkalis (pp.25–27)
$$\Delta^2 E = \alpha^2 R \frac{Z_i^2 Z_o^2}{(n^*)^3 l(l+1)}$$
where $Z_i \sim Z$ (inner, penetration), $Z_o \sim 1$ (outer, screening).

### §4.5 Spectroscopic Notation (pp.27–29)
Term symbol $^{2S+1}L_J$ for single electron: $^2P_{1/2}$, $^2P_{3/2}$ etc. $L=0,1,2,3 \leftrightarrow S,P,D,F$.

---

## §5: Two-Electron Atoms — LS Coupling (pp.30–36)

### §5.1–5.2 Magnesium and Electrostatic Perturbation (pp.30–32)
Two perturbations compete: $\Delta H_{RE}$ (residual electrostatic) and $\Delta H_{SO}$.
- **LS coupling regime:** $\Delta H_{RE} \gg \Delta H_{SO}$ → couple orbital momenta first: $\hat{L} = \hat{l}_1 + \hat{l}_2$, then spin: $\hat{S} = \hat{s}_1 + \hat{s}_2$, then $\hat{J} = \hat{L}+\hat{S}$.

### §5.3 Symmetry — Singlet and Triplet (pp.32–33)
- Spatial wavefunction: symmetric (+) or antisymmetric (−)
- Spin: singlet $S=0$ (antisymmetric) or triplet $S=1$ (symmetric)
- Total wavefunction must be antisymmetric (Pauli) → singlet with symmetric spatial, triplet with antisymmetric spatial.
- **Exchange energy** $K$: energy difference between singlet and triplet (electrostatic in origin, not magnetic!).

### §5.4–5.5 Orbital and Spin-Orbit Effects (pp.33–36)
- $L$ determines orbital symmetry → affects electrostatic energy.
- Spin-orbit in LS coupling: $\Delta H_{SO} \propto \hat{L}\cdot\hat{S}$, interval rule still holds.
- Term $^{2S+1}L_J$: $|L-S| \leq J \leq L+S$.

---

## §6: Nuclear Effects — Hyperfine Structure (pp.37–41)

### §6.1–6.4 Hyperfine Structure (pp.37–40)
- Nuclear spin $I$ couples to $J$: $\hat{F} = \hat{I} + \hat{J}$, $|I-J| \leq F \leq I+J$.
- Splitting scale: $\sim 10^{-6}$ eV (vs $\sim 10^{-3}$ eV for fine structure) — much smaller.
- Interval rule: $\Delta E \propto F$.
- Used to measure $I$: count hfs levels, use relative intensities $\propto (2F+1)$.

### §6.5 Isotope Effects (pp.40–41) — **NON-EXAMINABLE**

---

## §7: Selection Rules (pp.42–43)

| Rule | Single electron | Many electrons |
|------|----------------|----------------|
| Parity | must change | must change (Laporte) |
| $l$ | $\Delta l = \pm 1$ | — |
| $L$ | — | $\Delta L = 0, \pm 1$ |
| $J$ | \multicolumn{2}{c}{$\Delta J = 0, \pm 1$ (not $0\to 0$)} |
| $M_J$ | \multicolumn{2}{c}{$\Delta M_J = 0, \pm 1$ (not $0\to 0$ if $\Delta J=0$)} |
| $S$ | — | $\Delta S = 0$ |
| Config | one electron changes | one electron changes |

---

## §8: Atoms in Magnetic Fields (pp.44–55)

### §8.1 Weak Field, No Spin (pp.44–46)
Normal Zeeman effect. $\Delta E = m_l \mu_B B$. Three lines (triplet).

### §8.2 Weak Field With Spin — Anomalous Zeeman (pp.46–50)
$B$ field perturbation smaller than spin-orbit → $J$ is good QN.
$$\Delta E = g_J \mu_B B M_J$$
$$g_J = 1 + \frac{J(J+1)+S(S+1)-L(L+1)}{2J(J+1)} \quad \text{(Landé g-factor)}$$
Pattern: $2J+1$ sublevels. Transitions by $\Delta M_J = 0, \pm 1$ → multiple lines (anomalous pattern).
Polarization: $\Delta M_J = 0$ → $\pi$ (parallel to $B$, unshifted); $\Delta M_J = \pm 1$ → $\sigma^\pm$ (circular).

### §8.3 Strong Fields — Paschen-Back (pp.50–52)
$B$ field perturbation larger than spin-orbit → $L, S$ decouple. Good QNs: $M_L, M_S$.
$$\Delta E = \mu_B B(M_L + g_s M_S) \approx \mu_B B(M_L + 2M_S)$$
Returns to near-normal Zeeman pattern (three groups).

### §8.4 Intermediate Fields (pp.52)
Neither limit applies. Numerical treatment or perturbation theory in chosen basis.

### §8.5 Magnetic Field Effects on Hyperfine Structure (pp.52–55)
- Weak field: $F$ good QN, $\Delta E = g_F \mu_B B M_F$.
- Strong field: $F$ breaks down; $J, m_J, I, m_I$ become good QNs.

---

## §9: X-Rays (pp.56–62)

### §9.1–9.3 X-ray Spectra and Series (pp.56–58)
- Inner shell vacancy (e.g. remove K electron) → outer electron falls in → X-ray photon emitted.
- Series labelled by vacancy: K-series (transition to $n=1$), L-series ($n=2$), etc.
- **Moseley's law:** $\sqrt{\nu} = c(Z - \sigma_n)$ where $\sigma_n$ is a screening constant.
- Fine structure: spin-orbit splitting of the levels involved.

### §9.4 X-ray Absorption (pp.58)
Absorption edges at energies corresponding to shell ionisation thresholds.

### §9.5 Auger Effect (pp.59–62)
Radiationless alternative: vacancy filled, energy transferred to another electron which is ejected (Auger electron). Competes with X-ray emission. More probable for lighter elements.
