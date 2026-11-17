# Client-Aligned Ground-Truth Measurement Protocol
**Warp & Weft AI — Authoritative Textile Industry Manual Counting Specification**

---

## 1. Overview & Operational Mandate

This protocol establishes the standardized physical ground-truth methodology confirmed by the textile-industry client. 

In industrial textile quality assurance, fabric thread density is subject to local structural variance due to loom tension fluctuations, take-up dynamics, and finishing relaxation. Consequently, a single point measurement does NOT constitute certified ground truth for a fabric production lot. 

The client's official procedure mandates a **five-region sampling protocol** over a calibrated 1.0 cm distance, evaluated against a strict factory tolerance of **$\pm 2.0\text{ threads/cm}$**.

---

## 2. Five-Region Physical Measurement Procedure

1. **Specimen Conditioning:**
   - The fabric specimen is laid flat on a clean, horizontal inspection surface without tension or wrinkling.
   - A standardized measurement length of exactly $1.0\text{ cm}$ ($10.0\text{ mm}$, $10,000\,\mu\text{m}$) is physically marked or delineated using a calibrated optical pick-glass / linen tester graticule.

2. **Five Independent Region Sampling:**
   - Thread counting is executed at five spatially separated physical locations across the specimen:
     - **Region 1 (R1):** Upper-left quadrant.
     - **Region 2 (R2):** Upper-right quadrant.
     - **Region 3 (R3):** Specimen geometric center.
     - **Region 4 (R4):** Lower-left quadrant.
     - **Region 5 (R5):** Lower-right quadrant.
   - Adjacent regions must be separated by at least $2\text{ cm}$ to ensure independent local sampling across different warp ends and weft picks.

3. **Manual Counting & Unraveling:**
   - Thread counts are counted manually under optical magnification.
   - When yarn density exceeds $40\text{ threads/cm}$, thread unraveling (fraying out 1 cm of fringe yarns) is used to verify counts.

4. **Mathematical Specimen Aggregation:**
   - For a specimen with raw region observations $x_1, x_2, x_3, x_4, x_5$:
     $$\bar{x} = \frac{1}{5} \sum_{i=1}^5 x_i$$
     $$s = \sqrt{\frac{1}{4} \sum_{i=1}^5 (x_i - \bar{x})^2}$$
   - The specimen mean $\bar{x}$ constitutes the official certified reading for the specimen.

---

## 3. Reference Specimen Ground Truth (Specimen 2)

From the client's handwritten inspection sheet (**Image C**), the physical observations for the reference striped woven fabric (**Image A**) are:

### Warp Thread Counts ($1.0\text{ cm}$ gauge)
| Region ID | Physical Location | Manual Warp Count (Ends) | Local Density (Ends/cm) |
| :--- | :--- | :--- | :--- |
| **R1** | Position 1 | 31 | 31.0 |
| **R2** | Position 2 | 31 | 31.0 |
| **R3** | Position 3 | 30 | 30.0 |
| **R4** | Position 4 | 31 | 31.0 |
| **R5** | Position 5 | 32 | 32.0 |

- **Sum:** $31 + 31 + 30 + 31 + 32 = 155\text{ ends}$
- **Warp Specimen Mean ($\bar{x}_{\text{warp}}$):** $\mathbf{31.0\text{ ends/cm}}$
- **Warp Sample Standard Deviation ($s_{\text{warp}}$):** $\mathbf{0.71\text{ ends/cm}}$

### Weft Pick Counts ($1.0\text{ cm}$ gauge)
| Region ID | Physical Location | Manual Weft Count (Picks) | Local Density (Picks/cm) |
| :--- | :--- | :--- | :--- |
| **R1** | Position 1 | 27 | 27.0 |
| **R2** | Position 2 | 27 | 27.0 |
| **R3** | Position 3 | 26 | 26.0 |
| **R4** | Position 4 | 27 | 27.0 |
| **R5** | Position 5 | 26 | 26.0 |

- **Sum:** $27 + 27 + 26 + 27 + 26 = 133\text{ picks}$
- **Weft Specimen Mean ($\bar{x}_{\text{weft}}$):** $\frac{133}{5} = \mathbf{26.6\text{ picks/cm}}\quad (\text{commercially rounded to }\mathbf{27.0})$
- **Weft Sample Standard Deviation ($s_{\text{weft}}$):** $\mathbf{0.55\text{ picks/cm}}$

---

## 4. Factory Acceptance Tolerance Bounds

The textile mill operates under a confirmed tolerance of **$\pm 2.0\text{ threads/cm}$**:

- **Warp Density Acceptance Window:**
  $$[31.0 - 2.0,\; 31.0 + 2.0] = [\mathbf{29.0,\; 33.0}]\text{ ends/cm}$$
- **Weft Density Acceptance Window:**
  $$[27.0 - 2.0,\; 27.0 + 2.0] = [\mathbf{25.0,\; 29.0}]\text{ picks/cm}$$

### Certification Rule
A specimen is certified as **PASS** if and only if **both** axes satisfy the tolerance bounds:
$$\text{Specimen PASS} \iff (\bar{x}_{\text{warp}} \in [29.0, 33.0]) \land (\bar{x}_{\text{weft}} \in [25.0, 29.0])$$

---

## 5. Architectural Data Invariants

1. **No Replicated Specimen Labels:** The specimen mean ($31.0, 27.0$) must NEVER be copied back onto individual region records as exact ground truth. Each region record preserves its own local count.
2. **Supervision Level Tagging:**
   - `region_matched`: When a photograph is physically paired with the exact counted $1\times 1\text{ cm}$ region.
   - `specimen_only`: When measurements describe the specimen overall without matched local photographs.
3. **JSON Schema Version:** All stored ground-truth files must conform strictly to `schemas/client_ground_truth.schema.json` version `1.0.0`.
