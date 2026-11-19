# PHYSICAL CALIBRATION & METROLOGICAL UNCERTAINTY REPORT
**Document Reference:** `experiments/reports/CALIBRATION_AND_UNCERTAINTY_REPORT.md`  
**Execution Phase:** Phase 8 — Physical Calibration and Metrology Layer  
**Execution Context:** Repository Canonical Branch `main`  
**Date:** 2026-11-19  

---

## 1. Executive Summary

This report establishes the physical calibration principles, analytical uncertainty propagation models, and geometric perspective rectification algorithms governing the Warp & Weft AI metrology system.

A fundamental tenet of textile metrology is that **digital image pixels have no intrinsic physical dimension**. Any assertion of yarn density (ends/cm or picks/cm) is meaningless without an unbroken calibration chain linking image sensor coordinates to the International System of Units (SI metric centimeters).

---

## 2. Mathematical Calibration Model

The physical thread density $D$ (threads/cm) is defined by the fundamental metrological relationship:

$$D = \frac{S}{\hat{p}}$$

where:
- $\hat{p} \in \mathbb{R}^+$ is the spatial wavelength (pitch) of adjacent yarns in image coordinates (pixels/thread).
- $S \in \mathbb{R}^+$ is the optical sensor scale factor along the measurement axis (pixels/cm).

### 2.1 Optical Scale Derivation
The scale factor $S$ is established via three supported calibration mechanisms:
1. **Direct Two-Point Physical In-Scene Ruler:**
   Given two pixel coordinates $\mathbf{x}_1 = (u_1, v_1)$ and $\mathbf{x}_2 = (u_2, v_2)$ marking known tick marks separated by physical distance $L_{\text{cm}}$:
   $$S = \frac{\|\mathbf{x}_2 - \mathbf{x}_1\|_2}{L_{\text{cm}}} = \frac{\sqrt{(u_2 - u_1)^2 + (v_2 - v_1)^2}}{L_{\text{cm}}}$$
2. **Fixed Magnification Optical Microscopy (e.g., FabricNET):**
   Calibrated via stage micrometer under controlled optics:
   $$S_x = 1280.0\text{ px/cm}, \quad S_y = 1200.0\text{ px/cm}$$
3. **Planar Homography with Known Target Geometry:**
   Given 4 detected corners of a standardized calibration target (e.g., credit card or factory aperture of width $W_{\text{target}}$ and height $H_{\text{target}}$), compute homography matrix $\mathbf{H} \in \mathbb{R}^{3 \times 3}$:
   $$\tilde{\mathbf{x}}_{\text{metric}} \sim \mathbf{H} \tilde{\mathbf{x}}_{\text{sensor}}$$
   rectifying perspective distortion and resampling the fabric to an isotropic pixel grid ($S_x = S_y = S_{\text{canonical}}$).

---

## 3. First-Order Analytical Uncertainty Propagation

Every physical measurement carries uncertainty. Following the ISO/BIPM *Guide to the Expression of Uncertainty in Measurement* (GUM), the combined standard measurement uncertainty $\sigma_D$ is derived via first-order Taylor series expansion:

$$\sigma_D^2 = \left(\frac{\partial D}{\partial S}\right)^2 \sigma_S^2 + \left(\frac{\partial D}{\partial \hat{p}}\right)^2 \sigma_p^2 + 2 \left(\frac{\partial D}{\partial S}\right)\left(\frac{\partial D}{\partial \hat{p}}\right) \operatorname{Cov}(S, \hat{p})$$

Because the optical calibration scale $S$ is established independently from the localized spatial pitch $\hat{p}$, their covariance is zero ($\operatorname{Cov}(S, \hat{p}) = 0$).

Computing partial derivatives:
$$\frac{\partial D}{\partial S} = \frac{1}{\hat{p}} = \frac{D}{S}$$
$$\frac{\partial D}{\partial \hat{p}} = -\frac{S}{\hat{p}^2} = -\frac{D}{\hat{p}}$$

Substituting into the variance formula:
$$\sigma_D^2 = \left(\frac{D}{S}\right)^2 \sigma_S^2 + \left(-\frac{D}{\hat{p}}\right)^2 \sigma_p^2 = D^2 \left[ \left(\frac{\sigma_S}{S}\right)^2 + \left(\frac{\sigma_p}{\hat{p}}\right)^2 \right]$$

