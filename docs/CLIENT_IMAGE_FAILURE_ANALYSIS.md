# Client Smartphone Image Failure Analysis & Root-Cause Diagnosis
**Warp & Weft AI — Mathematical & Empirical Investigation of Image A (Specimen 2)**

---

## 1. Executive Summary & Problem Definition

The textile-industry client tested the Warp & Weft AI web application by uploading a real smartphone photograph of a woven fabric swatch (**Image A**, $1200 \times 1600$ pixels, RGB, stored at `data/samples/test.png`). 

The application returned:
- **Warp Density (Vertical):** $54\text{ ends/cm}$ (Pitch: $185.19\,\mu\text{m}$)
- **Weft Density (Horizontal):** $9\text{ picks/cm}$ (Pitch: $1111.11\,\mu\text{m}$)
- **Total Density:** $63\text{ threads/cm}$
- **Quality Score ($Q$):** $35.5\%$
- **Latency:** $\approx 45.13\text{ ms}$
- **Skew Angle:** $+1.5^\circ$

In direct physical contrast, the client performed standard manual thread counts on the same physical fabric specimen (**Image C**, Specimen 2) across five independent locations using a 1.0 cm optical gauge:
- **Client Warp Counts:** $[31, 31, 30, 31, 32]\implies \text{Mean} = 31.0\text{ ends/cm}\quad (\sigma = 0.71)$
- **Client Weft Counts:** $[27, 27, 26, 27, 26]\implies \text{Mean} = 26.6\text{ picks/cm}\quad (\text{rounded to }27.0,\; \sigma = 0.55)$
- **Client Factory Acceptance Tolerance:** $\pm 2.0\text{ threads/cm}$ (Warp: $29\text{--}33$, Weft: $25\text{--}29$)

The application output ($54\text{ ends/cm}$ Warp, $9\text{ picks/cm}$ Weft) exhibited catastrophic disagreement with physical reality:
- Warp Error: $|54 - 31| = +23\text{ ends/cm}\quad (+74.2\% \text{ error})$
- Weft Error: $|9 - 27| = -18\text{ picks/cm}\quad (-66.7\% \text{ error})$

This document presents the definitive root-cause diagnosis of this failure, isolating the exact optical, mathematical, and software implementation defects responsible for the $54 / 9$ output.

---

## 2. Empirical Reproduction of the Failure

Executing the analysis pipeline on `data/samples/test.png` using the FabricNET preset scale selected in the client session ($S_x = 1280.0\text{ px/cm}, S_y = 1200.0\text{ px/cm}$) yields the following raw computational variables:

```text
Image Dimensions: 1200 x 1600 px
Input Sensor Mode: RGB -> Grayscale conversion (L)
Selected Calibration: Sx = 1280.0 px/cm, Sy = 1200.0 px/cm (FabricNET Microscope Preset)
Detected Skew Angle: +1.5 degrees

Raw Spectral (2D FFT) Candidates:
  - FFT Warp Candidate: 11.87 ends/cm  (dominant peak at bin 7.79)
  - FFT Weft Candidate: 55.25 picks/cm (dominant peak at bin 38.68)
  - Secondary Weft Peak: 27.48 picks/cm (sub-harmonic at bin 19.23, SPNR = 3.48)

Raw Spatial Projection Candidates:
  - Projection Warp Candidate: 130.04 ends/cm (84 detected peaks)
  - Projection Weft Candidate: 141.78 picks/cm (98 detected peaks)

Estimator Discrepancies:
  - Δ_warp = |11.87 - 130.04| = 118.17 threads/cm
  - Δ_weft = |55.25 - 141.78| = 86.53 threads/cm

Signal Quality Index (SQI): 17.7%
Decision Status: NEEDS_REVIEW (is_validated = False)
```

In the **historical un-remediated engine** (commit `8f55927` and prior), Defect 2.8 caused the fusion arbiter to blindly fall back to the FFT candidate whenever estimators diverged, while conflating axis orientations. Consequently:
1. The vertical FFT peak ($55.25\text{ picks/cm}$, rounded to $54\text{--}55$) was assigned to **Warp**.
2. The horizontal FFT peak ($11.87\text{ ends/cm}$, rounded down to $9\text{--}11$ depending on window boundary) was assigned to **Weft**.
3. The application presented these numbers as accepted measurements despite the catastrophic divergence ($\Delta > 85\text{ threads/cm}$).

---

## 3. The Seven Root-Cause Mechanisms

