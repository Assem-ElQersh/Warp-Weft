# Client Ground-Truth Collection Protocol

## Purpose and client-confirmed acceptance rule

The client measures one physical fabric specimen at five distinct locations. At each location, the operator marks a 1 cm measurement length, counts warp ends and weft picks, and computes the specimen average across the five readings.

The client's stated specimen reference for the shared example is 31 warp ends/cm and 27 weft picks/cm. The stated factory tolerance is inclusive ±2 threads relative to the reference:

- Warp acceptance interval: 29–33 ends/cm.
- Weft acceptance interval: 25–29 picks/cm.

These reference values are specimen-level averages. They are not labels for every image crop or every local region.

## Required data organization

Use one specimen record (fabric_id) containing exactly five region observations. Each region needs a unique region_id and the fields in schemas/client_ground_truth.schema.json:

- image_path: photograph of this exact physical region, or null when no matched photograph exists.
- warp_manual_count, weft_manual_count: raw counts, not pre-rounded density estimates.
- measurement_length_cm: actual measured length. For the client's current protocol this should normally be 1.0.
- camera_id, pixels_per_cm_x, pixels_per_cm_y, calibration_source.
- weave_type, lighting_type, focus_quality, measurement_date.

Unknown capture metadata must be recorded as null, not guessed. Both axis calibration scales must be present together or both null. A nominal phone zoom level is not a physical calibration.

## Derived specimen reference

For each region, first derive local densities:

warp_ends_per_cm = warp_manual_count / measurement_length_cm

weft_picks_per_cm = weft_manual_count / measurement_length_cm

Then calculate the mean and sample standard deviation across the five distinct regional observations. Preserve every raw count and every local density.

The specimen mean is the comparator for specimen-level aggregate inference. Local image inference must be evaluated against the manual count from the same physical region only.

## Supervision rules

- region_matched: the region's own image is linked to that region's manual count. It may be used for local-region supervised training/evaluation.
- specimen_only: no matched region image exists. It may contribute to a specimen-level report, but it must not be expanded into five copied labels or used as five local training targets.
- A photograph of a nearby or visually similar region is not a matched image.

If the client sends only the five counts and one general photograph, record the five manual observations but leave each unmatched image_path null unless the photographed ROI can be tied to a specific measured region.

## Image capture and calibration

1. Capture the physical region that was counted, before moving the specimen.
2. Include a calibration target in the same imaging plane or use a verified calibration for the exact camera, lens, focus distance, zoom, and image pipeline.
3. Record independent X and Y pixels/cm.
4. Avoid digital resizing, screenshotting, messenger recompression, or unknown cropping before measurement. Keep the original file.
5. Record lighting arrangement, focus condition, camera identifier, and acquisition date.
6. Repeat measurements without changing the physical region identifier. A second operator/count should be stored as a separate observation/version rather than overwriting the first.

FabricNET's published/repository nominal optical geometry is different from the client's smartphone domain: 640×480 px over 5×4 mm, giving nominal 1280×1200 px/cm. The repository correctly labels this calibration as derived from the dataset FOV and not physically verified with a stage micrometer. Do not transfer this calibration to smartphone images.

## Validation metrics

Report separately for warp and weft:

- MAE and RMSE.
- Median absolute error.
- Mean signed bias (prediction minus manual reference).
- Percentage within ±1 and within the client's inclusive ±2 tolerance.
- Number of eligible predictions, rejected predictions, coverage, and rejection rate.
- Runtime statistics.
- Per-weave and per-specimen breakdowns.
- A bootstrap 95% confidence interval for MAE where sample size supports it.

Compute error statistics only on predictions that were actually returned, but always report coverage/rejection using all eligible rows as the denominator. Never convert a rejected measurement into a candidate FFT prediction for the purpose of accepted-measurement accuracy.

A production pass-rate target beyond the client's per-result ±2 interval has not been supplied. Report observed percentages; do not invent a population acceptance threshold.

## Leakage prevention

All regions, crops, augmentations, and repeat images belonging to one physical specimen must remain in the same data partition. Group by fabric_id (and, when relevant, a broader specimen/lot identifier) before producing train/validation/test splits. Fit feature normalization and hyperparameter tuning on training data only. Keep a locked test group untouched until final evaluation.

## Machine-readable implementation

- Schema: schemas/client_ground_truth.schema.json
- Python types and validation: src/fabric_analysis/ground_truth.py
- Metrics: src/fabric_analysis/validation_metrics.py
- Specimen-grouped folds and holdout splits: src/fabric_analysis/grouped_splits.py

The Python validator requires exactly five region observations, unique region IDs, matching fabric IDs, non-negative integer raw counts, positive measurement lengths, and consistent anisotropic calibration fields.