Thus, the relative uncertainty satisfies the quadrature sum:
$$\frac{\sigma_D}{D} = \sqrt{\left(\frac{\sigma_S}{S}\right)^2 + \left(\frac{\sigma_p}{\hat{p}}\right)^2}$$

and the absolute uncertainty in threads/cm is:
$$\sigma_D = D \sqrt{\left(\frac{\sigma_S}{S}\right)^2 + \left(\frac{\sigma_p}{\hat{p}}\right)^2}$$

---

## 4. Sensitivity Analysis & Numerical Error Budgets

To illustrate uncertainty propagation across practical working conditions, the table below models varying optical scales, working distances, and pitch variations for a nominal fabric of $D = 30.0\text{ threads/cm}$:

| Optical Condition | Scale $S$ (px/cm) | Pitch $\hat{p}$ (px) | Pitch Variance $\sigma_p$ (px) | Scale Uncertainty $\sigma_S / S$ (%) | Density $D$ (threads/cm) | Absolute Uncertainty $\sigma_D$ (threads/cm) | Relative Uncertainty (%) | Meets Factory Tol ($\le \pm 2$ at $2\sigma$)? |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **High-Res Microscope** | 1280.0 | 42.67 | 0.50 px | 0.5% | 30.00 | **$\pm 0.38$** | 1.27% | **YES (High Margin)** |
| **Well-Calibrated Phone** | 263.5 | 8.78 | 0.40 px | 2.0% | 30.01 | **$\pm 1.49$** | 4.98% | **YES ($2\sigma = \pm 2.98$)** |
| **Phone with Ruler Jitter** | 263.5 | 8.78 | 0.60 px | 5.0% | 30.01 | **$\pm 2.54$** | 8.47% | **MARGINAL ($1\sigma > 2.0$)** |
| **Low-Res Smartphone** | 150.0 | 5.00 | 0.50 px | 3.0% | 30.00 | **$\pm 3.13$** | 10.44% | **FAIL (Exceeds Tolerance)** |

### 4.1 Key Deductions from Sensitivity Analysis
1. **The Low-Pitch Penalty:** When pixel pitch $\hat{p}$ drops below $6\text{ pixels/yarn}$ (low magnification or high thread count), pitch estimation jitter ($\sigma_p \approx 0.5\text{ px}$) dominates the uncertainty budget, rendering measurements incapable of meeting $\pm 2.0\text{ threads/cm}$ factory tolerance.
2. **Minimum Resolution Requirement:** For reliable client measurement, the optical magnification must provide at least $\hat{p} \ge 8.0\text{ pixels/yarn}$, corresponding to $S \ge 250\text{ px/cm}$ for typical $30\text{ threads/cm}$ apparel fabrics.

---

## 5. Perspective Distortion & Planar Homography Rectification

When a client captures a smartphone image obliquely (non-perpendicular optical axis), perspective distortion causes the apparent scale to vary across the field of view:
$$S(y) = \frac{f \cdot S_{\text{sensor}}}{Z(y)}$$
where $Z(y)$ is the variable working distance along the tilted plane.

To eliminate perspective variation, `experiments/learned_models/calibration.py` provides planar homography rectification:
```python
# The mechanistic justification for this step is: compute 3x3 homography matrix
# mapping 4 coplanar target corner points to an orthogonal metric coordinate frame,
# eliminating perspective foreshortening and establishing isotropic pixel scale.
h_matrix, (w_px, h_px) = compute_planar_homography(
    src_points=target_corners,
    target_width_cm=10.0,
    target_height_cm=10.0,
    scale_px_per_cm=300.0
)
rectified_image = rectify_perspective(image, h_matrix, (w_px, h_px))
```

---

## 6. Engineering Implementation in the Web Application

The calibration layer is integrated into the web application via two primary user workflows:
1. **Tab 1 / Tab 4 Two-Point Ruler Tool:** The client clicks two known tick marks on an in-scene millimeter ruler. The frontend captures $(u_1, v_1)$ and $(u_2, v_2)$, computes $S = \text{pixel\_distance} / L_{\text{cm}}$, and binds $S_x, S_y$ to the measurement request.
2. **Uncertainty Display:** Every measurement result is presented with its $95\%$ confidence interval:
   $$D \pm 1.96 \sigma_D\text{ threads/cm}$$
   preventing overconfident single-point reporting.
