# Learned-Model Validation and Reproducibility Audit

## Audit baseline

This audit is against public main at commit 8f55927d910197d6778b2d56217092973bf9cc56.

The public tree does not contain experiments/learned_models/, six learned-model notebooks, model checkpoints, a model registry, trained weights, feature-extraction source for the reported 262-dimensional vector, or real image/mask annotations for the reported U-Net experiment. Consequently, the external/local agent's reported model table is not reproducible from this checkout and is not accepted as verified repository evidence.

This is a missing-artifact finding, not evidence that the experiments never ran on the agent's machine. Those local artifacts must be supplied and committed before their results can be independently audited.

## FabricNET calibration finding

The public repository's data/README.md, notebooks/04_real_fabric_benchmark.ipynb, and benchmark metadata already state the correct nominal FabricNET geometry:

- Image resolution: 640×480 px.
- Field of view: 5×4 mm (0.5×0.4 cm).
- Nominal calibration: 1280 px/cm horizontally and 1200 px/cm vertically.
- Calibration uncertainty: the FOV-derived scale has not been independently verified against a stage micrometer.

Therefore the earlier claim that the current public repository used a 1 cm FabricNET field of view is not supported by this baseline. The 5×4 mm description is retained. The learned-model experiment report, which was not present in the public tree, must use these same physical dimensions.

## Feature-regression claims

The reported custom 262-dimensional vector (GLCM 96 + LBP 54 + Gabor 96 + statistical features 16) is absent from the public source tree. There is no public code to confirm exact feature definitions, windowing, normalization, or whether the 16 statistical features implement IFV. It must be described as a custom handcrafted feature baseline unless a reproducible implementation proves equivalence to the paper's IFV method.

The claimed Random Forest, XGBoost, and MLP metrics are not independently reproducible without the feature code, exact labels, group split manifest, fixed seeds, configurations, and predictions on the same locked test specimens.

## U-Net claims

The public tree contains no reported 120-swatch synthetic U-Net experiment, generator, masks, architecture, weights, training logs, or evaluation notebook. Any previously reported pixel accuracy or mIoU must be labelled as synthetic-domain results unless the generator and masks prove otherwise. Synthetic mIoU is not evidence of real FabricNET or client-phone segmentation accuracy.

Real-domain validation requires masks annotated independently on real images. No mask may be generated from the model's own predictions and then treated as ground truth.

## Roboflow and NMS claims

The current public repository has a Roboflow skills reference but no exported warp-weft-new-prod annotations, dataset version, model weights, inference outputs, or NMS simulation source. The project-page detection metrics, if cited, must be attributed to that detection benchmark. mAP, precision, and recall are not physical ends/cm or picks/cm measurements.

The public project description is Roboflow 3.0 Object Detection (Fast). The repository must not assert a specific YOLO architecture unless the model card/export metadata supports it. A hypothetical NMS simulation is not observed suppression on the model's actual boxes. For non-overlapping 18 px boxes with 20 px center-to-center spacing, pairwise IoU is zero; IoU NMS cannot suppress them under that geometry.

## FCN reference

No FCN implementation, paired front/back illumination dataset, checkpoint, or inference output is present in this repository baseline. Treat it as a literature/reference candidate only. Do not claim it has been evaluated on the client's single-exposure phone image.

## Experimental protocol requirements

Before learned-model accuracy is used for a decision or UI claim, publish:

1. Versioned dataset manifest and exact source/provenance.
2. Region-local manual labels, not replicated specimen averages.
3. fabric_id-grouped train/validation/test manifests.
4. Fixed seeds, preprocessing, feature definitions, and hyperparameters.
5. Model source, checkpoint, SHA-256, input contract, and inference adapter.
6. Per-sample predictions (including rejected rows) and runtime.
7. MAE, RMSE, median absolute error, bias, ±1/±2 rates, coverage, rejection rate, per-weave/per-specimen results, and confidence intervals.
8. Separate FabricNET microscopy and client smartphone domain results.

The web application exposes Classical, Learned, and Hybrid choices. Only Classical is available in this checkout. Learned and Hybrid remain unavailable until a verifiable model registry, checkpoint, inference adapter, and explicit server-side dispatch implementation are committed and validated. Merely placing a checkpoint or adapter file in the repository must not enable the mode. The UI/API must not synthesize or substitute a model prediction.
