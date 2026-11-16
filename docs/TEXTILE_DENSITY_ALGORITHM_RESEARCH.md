# Textile Warp and Weft Density Measurement: Algorithmic Research Note

## 1. Executive Summary & Problem Formulation
The automated inspection of yarn density in woven textile fabrics requires quantifying two orthogonal parameters:
1. **Warp Yarn Density ($N_{\text{warp}}$):** Number of longitudinal threads (ends) per unit length (e.g., ends/cm or ends/inch [EPI]).
2. **Weft Yarn Density ($N_{\text{weft}}$):** Number of transverse threads (picks) per unit length (e.g., picks/cm or picks/inch [PPI]).

When digitized through optical imaging (macro photography, digital microscopy, or flatbed scanning), a woven fabric presents a 2D semi-periodic intensity matrix $I(x,y)$. The physical yarn spacing $p_x, p_y$ (pitch in micrometers) relates to physical thread density $N$ and discrete pixel frequency $f$ via the spatial calibration scale $S = [S_x, S_y]$ in pixels/cm:
$$p_x = \frac{10,000}{N_{\text{warp}}} \, (\mu\text{m}), \quad p_y = \frac{10,000}{N_{\text{weft}}} \, (\mu\text{m})$$
$$N_{\text{warp}} = \frac{k_x \cdot S_x}{W}, \quad N_{\text{weft}} = \frac{k_y \cdot S_y}{H}$$
where $k_x, k_y$ represent the discrete Fourier transform (DFT) harmonic bin indices corresponding to fundamental yarn spacing over a crop window of size $W \times H$ pixels.

---

## 2. Comprehensive Literature Review & Methodological Analysis

### 2.1. Paper 1: Light Transmittance & Fourier Analysis
* **Citation:** Ajallouian, F., Tavanai, H., Palhang, M., et al. *"Automatic inspection of density in yarn-dyed fabrics by utilizing fabric light transmittance and Fourier analysis"*, *Applied Optics*, Vol. 54, Issue 4, pp. 966-972 (2015).
* **URL:** https://pubmed.ncbi.nlm.nih.gov/25967813/ | https://doi.org/10.1364/AO.54.000966
* **Mathematical Basis:**
  * Uses transmitted backlighting to create a high-contrast binary-like structure where yarn interstices act as light apertures and yarn cores act as opaque obstacles.
  * Applies a 2D Discrete Fourier Transform (2D-DFT) to the transmitted image.
  * Detects fabric skew angle $\theta$ directly from the angular distribution of the power spectrum:
    $$P(u, v) = |F(u, v)|^2$$
  * Performs inverse 2D-DFT (2D-IDFT) with band-selective filtering along the principal axes to reconstruct individual warp-only and weft-only images.
  * Computes 1D projection profiles from the reconstructed images and counts peaks/valleys.
* **Suitable Structures:** Plain weaves, yarn-dyed checks, and striped fabrics where transmitted light overcomes surface reflection color noise.
* **Limitations:** Requires dedicated backlighting hardware; not directly applicable to reflective smartphone or single-sided macro captures where only front surface illumination is available.
* **Comparison with Current Implementation:**
  * Existing implementation used raw 2D FFT slice `argmax` without directional reconstruction. Reconstructing directional sub-images via frequency masking suppresses inter-yarn harmonics and cross-weave interference.

### 2.2. Paper 2: Mathematical Statistics of Sub-Images
* **Citation:** Pan, R., Gao, W., Liu, J., et al. *"Automatic inspection of yarn-dyed fabric density by mathematical statistics of sub-images"*, *The Journal of The Textile Institute*, Vol. 106, Issue 4, pp. 389-401 (2015).
* **URL:** https://doi.org/10.1080/00405000.2014.946342
* **Mathematical Basis:**
  * Decomposes an inspection Region of Interest (ROI) into $M \times N$ overlapping sub-windows $I_{m,n}(x,y)$.
  * Computes 1D marginal projections $P_{m,n}(x) = \frac{1}{H_{\text{sub}}} \sum_y I_{m,n}(x,y)$ on each sub-image.
  * Employs statistical peak detection with outlier rejection (filtering by standard deviation $\sigma_{\text{dist}}$ of peak intervals).
  * Computes the global density by statistical consensus (median and interquartile mean across sub-images).
