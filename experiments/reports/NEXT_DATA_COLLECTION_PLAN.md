# Industrial Factory Data Collection & Physical Calibration Protocol (50–100 Swatches)

**The mechanistic justification for this step is: establish a statistically rigorous, factory-executable data acquisition protocol to eliminate the $N=1$ client sample bottleneck, provide empirical ground truth under ASTM D3775, and supply calibrated multi-illumination imagery for training domain-adapted neural segmentation models.**

---

## 1. Context & Operational Imperative

The empirical findings from the Warp & Weft research program conclusively establish:
1. **The $N=1$ Sample Bottleneck:** Deep neural networks cannot learn generalized yarn feature representations from a single client smartphone photograph (`data/samples/test.png`).
2. **The Microscopy Domain Gap:** Pretrained models trained on high-magnification optical USB microscopy ($1280\text{ px/cm}$, $\text{FOV} \approx 0.5\text{ cm}$) collapse when transferred to smartphone macro photography ($263.5\text{ px/cm}$, $\text{FOV} \approx 10\text{ cm}$) due to a $4.86\times$ optical magnification shift and fiber fuzz bundling.
3. **The Dimensionless Tensor Invariant:** Any deep learning model must operate in tandem with an absolute, physically calibrated optical scale ($S_x, S_y$, in $\text{px/cm}$) to output valid thread densities ($N = S / \Delta$).

To transition Warp & Weft AI from a prototype to a factory-certified automated metrology instrument, a standardized dataset of **50 to 100 physical fabric swatches** must be collected under controlled industrial conditions.

---

## 2. Fabric Swatch Matrix & Structural Diversity

The sample collection must span the operational range of commercial woven textiles ($15\text{ to }90\text{ threads/cm}$):

| Fabric Family / Weave Type | Target Count | Expected Density Range (threads/cm) | Primary Optical Challenges |
| :--- | :--- | :--- | :--- |
| **Plain Weaves (Poplin, Sheeting, Voile)** | 25 swatches | Warp: 20–45, Weft: 18–40 | High yarn crimp; tight packing; low interstice contrast in bleached white swatches. |
| **Twill Weaves (Denim, Chino, Drill)** | 20 swatches | Warp: 25–65, Weft: 16–35 | Strong diagonal ridges ($45^\circ / 63^\circ$) causing directional Fourier harmonics and float aliasing. |
| **Satin / Sateen Weaves** | 15 swatches | Warp: 30–80, Weft: 20–50 | Long floating yarns spanning 4 to 8 cross yarns; high specular reflection on mercerized yarn crowns. |
| **Yarn-Dyed Checks & Stripes** | 15 swatches | Warp: 25–40, Weft: 20–35 | Macro-color bands generating low-frequency spatial harmonics that distract Fourier peak detectors. |
| **Complex / Textured (Oxford, Dobby, Jacquard)** | 15 swatches | Warp: 18–50, Weft: 15–45 | Multi-yarn bundling, paired ends (Oxford basket), variable float lengths. |
| **Total Cohort** | **90 swatches** | **15–80 threads/cm** | Full commercial factory operational spectrum. |

---

## 3. Physical Calibration & Imaging Hardware Rig

Handheld, unconstrained smartphone photography introduces out-of-plane tilt, perspective skew, variable working distances ($d_w$), and non-uniform illumination gradients. All factory imagery must be acquired using a standardized benchtop jig:

### 3.1. Optical Rig Architecture
* **Rig Frame:** Rigid vertical camera stand with micro-adjustable height ($8.0\text{ to }15.0\text{ cm}$ working distance).
* **Base Plate:** Non-reflective matte black vacuum table or magnetic clamp plate ensuring fabric swatches lie completely flat without wrinkles or puckering.
* **Camera Sensor:** Standard commercial smartphone (e.g., iPhone 13+, Samsung S21+, Google Pixel 6+) or industrial USB3 CMOS sensor (Sony IMX series).
* **Camera Settings:**
  * Fixed manual focus locked on the fabric surface.
  * ISO set to minimum native value ($\text{ISO} \le 100$) to eliminate sensor shot noise.
  * Shutter speed $\ge 1/250\text{ s}$ to eliminate mechanical vibration blur.
  * White balance manually calibrated using an 18% neutral gray card.
  * Digital zoom strictly disabled ($1.0\times$ native optical lens).
  * Storage format: Uncompressed 16-bit DNG (RAW) or lossless 8-bit RGB PNG ($0\%$ compression artifacts).