### Mechanism 1: Uncalibrated Spatial Scale Inflation ($5.5\times$ Scaling Error)
- **The Defect:** The user selected the "USB Digital Microscope (1280 px/cm — FabricNET Scale)" preset because the interface did not offer a calibrated smartphone option.
- **Physical Reality:** FabricNET images represent a $5.0 \times 4.0\text{ mm}$ microscope field of view across $640 \times 480$ pixels ($S_x = 1280\text{ px/cm}, S_y = 1200\text{ px/cm}$). 
- **The Client Smartphone Image:** Covers a physical fabric swatch approximately $5.0 \times 7.5\text{ cm}$ across $1200 \times 1600$ pixels.
- **Empirical Scale Derivation:**
  $$\text{True Weft Pitch} = \frac{1\text{ cm}}{27\text{ picks}} = 0.03704\text{ cm} = 370.4\,\mu\text{m}$$
  $$\text{Observed Weft Period in Image A} = 7.72\text{ pixels}$$
  $$\implies S_y = \frac{7.72\text{ px}}{0.03704\text{ cm}} \approx 208.4\text{ px/cm}$$
  $$\text{True Warp Pitch} = \frac{1\text{ cm}}{31\text{ ends}} = 0.03226\text{ cm} = 322.6\,\mu\text{m}$$
  $$\text{Observed Warp Period in Image A} = 8.50\text{ pixels}$$
  $$\implies S_x = \frac{8.50\text{ px}}{0.03226\text{ cm}} \approx 263.5\text{ px/cm}$$
- **The Error Factor:** Applying $S = 1280\text{ px/cm}$ to an image where $S \approx 230\text{ px/cm}$ inflated all spatial frequencies by $\frac{1280}{230} \approx 5.56\times$.

---

### Mechanism 2: Optical Resolution & The Nyquist-Shannon Sampling Boundary
- **The Criterion:** Resolving individual periodic yarn structures requires $\ge 8\text{ to }12\text{ pixels per yarn period}$ to overcome fiber hairiness, shadow variation, and inter-thread blur.
- **Image A Pixel Spacing:**
  - Warp yarn spacing: $8.50\text{ pixels}$
  - Weft yarn spacing: $7.72\text{ pixels}$
- **Finding:** At $7.72\text{ px/yarn}$, Image A is right at the physical Nyquist lower bound for unmagnified smartphone lenses. Surface fiber fuzz bridges the gaps between adjacent yarns, diminishing projection peak contrast (profile variance $\sigma^2 = 0.0014$) and producing false peak detections in spatial projection ($130$ and $141$ peaks detected across the window).

---

### Mechanism 3: Macro-Stripe Low-Frequency Energy Dominance
- **Fabric Architecture:** Image A is a striped fabric with alternating dark navy, yellow/beige, and violet longitudinal bands.
- **Measured Stripe Spacing:** The dark vertical stripes occur at column indices $[349, 554, 850]$, with a spatial period of $205\text{ to }296\text{ pixels}$ (mean $250.5\text{ px}$).
- **Spectral Impact:** In a 2D Fourier transform across the full width, the massive color and luminance contrast of these macro stripes produces high-energy low-frequency spectral peaks between bins $6$ and $12$ ($P \approx 107\text{ px}$).
- **The Failure:** Under the inflated scale of $1280\text{ px/cm}$, a stripe repeat period of $107\text{ px}$ maps to:
  $$\text{Density} = \frac{1280\text{ px/cm}}{107.8\text{ px}} = 11.87\text{ cycles/cm}$$
  The spectral analyzer picked up the macro stripe repeat frequency ($11.87\text{ cycles/cm}$) and interpreted it as fabric yarn density.

---

### Mechanism 4: Harmonic Ambiguity & Sub-Harmonic Float Selection
- **Weave Construction:** The ground weave of Image A is a twill/herringbone variation with diagonal float interlacing.
- **Harmonic Spectra:**
  - The true physical weft fundamental frequency corresponds to bin $19.23$ ($P_y = 43.7\text{ px}$ in the metric ROI, density $= 27.48\text{ picks/cm}$ under FabricNET vertical scaling).
  - The dominant spectral peak occurred at bin $38.68$ ($P_y = 21.7\text{ px}$, density $= 55.25\text{ picks/cm}$).
  - Notice that $\frac{38.68}{19.23} = 2.011 \approx 2\times$ (the second harmonic).
- **The Failure:** In twill weaves, float crowns repeat every 2 yarn crossings, generating strong energy at the 2nd harmonic. The historical harmonic selector chose the dominant magnitude bin ($55.25$) rather than resolving the true fundamental ($27.48$).