* **Suitable Structures:** Yarns with local color variations, slight tension distortions, and non-uniform illumination.
* **Limitations:** Sub-images must contain a sufficient number of yarn periods ($> 5\text{--}8$ periods) to establish statistical periodicity.
* **Comparison with Current Implementation:**
  * Existing implementation processed one monolithic ROI window. If illumination varied across the window, false peaks were detected. Sub-window statistical validation prevents localized shadows or fuzz clusters from skewing the global count.

### 2.3. Paper 3: Skew Correction and Density Detection
* **Citation:** Jing, J., Hao, P., Li, P., Zhang, L., Zhang, H. *"Skew Correction and Density Detection of Knitted and Woven Fabric"*, *Journal of Fiber Bioengineering and Informatics*, Vol. 9, No. 1, pp. 53-61 (2016).
* **URL:** https://www.mdpi.com/2617-8699/9/1/53 | https://doi.org/10.3993/jfbim00179
* **Mathematical Basis:**
  * Formulates skew detection via projection variance maximization: rotating the coordinate system through angle $\theta$ and evaluating the variance of marginal projection profiles:
    $$\theta^* = \arg\max_\theta \text{Var}\left(P_\theta(x)\right)$$
  * Applies a Butterworth low-pass filter to eliminate high-frequency yarn fuzz and sensor noise.
  * Uses 2D FFT to extract spectral peaks and reconstructs directional yarn grids using 2D IFFT.
* **Suitable Structures:** Both woven (orthogonal lattice) and knitted fabrics (loop courses/wales).
* **Limitations:** Search grid for projection variance requires iterative rotation, which is computationally expensive without coarse-to-fine angular refinement.
* **Comparison with Current Implementation:**
  * Existing implementation used Polar Radon integration over 2D FFT magnitude, which is faster ($\mathcal{O}(N_{\theta} \cdot R)$) than spatial image rotation. However, it failed to apply the detected skew correction to physical benchmark images in Notebook 04.

### 2.4. Paper 4: Spatial & Frequency Domain Inspection
* **Citation:** Aldemir, E., Özdemir, H., Kılınç, S. *"Automatic Inspection of the Warp-Weft Density Using Image Processing Techniques"*, *Tekstil ve Mühendis*, Vol. 23, No. 104, pp. 247-262 (2016).
* **URL:** https://dergipark.org.tr/en/pub/tekstilvemuhendis/issue/27335/287515
* **Mathematical Basis:**
  * Rigorously benchmarks multiple spatial filters (Median, Wiener, GLCM, Gray Line Profiles) against frequency-domain Fourier and Wavelet transformations across plain, twill, and patterned weaves.
  * Finds that Fourier harmonic peak extraction reliably resolves weave repetition, while spatial median filtering before projection yields the highest signal-to-noise ratio for peak counting.
* **Suitable Structures:** Plain and Twill fabrics.
* **Limitations:** Fourier method requires careful disambiguation between yarn pitch harmonics and weave pattern harmonics (float structure periods).
* **Comparison with Current Implementation:**
  * Existing implementation relied on a static weave hint to force 2D FFT on twill/satin without examining whether the FFT peak was a sub-harmonic (weave repeat $R$) or the true yarn frequency $f_{\text{yarn}}$.

