# Vehicle Damage Segmentation Model — Training Report

## 1. Report purpose

This report records the training work that was actually completed for the vehicle-damage model. It covers:

- the source dataset and its prepared structure;
- dataset-path preparation and transfer checks;
- the model type and seven trained damage classes;
- the CPU-to-RTX resume workflow;
- the completed 50 epochs;
- validation results and saved artifacts;
- known limitations;
- work that was discussed but **not performed**, including negative/background training and a custom vehicle validator.

This distinction is important: the completed artifact is a **seven-class vehicle-damage segmentation model**. It is not a binary `vehicle_or_part` versus `not_vehicle` classifier, and no separate negative-image model was trained.

## 2. Training objective

The objective was to fine-tune a YOLO segmentation model to locate visible damaged regions and assign each accepted region to one of seven damage categories.

The trained classes were:

| Class ID | Class |
|---:|---|
| 0 | Scratch |
| 1 | Dent |
| 2 | Tear |
| 3 | Missing part |
| 4 | Broken lamp |
| 5 | Puncture |
| 6 | Broken glass |

This is an **instance-segmentation** task. The model predicts:

1. a damage class;
2. a confidence score;
3. a bounding box;
4. a segmentation mask/polygon showing the predicted damaged region.

It is not a regression-only model. Regression losses are used internally for box coordinates and mask learning, but the complete task combines classification, localization and segmentation.

## 3. Dataset used

### 3.1 Dataset source

Training used the existing local YOLO dataset located in:

```text
vehicle_damage_yolo_desktop/yolo_dataset/
```

The prepared dataset configuration points to:

```text
path: E:\Need For Speed Most Wanted (2005)\vehicle_damage_yolo_desktop\yolo_dataset
train: images/train
val: images/val
```

### 3.2 Dataset size and split

The dataset present with the completed project contains:

| Split | Images | Label files | Approximate share |
|---|---:|---:|---:|
| Training | 11,621 | 11,621 | 83.33% |
| Validation | 2,324 | 2,324 | 16.67% |
| Test | 0 | 0 | 0% |
| **Total** | **13,945** | **13,945** | **100%** |

Every image in the training and validation folders has a corresponding label file. No separate held-out test split was used in this completed run.

### 3.3 Negative images

The current label folders contain:

- zero empty training label files;
- zero empty validation label files;
- no dedicated negative/background split.

Therefore, the dataset did **not** explicitly train the model using unlabeled examples such as:

- buildings;
- walls;
- furniture;
- people without vehicles;
- unrelated objects;
- clean non-damaged vehicle regions as a dedicated negative category.

Negative training and a separate binary vehicle/vehicle-part validator were discussed as future improvements only. They were not included in the completed 50-epoch run.

## 4. Dataset preparation and fixing

The `prepare_dataset.py` utility was used to make the dataset portable and suitable for local desktop or RTX-PC training.

The preparation process:

1. Created the selected data directory when required.
2. Extracted ZIP archives if dataset archives were supplied.
3. Searched recursively for `dataset.yaml` or `data.yaml`.
4. Detected either supported YOLO directory layout:
   - `images/train` and `images/val`; or
   - `train/images` and `val/images`.
5. Required both training and validation image folders.
6. Replaced computer-specific dataset paths with the current absolute dataset root.
7. Preserved the seven-class name mapping.
8. Wrote the normalized configuration to `prepared_dataset.yaml`.

The final prepared configuration was:

```yaml
path: E:\Need For Speed Most Wanted (2005)\vehicle_damage_yolo_desktop\yolo_dataset
train: images/train
val: images/val
names:
  0: scratch
  1: dent
  2: tear
  3: missing_part
  4: broken_lamp
  5: puncture
  6: broken_glass
```

### 4.1 What “dataset fixing” did and did not mean

Completed dataset preparation fixed:

- invalid machine-specific paths;
- discovery of the correct YOLO YAML file;
- recognition of training and validation folder layouts;
- portability between the source computer and RTX computer;
- archive transfer integrity through ZIP CRC validation tooling.