### 3.2. Coplanar In-Frame Physical Scale Targets
Every capture must incorporate an authoritative metric reference placed strictly coplanar with the fabric face:
1. **Precision Steel Metrology Scale:** A certified etched 0.5 mm graduation steel ruler placed along the image margin.
2. **High-Accuracy ArUco / Checkerboard Target:** A $20\text{ mm}\times 20\text{ mm}$ photogrammetric marker with known physical dimensions printed on high-density ceramic or matte aluminum.
3. **Automated Scale Derivation:**
   $$\text{Scale } S_x = \frac{\Delta x_{\text{pixels}}}{L_{\text{metric}}}\,[\text{px/cm}], \quad S_y = \frac{\Delta y_{\text{pixels}}}{L_{\text{metric}}}\,[\text{px/cm}]$$
   The software must automatically detect the marker, rectify lens barrel distortion, and record $S_x$ and $S_y$ directly into the image JSON manifest.

---

## 4. Multi-Illumination Acquisition Modalities

Different weave structures reveal their yarn boundaries under specific lighting angles. For each of the 90 swatches, three synchronized photographic exposures must be captured:

```
[Camera Sensor] (Normal Axis z)
       |
       |  (Orthogonal)
       v
+--------------+   <--- Mode 1: Diffuse Dome Ring Light (Even illumination)
| Fabric Face  |   <--- Mode 2: Low-Angle Grazing Lighting (30 deg raking shadows)
+--------------+   <--- Mode 3: Transmissive Backlight (Bottom-up light table)
       ^
       |
[Backlight Panel]
```

1. **Mode 1: Orthogonal Diffuse Ring Light (Ground Color Capture):**
   * High-CRI ($>95$) LED ring light with diffuser hood.
   * Eliminates specular hot spots; captures true surface reflectance and printed dye boundaries.
2. **Mode 2: Low-Angle Grazing Raking Light ($30^\circ\text{--}45^\circ$ Grazing Angle):**
   * Directional bar light casting directional micro-shadows into the deep inter-yarn crevices.
   * Maximizes the edge gradient of warp and weft yarn crowns, boosting both 1D projection peak prominence and neural segmentation edge clarity.
3. **Mode 3: Transmissive Backlight (Light Table):**
   * High-uniformity LED light panel placed beneath open-structure, sheer, or high-porosity fabrics.
   * Highlights inter-yarn interstices as brilliant white aperture points ($I=255$), transforming yarn centerline detection into an unambiguous binary pore segmentation problem.

---

## 5. ASTM D3775 Ground Truth Labeling Protocol

Every physical swatch must be accompanied by certified ground truth counts established by two independent senior laboratory technicians:

### 5.1. 5-Region Physical Measurement Protocol
In compliance with ASTM D3775 ("Standard Test Method for End (Warp) and Pick (Weft) Count of Woven Fabrics"):
* Count five distinct regions on each swatch, separated by at least $2.0\text{ cm}$ diagonally across the fabric body:
  * Region 1: Center
  * Region 2: Top-Left Quadrant
  * Region 3: Top-Right Quadrant
  * Region 4: Bottom-Left Quadrant
  * Region 5: Bottom-Right Quadrant
* Tools: Precision counting pick-glass (optical magnifier with calibrated 1-inch / 1-cm aperture) and mechanical needle pointer.
* Verification: Both technicians must agree within $\le 1.0\text{ thread/cm}$. If discrepancy exceeds $1.0$, a third master metrologist repeats the count.
* Record mean $\bar{x}$, standard deviation $\sigma$, and discrete count array $[r_1, r_2, r_3, r_4, r_5]$ for both Warp (Ends/cm) and Weft (Picks/cm).