### 2.5. Paper 5: Image Processing for Density Determination
* **Citation:** Yildiz, K., Şenyürek, V. Y., Yildiz, Z., Özen, M. S. *"A New Approach to the Determination of Warp-Weft Densities in Textile Fabrics by Using an Image Processing Technique"*, *Journal of Engineered Fibers and Fabrics*, Vol. 9, Issue 1, pp. 1-8 (2014).
* **URL:** https://doi.org/10.1177/155892501400900101
* **Mathematical Basis:**
  * Captures fabric swatches using calibrated optical imaging.
  * Preprocesses with contrast adjustment and adaptive spatial smoothing.
  * Analyzes 1D projection profiles by tracking individual yarn peaks and inter-peak distances $\Delta p_i$.
  * Employs inter-peak distance statistics:
    $$\bar{p} = \frac{1}{K-1} \sum_{i=1}^{K-1} (x_{i+1} - x_i), \quad N = \frac{S}{\bar{p}}$$
  * Compares pitch-based density with total peak count divided by field of view.
* **Suitable Structures:** Handheld pick-glass and microscope images of commercial apparel fabrics.
* **Limitations:** Dependent on continuous peak visibility; yarn breaks or slubs disrupt the sequence.
* **Comparison with Current Implementation:**
  * Existing implementation only did $\text{len}(\text{peaks}) / \text{FOV}_{\text{cm}}$, ignoring inter-peak distance dispersion, boundary effects, and median pitch estimation.

### 2.6. Paper 6: Recognition of Density & Weave Pattern
* **Citation:** Lin, Y., et al. *"Automatic Recognition of Density and Weave Pattern of Yarn-Dyed Fabric"*, *Autex Research Journal*, Vol. 22, No. 4, pp. 483-492 (2022).
* **URL:** https://doi.org/10.2478/aut-2022-0025
* **Mathematical Basis:**
  * Uses Radon transform over Fourier magnitude space for skew angle detection.
  * Maps warp-weft intersection points (crossing nodes) to determine thread interlacement topology.
  * Distinguishes yarn fundamental frequency $f_0$ from float repeat frequencies $f_r = f_0 / k$ ($k = 2, 3, 4$ for twill/satin).
* **Suitable Structures:** Multi-colored yarn-dyed wovens, twills, satins, and plaids.
* **Limitations:** Crossing-node segmentation requires high spatial resolution ($\ge 12\text{--}16\text{ px per yarn period}$).
* **Comparison with Current Implementation:**
  * Direct relevance: Explains why twill fabrics produce sub-harmonic peaks at $f_{\text{repeat}} = f_0 / 2$ or $f_0 / 3$ in Fourier space, causing the existing naive `argmax` to pick the repeat frequency instead of the yarn density.

---

## 3. Algorithmic Comparison: Existing vs. Proposed Remediated Engine

| Pipeline Component | Existing Implementation (`web_app/engine.py`) | Proposed Remediated Architecture | Mechanistic Rationale |
| :--- | :--- | :--- | :--- |
| **Calibration** | Single scalar `pixels_per_cm` applied to both X and Y. | Independent $S_x, S_y$ calibration object with verified physical pixel pitch $p_x, p_y$. | FabricNET has $S_x = 1280.0$, $S_y = 1200.0$ ($6.67\%$ anisotropy). Using a single scalar causes significant vertical distortion. |
| **ROI Handling** | Silently crops undersized images and claims $1.0\text{ cm}^2$ ROI. | Explicit ROI metadata reporting `requested_roi_cm`, `actual_roi_cm`, and `requested_roi_fully_available`. | Prevents false certainty when analyzing sub-centimeter optical captures. |
| **Skew Rectification** | Detected via Polar Radon, but omitted in Notebook 04 benchmark; pixel rotation without aspect normalization. | Metric-consistent affine rectification applied uniformly in production engine and physical benchmark. | Skew destroys projection variance ($\sigma = 0.00568$ vs $0.16333$, $28.77\times$ delta) and shifts 2D FFT peaks away from principal axes. |
| **2D FFT Extraction** | 1D axial slice `argmax` beyond fixed offset $k \ge 4$. | Windowed 2D FFT (Hann/Tukey) with multi-candidate harmonic family detection, DC band rejection, and symmetric peak-pair verification. | Eliminates harmonic confusion where illumination DC leak, weave repeats, or yarn hairiness dominate over yarn pitch. |
| **Spatial Projection** | Fixed `min_dist = Sx / 85.0`, pure peak count divided by crop width. | Adaptive minimum separation, prominence thresholding, median pitch estimation with outlier rejection, and boundary-aware span calculation. | Handles high-density fabrics up to $93\text{ picks/cm}$ without peak suppression, and eliminates endpoint truncation errors. |
| **Consensus & Fusion** | Disagreement defaults to FFT; twill/satin blindly forces FFT. | Multi-hypothesis evidence-based fusion with decision states (`VALIDATED`, `CONSISTENT_WITH_WARNING`, `NEEDS_REVIEW`). | Contradictory evidence indicates measurement ambiguity, not guaranteed FFT superiority. |
| **Quality Index** | Called `confidence_score` (arbitrary heuristic). | Renamed to `signal_quality_index` with breakdown of SPNR, profile contrast, and inter-engine concordance. | Honest representation; avoids claiming statistical probability of correctness without empirical calibration. |
| **Density Semantics** | Total density defined as $N_{\text{warp}} + N_{\text{weft}}$ but labeled threads/cm². | Separated into linear density sum (threads/cm) and areal intersection density (crossings/cm² = $N_{\text{warp}} \times N_{\text{weft}}$). | Strict dimensional and physical unit correctness. |