The available preparation script does **not** show evidence of automatically:

- redrawing inaccurate segmentation polygons;
- correcting incorrect damage-class annotations;
- finding duplicate images;
- detecting train/validation leakage;
- adding negative images;
- generating a test split;
- balancing rare and common classes;
- converting bounding boxes into segmentation masks.

Those items should not be reported as completed.

## 5. Model and training method

### 5.1 Model family

The project training script initializes:

```text
yolov8n-seg.pt
```

This is the small/nano Ultralytics YOLO segmentation architecture initialized from pretrained weights and fine-tuned for the seven damage classes.

The completed run was subsequently resumed from saved checkpoints. The final run configuration records:

```text
task: segment
pretrained: true
resume: ...\weights\last_gpu.pt
```

### 5.2 Principal training settings

| Setting | Recorded value |
|---|---:|
| Epoch target | 50 |
| Input size | 640 × 640 |
| Batch size | 16 |
| Data-loader workers | 4 |
| Final device | CUDA device 0 |
| Validation during training | Enabled |
| Plot generation | Enabled |
| Checkpoint saving | Enabled |
| Optimizer | Auto-selected by Ultralytics |
| Deterministic mode | Enabled |
| Random seed | 0 |
| Automatic mixed precision | Enabled |
| Mask overlap handling | Enabled |
| Mask downsample ratio | 4 |
| Initial learning rate | 0.01 |
| Final learning-rate factor | 0.01 |
| Momentum | 0.937 |
| Weight decay | 0.0005 |
| Warm-up | 3 epochs |
| IoU validation/NMS setting | 0.70 |
| Maximum detections | 300 |

### 5.3 Recorded augmentation settings

The saved run configuration records these training-time augmentation parameters:

| Augmentation | Value |
|---|---:|
| HSV hue | 0.015 |
| HSV saturation | 0.70 |
| HSV brightness/value | 0.40 |
| Translation | 0.10 |
| Scale | 0.50 |
| Horizontal flip probability | 0.50 |
| Mosaic | 1.00 |
| Close mosaic | Last 10 epochs |
| MixUp | 0.00 |
| CutMix | 0.00 |
| Copy-paste | 0.00 |
| Rotation | 0 degrees |
| Shear | 0 |
| Perspective | 0 |

These are the saved run parameters. No claim is made that negative examples were synthesized by these transformations.

## 6. Training execution flow

### 6.1 Initial local training

Training began on the source computer using CPU processing. The first nine epochs were completed and saved. The model checkpoint allowed the work to continue rather than restart.

The recorded cumulative time at epoch 9 was approximately:

```text
49,073.7 seconds ≈ 13 hours 38 minutes
```

### 6.2 Continued local training

The run was resumed and continued through epoch 15. The time counter reset when the resumed process began, which is why `results.csv` does not contain one continuously increasing time value across all 50 rows.

The epoch 10–15 segment recorded approximately:

```text
37,875.3 seconds ≈ 10 hours 31 minutes
```

### 6.3 Transfer to the RTX computer

The project was transferred without copying the original virtual environment. The transfer retained:

- the YOLO dataset;
- prepared dataset YAML;
- training scripts;
- run directory;
- saved checkpoints;
- resume documentation.

On the RTX computer:

1. A compatible Python environment was created.
2. CUDA-enabled PyTorch and project requirements were installed.
3. `torch.cuda.is_available()` and the NVIDIA device name were checked.
4. Dataset paths were regenerated for the RTX computer.
5. Training resumed from the saved `last_gpu.pt` checkpoint.
6. CUDA device `0`, batch size `16` and four workers were used.

### 6.4 RTX completion

The timing counter resets again at epoch 16, consistent with another resumed training process. Epochs 16–50 completed in approximately:

```text
2,731.58 seconds ≈ 45 minutes 32 seconds
```

The artifacts therefore indicate a multi-stage workflow:

