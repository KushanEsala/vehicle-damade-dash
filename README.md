# Vehicle Damage Dashboard

A local Streamlit dashboard for vehicle-damage segmentation. It combines:

- `best.pt`, the trained YOLO segmentation model for visible vehicle damage.
- `yolov8n.pt`, a general detector used to confirm that a supported vehicle is present.
- Saved validation metrics, plots, and prediction examples from the completed 50-epoch run.

## Detected damage classes

- Scratch
- Dent
- Tear
- Missing part
- Broken lamp
- Puncture
- Broken glass

## Quick start on Windows

Python 3.11 is recommended.

```powershell
git clone https://github.com/KushanEsala/vehicle-damade-dash.git
cd vehicle-damade-dash
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
.\start_model_tester.ps1
```

Open <http://localhost:8501> if the browser does not open automatically.

For model verification, RTX setup, and troubleshooting close-up images, see
[SETUP_AND_TROUBLESHOOTING.md](SETUP_AND_TROUBLESHOOTING.md).

## Included trained artifacts

The dashboard loads:

```text
Runscomplete/runs/vehicle_damage_seg-2/weights/best.pt
```

The completed run also includes `last.pt`, `results.csv`, validation predictions,
precision/recall curves, and confusion matrices. The best saved validation row
was epoch 44:

| Metric | Value |
|---|---:|
| Mask precision | 53.78% |
| Mask recall | 40.57% |
| Mask mAP50 | 41.20% |
| Mask mAP50-95 | 22.15% |
| Box mAP50 | 44.80% |
| Box mAP50-95 | 27.58% |

## Dataset policy

Training datasets are intentionally not committed. To retrain, place a YOLO
segmentation dataset in `data/` or `yolo_dataset/`, run
`python prepare_dataset.py`, and then use `train.py`.

This is a prototype decision-support tool. Predictions should be reviewed by a
person and must not be the sole basis for repair, insurance, or safety decisions.