---

## 4. Technical Strategy for Core Engine Remediations

### 4.1. Anisotropic Metric Coordinate Normalization
Given an input image $I$ with dimensions $W \times H$ and scales $S_x, S_y$:
1. If $S_x = S_y$, coordinates are isotropic.
2. If $S_x \ne S_y$, we rescale the image to an isotropic reference grid $S_{\text{iso}} = \max(S_x, S_y)$ using bicubic anti-aliasing interpolation:
   $$W_{\text{norm}} = \text{round}\left(W \cdot \frac{S_{\text{iso}}}{S_x}\right), \quad H_{\text{norm}} = \text{round}\left(H \cdot \frac{S_{\text{iso}}}{S_y}\right)$$
   This guarantees that physical angles $\theta_{\text{phys}}$ map linearly to image coordinate angles $\theta_{\text{img}}$, enabling exact affine rotation without shear distortion.
3. Alternatively, transformations in frequency and spatial space are scaled strictly by their respective dimensional scales:
   $$f_{x, \text{metric}} = \frac{k_x}{W_{\text{px}}} \cdot S_x, \quad f_{y, \text{metric}} = \frac{k_y}{H_{\text{px}}} \cdot S_y$$

### 4.2. Multi-Candidate Harmonic Family Identification in 2D FFT
Instead of naively taking `argmax(slice[4:])`:
1. Apply a 2D Hann window $w(x, y) = \sin^2(\frac{\pi x}{W}) \sin^2(\frac{\pi y}{H})$ to suppress border spectral leakage.
2. Compute the 2D FFT magnitude spectrum $M(u, v) = |\mathcal{F}\{I \cdot w\}|$.
3. Extract candidate local maxima along the horizontal band $|v| \le 2$ (warp candidates) and vertical band $|u| \le 2$ (weft candidates).
4. Evaluate candidates against the plausible physical density bounds:
   $$N_{\min} = 10\text{ threads/cm}, \quad N_{\max} = 120\text{ threads/cm}$$
5. Identify harmonic ratios: If a strong peak exists at $f_1$ and another at $f_2 \approx 2 f_1$, evaluate whether $f_1$ is the yarn fundamental and $f_2$ is the second harmonic, or if $f_1$ is a weave repeat (e.g. in twill $2/2$).
6. Validate symmetric pairs: A genuine physical spatial frequency must exhibit conjugate symmetry:
   $$M(+u_0, +v_0) \approx M(-u_0, -v_0)$$