### 5.2. Dense Micro-Annotation Benchmark Subset (10 Swatches)
For a representative subset of 10 swatches (spanning 4 plain, 3 twill, 2 satin, 1 oxford):
* Manually annotate individual yarn centerlines and boundary polygons across a $512\times 512$ ROI using Labelme / CVAT.
* Classes: `background_interstice` (0), `warp_yarn_crown` (1), `weft_yarn_crown` (2).
* Export format: Semantic binary segmentation masks (PNG) and COCO format polygons (JSON).
* Purpose: Provides pixel-level supervision to fine-tune SegFormer-B0 and WarpWeftUNet.

---

## 6. Manifest Schema & Directory Storage Architecture

The collected dataset must be archived in the repository under `data/factory_benchmark/` following this strict schema:

```
data/factory_benchmark/
├── metadata/
│   ├── dataset_manifest.json
│   └── swatches_index.csv
├── swatches/
│   ├── SW_001/
│   │   ├── diffuse.png
│   │   ├── raking.png
│   │   ├── backlight.png
│   │   ├── metadata.json
│   │   └── masks/ (if annotated subset)
│   │       ├── warp_mask.png
│   │       └── weft_mask.png
│   ├── SW_002/
│   └── ...
```

### Swatch Metadata Schema (`metadata.json`)
```json
{
  "swatch_id": "SW_001",
  "weave_type": "twill_2_1",
  "fiber_composition": "100% Cotton",
  "fabric_weight_gsm": 215.0,
  "fabric_color": "Indigo Raw Denim",
  "camera_sensor": "Sony IMX766 50MP",
  "focal_length_mm": 24.0,
  "working_distance_cm": 10.5,
  "optical_scale": {
    "scale_x_px_cm": 265.4,
    "scale_y_px_cm": 264.8,
    "calibration_target": "ArUco_20mm_Dict4x4"
  },
  "ground_truth_astm_d3775": {
    "technician_1_id": "TECH_A",
    "technician_2_id": "TECH_B",
    "warp_ends_per_cm": {
      "counts": [31, 31, 30, 31, 30],
      "mean": 30.6,
      "std": 0.55,
      "certified_nominal": 31.0
    },
    "weft_picks_per_cm": {
      "counts": [27, 27, 26, 27, 26],
      "mean": 26.6,
      "std": 0.55,
      "certified_nominal": 27.0
    },
    "acceptable_range_warp": [29.0, 33.0],
    "acceptable_range_weft": [25.0, 29.0]
  }
}
```

---

## 7. Model Training & Active Learning Roadmap

With 90 swatches and multi-illumination crops, the machine learning workflow proceeds as follows:

```
+-----------------------------------------------------------+
| 90 Physical Swatches x 3 Exposures = 270 High-Res Images  |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
| Patch Tiling: 270 Images -> 10,800 Patches (512x512)      |
+-----------------------------------------------------------+
                             |
       +---------------------+---------------------+
       |                                           |
       v                                           v
[Weave Classification]                    [Semantic Segmentation]
DINOv2 ViT-S/14 Frozen Backbone           SegFormer-B0 (MiT-B0 Encoder)
+ Linear Classifier Head                  Fine-tuned on 10 Dense Swatches
Output: Plain / Twill / Satin             Output: Yarn Float & Centerline Masks
       |                                           |
       +---------------------+---------------------+
                             |
                             v
+-----------------------------------------------------------+
| Peak Prominence & Distance Transform Tracking             |
| Decoupled Yarn Spacing: Delta_x, Delta_y (pixels)         |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
| Physical Metric Scaling: N_warp = S_x / Delta_x           |
|                         N_weft = S_y / Delta_y            |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
| ASTM D3775 Verification against Ground Truth Counts       |
| Target: 100% Pass Rate within +/- 2.0 threads/cm          |
+-----------------------------------------------------------+
```