| Stage | Epochs | Recorded processing |
|---|---|---|
| Initial source-PC stage | 1–9 | CPU |
| Continued source-PC stage | 10–15 | Resumed CPU run |
| RTX stage | 16–50 | NVIDIA CUDA GPU |

The approximate combined recorded training time is about **24 hours 54 minutes**, excluding setup, transfer, dependency installation, validation outside the epoch loop and interruptions.

## 7. Losses and optimization

The run recorded:

- box loss for localization;
- segmentation loss for mask accuracy;
- classification loss for damage-class prediction;
- distribution focal loss for box-coordinate quality;
- corresponding validation losses.

### 7.1 Loss progression

| Loss | Epoch 1 | Epoch 50 | Direction |
|---|---:|---:|---|
| Training box loss | 1.6704 | 1.2899 | Improved |
| Training segmentation loss | 3.7238 | 2.3694 | Improved |
| Training classification loss | 3.3199 | 1.6259 | Improved |
| Training DFL loss | 1.6863 | 1.4127 | Improved |
| Validation box loss | 1.9972 | 1.5424 | Improved |
| Validation segmentation loss | 3.6602 | 2.8142 | Improved |
| Validation classification loss | 3.5784 | 2.0121 | Improved |
| Validation DFL loss | 1.9920 | 1.5676 | Improved |

The general decrease shows that the model learned meaningful patterns from the supplied annotations. Validation loss remained higher than training loss, which is expected, but the modest validation metrics show that difficult cases and generalization remain open problems.

## 8. Validation results

### 8.1 Best saved validation result

The project documentation identifies epoch 44 as the best saved validation row.

| Metric | Best recorded value |
|---|---:|
| Box precision | 55.91% |
| Box recall | 43.33% |
| Box mAP50 | 44.80% |
| Box mAP50–95 | 27.58% |
| Mask precision | 53.78% |
| Mask recall | 40.57% |
| Mask mAP50 | 41.20% |
| Mask mAP50–95 | 22.15% |

### 8.2 Final epoch result

At epoch 50:

| Metric | Epoch 50 |
|---|---:|
| Box precision | 56.98% |
| Box recall | 43.39% |
| Box mAP50 | 45.06% |
| Box mAP50–95 | 27.64% |
| Mask precision | 54.98% |
| Mask recall | 40.89% |
| Mask mAP50 | 41.14% |
| Mask mAP50–95 | 22.15% |

The highest single metric is not automatically the checkpoint-selection criterion. Ultralytics uses a combined fitness calculation, so `best.pt` may correspond to a different epoch from the row with the highest individual metric.

### 8.3 Interpretation

- Precision near 54% means a meaningful portion of predicted masks are correct, but false positives remain.
- Recall near 41% means the model misses a significant number of labeled damage instances.
- Mask mAP50 near 41% indicates moderate performance at the easier IoU threshold.
- Mask mAP50–95 near 22% indicates that precise segmentation boundaries remain challenging.
- The model is suitable as a prototype and operator decision-support tool, not as an autonomous insurance decision system.

These percentages are validation metrics, not a single conventional “accuracy” score.

## 9. Saved outputs

The completed run is stored under:

```text
Runscomplete/runs/vehicle_damage_seg-2/
```

Important artifacts include:

| Artifact | Purpose |
|---|---|
| `weights/best.pt` | Recommended inference checkpoint selected during validation |
| `weights/last.pt` | Model state at the end of epoch 50 |
| `weights/last_gpu.pt` | Larger resume checkpoint containing optimizer/training state |
| `results.csv` | Per-epoch losses, metrics and learning rates |
| `results.png` | Training/validation curves |
| `args.yaml` | Complete saved run configuration |
| `confusion_matrix.png` | Raw class-confusion visualization |
| `confusion_matrix_normalized.png` | Normalized confusion matrix |
| `BoxPR_curve.png` | Bounding-box precision/recall curve |
| `BoxF1_curve.png` | Bounding-box F1 curve |
| `MaskPR_curve.png` | Segmentation-mask precision/recall curve |
| `MaskF1_curve.png` | Segmentation-mask F1 curve |
| `val_batch*_labels.jpg` | Ground-truth validation examples |
| `val_batch*_pred.jpg` | Corresponding model predictions |
| `labels.jpg` | Dataset label/class distribution visualization |

