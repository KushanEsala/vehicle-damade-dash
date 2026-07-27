# Vehicle Damage Model Tester

This local interface uses:

- `Runscomplete/runs/vehicle_damage_seg-2/weights/best.pt` for damage segmentation.
- A pretrained `yolov8n.pt` detector to confirm that a car, motorcycle, bus, or
  truck is present before accepting damage predictions.

## Install

```powershell
cd "PATH\TO\vehicle-damade-dash"
Set-ExecutionPolicy -Scope Process Bypass
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Start

```powershell
.\start_model_tester.ps1
```

The browser interface normally opens at `http://localhost:8501`.

The first run downloads the small pretrained vehicle detector. The trained
damage model remains local.