### 4.3. Robust Spatial Pitch Estimation
For marginal projection profiles $P_{\text{warp}}(x)$ and $P_{\text{weft}}(y)$:
1. Apply a 1D median filter ($k=3$) to suppress single-pixel fiber fuzz.
2. Detect local maxima with prominence $\ge \Delta y_{\text{prom}}$ and adaptive minimum distance $d_{\min} = \max(3, \text{round}(0.5 \cdot S_x / N_{\max}))$.
3. Compute all consecutive inter-peak intervals:
   $$\Delta x_i = x_{i+1} - x_i, \quad i = 1, \dots, K-1$$
4. Compute the median pitch $\tilde{p}_x = \text{median}(\{\Delta x_i\})$ and dispersion ratio $\text{IQR} / \tilde{p}_x$.
5. The pitch-based density is:
   $$N_{\text{proj, pitch}} = \frac{S_x}{\tilde{p}_x}$$
6. The span-based density is:
   $$N_{\text{proj, span}} = \frac{K - 1}{(x_K - x_1) / S_x}$$
7. If the intervals are highly regular ($\text{IQR} / \tilde{p}_x \le 0.15$), $N_{\text{proj, pitch}}$ and $N_{\text{proj, span}}$ converge. If irregular, outlier rejection is applied.


---

## 5. Client Ground Truth and Validation Design

The client-confirmed manual protocol measures each specimen at five distinct locations over 1 cm, counts warp and weft independently at each location, and uses the average of the five readings as the specimen reference. The stated example is 31 ends/cm Warp and 27 picks/cm Weft, with inclusive ±2 factory tolerance. These specimen-level averages must not be copied onto individual region photographs as if they were local labels.

The implemented data contract is versioned (schemas/client_ground_truth.schema.json, schema version 1.0.0). Each of five regions stores raw region Warp/Weft counts, exact measurement length, image identity or null, camera and calibration metadata, weave, lighting, focus, and date. A region is eligible for local supervised training only when its own photograph is tied to its own manual count. Specimen-only records remain separate.

Evaluation now reports local-region metrics and specimen-level aggregates. A specimen aggregate is accepted on an axis only if all five regional model outputs are available on that axis. Cluster bootstrap resamples fabric_id specimens rather than treating five correlated regions as independent observations. All reported accuracies include explicit coverage and rejection rates.

## 6. Learned-Model Evidence and Current Research Boundary

The public repository baseline inspected for this work did not contain the reported experiments/learned_models directory, model notebooks, feature extraction source, checkpoint files, training logs, split manifests, real segmentation annotations, or learned inference dispatcher. The earlier agent's reported Random Forest, XGBoost, MLP, U-Net, Roboflow and FCN results therefore cannot currently be reproduced from the public checkout.

Those results must remain unverified until the source code, exact input/label data, specimen-grouped splits, configurations, checkpoints and per-sample predictions are committed. In particular:

- A synthetic U-Net mIoU is not real-fabric segmentation accuracy.
- Roboflow object-detection mAP is not physical threads/cm accuracy.
- A custom handcrafted feature vector should not be described as an exact reproduction of FabricNET's IFV method without code-level equivalence.
- The legacy TextileDefectDetection FCN is a reference candidate whose paired illumination input assumptions differ from the client's single smartphone exposure.
- Learned regression, yarn segmentation, and hybrid segmentation-plus-geometric-measurement are separate experiments.

The webpage now exposes Classical, Learned and Hybrid choices, but only Classical is enabled because it is the only mode with an implemented inference path in this checkout. Method-comparison mode executes every currently available method and labels unavailable methods explicitly. It does not fabricate learned results.

## 7. Deterministic Benchmark Reproduction Result

A dedicated CI runner re-executed all 130 FabricNET images using the authoritative src.fabric_analysis engine and the nominal 5 × 4 mm FOV (1280 × 1200 px/cm). The rerun exactly reproduced all candidate predictions, accepted densities and decision statuses in the committed benchmark (zero changed fields across 130 images). This establishes source/data/configuration reproducibility, not satisfaction of the client's ±2 tolerance in a smartphone/factory acquisition domain.

See docs/FABRICNET_BENCHMARK_RERUN.md for the full per-weave breakdown, acceptance coverage, confidence intervals and artifact provenance.