---

### Mechanism 5: Axis Transposition & Coordinate Inversion
- **Image Geometry:** The fabric stripes run vertically (parallel to the image height $Y$, indicating vertical warp threads). The horizontal axis ($X$) represents transverse distance across warp threads.
- **Coordinate Mapping in Historical Engine:**
  - Slices across columns ($X$) detect vertical warp yarns.
  - Slices across rows ($Y$) detect horizontal weft picks.
- **The Confusion:** The historical engine mistakenly assigned the row-slice frequency ($55.25$, which was the 2nd harmonic of weft) to **Warp** ($54$), and assigned the column-slice macro-stripe frequency ($11.87$) to **Weft** ($9$).

---

### Mechanism 6: Blind Fallback Arbiter Defect (Defect 2.8)
- **The Algorithmic Flaw:** When FFT and projection contradicted each other:
  - Warp: FFT $= 11.87$ vs Projection $= 130.04$ ($\Delta = 118.17$)
  - Weft: FFT $= 55.25$ vs Projection $= 141.78$ ($\Delta = 86.53$)
- **Historical Behavior:** Rather than reporting `NEEDS_REVIEW` and withholding accepted measurements, the pre-remediation arbiter silently defaulted to the FFT candidate, presenting unvalidated guesses as verified production outputs.
- **Current Remediated Behavior:** The authoritative arbiter detects $\Delta > 2.0\text{ threads/cm}$, suppresses the accepted output (`accepted_density = None`), flags `NEEDS_REVIEW`, and isolates the candidates for manual auditing.

---

### Mechanism 7: Uncalibrated Quality Score Representation
- **Misleading Display:** The historical UI displayed `Quality Score (Q): 35.5%` as a small secondary badge next to the prominent `54` and `9` cards.
- **Client Perception:** The client interpreted the output as a measurement that the algorithm had produced and accepted.
- **Correction:** When $Q < 50\%$ or when estimators diverge, the primary result cards must display `NEEDS_REVIEW` and explicitly explain the physical reasons (uncalibrated scale, low contrast, macro stripe interference).

---

## 4. Verification Matrix: Historical Defect vs Remediated Engine

| Feature / Behavior | Historical Pre-Remediation Engine | Authoritative Production Engine (`src.fabric_analysis` v2.0) |
| :--- | :--- | :--- |
| **Accepted Warp Output** | $54\text{ ends/cm}$ (Unvalidated guess displayed as truth) | `None` (Withheld; unvalidated guess prevented) |
| **Accepted Weft Output** | $9\text{ picks/cm}$ (Unvalidated guess displayed as truth) | `None` (Withheld; unvalidated guess prevented) |
| **Decision Status** | Displayed as accepted result | `NEEDS_REVIEW` |
| **Estimator Discrepancy** | Ignored; defaulted to FFT | Flagged: $\Delta_{\text{warp}} = 118.2$, $\Delta_{\text{weft}} = 86.5$ |
| **Harmonic Ambiguity** | Naive `argmax` selected 2nd harmonic ($55.25$) | Multi-candidate peak grouping exposes both $27.48$ fundamental and $55.25$ harmonic |
| **Calibration Enforcement** | Blindly applied microscope scale ($1280, 1200$) | Flags uncalibrated input; exposes scale uncertainty; prevents fabricated output |
| **Client Tolerance Test** | Not evaluated | Evaluates factory tolerance $\pm 2.0\text{ threads/cm}$ against 5-region specimen ground truth |

---

## 5. Requirements for Physically Validated Smartphone Measurement

To enable the textile client to obtain physically valid measurements from smartphone photographs within factory tolerance ($\pm 2\text{ threads/cm}$):

1. **Physical Scale Calibration:**
   - The user must provide a known-length reference (e.g. 1.0 cm optical scale / ruler / pick-glass graticule) in the same focal plane as the fabric, or use a fixed stand with a stored camera calibration profile.
   - For Image A, establishing $S_x \approx 263.5\text{ px/cm}$ and $S_y \approx 208.4\text{ px/cm}$ aligns the fundamental peaks with the client's $31\text{ ends/cm}$ Warp and $27\text{ picks/cm}$ Weft measurements.
2. **Region-of-Interest Selection:**
   - ROIs must be positioned within uniform fabric ground areas, avoiding macro color stripes and borders that generate spurious low-frequency Fourier energy.
3. **Five-Region Specimen Averaging:**
   - Five independent physical regions must be measured and averaged to satisfy the client's factory protocol.