For application inference, the primary model file is:

```text
Runscomplete/runs/vehicle_damage_seg-2/weights/best.pt
```

`yolov8n.pt` is a separate general COCO object detector used by the dashboard to confirm common vehicle classes. It was not fine-tuned during this seven-class damage-training run.

## 10. What was not completed

The following items were discussed but were not trained or implemented as new model training:

1. A binary `vehicle_or_part` versus `not_vehicle` model.
2. A custom close-up vehicle-part confirmation model.
3. Explicit negative training using buildings, furniture, walls, people and unrelated objects.
4. Dedicated vehicle-part classes such as bumper, door, lamp and glass for validator training.
5. Training on the additional `DamageDataset` folder.
6. A 70/20/10 train/validation/test resplit.
7. A separate untouched test-set evaluation.
8. Additional epochs beyond the completed first 50.
9. ROCm/AMD-GPU training.
10. Apple-silicon/M-series training.

The dashboard’s use of the general `yolov8n.pt` vehicle detector is an inference-time validation layer. It does not mean that negative/background examples were added to the damage model’s training dataset.

## 11. Known limitations

1. **No independent test set:** all reported measurements come from the validation split used during model development.
2. **No explicit negatives:** unrelated scenes and close-up false positives were not directly addressed through dedicated negative training.
3. **Close-up vehicle confirmation:** a general COCO detector may fail when only a damaged bumper, door, lamp or panel is visible.
4. **Moderate recall:** approximately 59% of labeled masks may remain undetected at the evaluated operating point.
5. **Boundary precision:** mask mAP50–95 shows that exact damage boundaries remain difficult.
6. **Class imbalance risk:** the saved label plot should be reviewed before future training to determine whether rare classes require more examples.
7. **Dataset leakage was not audited:** duplicate or near-duplicate images across train and validation were not programmatically checked by the preparation script.
8. **Human review remains required:** predictions and estimated costs must be reviewed by an authorized operator.

## 12. Recommended next training phase

The completed 50-epoch model should remain the baseline. A future improvement phase should be treated as a new experiment rather than overwriting this run.

Recommended steps:

1. Preserve `best.pt`, `last.pt`, `results.csv` and the existing validation artifacts.
2. Create a dataset inventory with per-class image and instance counts.
3. Detect duplicate and near-duplicate images across splits.
4. Manually review segmentation polygons and class names.
5. Add an untouched test split, preferably by vehicle or source group rather than random image only.
6. Add background/negative images with empty YOLO label files.
7. Add difficult close-ups of bumpers, doors, lamps, glass, tyres and body panels.
8. Train a separate validator with:
   - `vehicle_or_part`;
   - `not_vehicle`.
9. Evaluate the current baseline and new model on the same untouched test set.
10. Compare per-class precision, recall, F1 and mask mAP rather than only an overall score.
11. Select confidence thresholds using validation curves.
12. Retain operator review and record model version/hash with every insurance analysis.

## 13. Final conclusion

The completed work successfully produced a seven-class YOLO vehicle-damage segmentation model after 50 epochs, using 11,621 training images and 2,324 validation images. Training was checkpointed and resumed across the source computer and RTX computer, with the final 35 epochs completed rapidly on NVIDIA CUDA hardware.

The model learned useful damage localization and segmentation behavior, reaching approximately 41.20% mask mAP50 and 22.15% mask mAP50–95 at its best recorded validation point. It is an appropriate prototype for human-reviewed damage assessment.

Negative/background training, a custom vehicle/vehicle-part validator, additional datasets and an independent test split remain future work. They must not be represented as part of the completed first 50-epoch experiment.
