# Correct Setup and Troubleshooting

This guide starts the dashboard with the trained damage model included in this
repository. Do not copy an existing `.venv` from another computer.

## Which model is which?

The trained damage model is:

```text
Runscomplete/runs/vehicle_damage_seg-2/weights/best.pt
```

It identifies:

- scratch
- dent
- tear
- missing part
- broken lamp
- puncture
- broken glass

`yolov8n.pt` is a separate general detector. It only confirms that a car,
motorcycle, bus, or truck is visible. It is not the trained damage model.

## 1. Clone or update the repository

For a new copy:

```powershell
git clone https://github.com/KushanEsala/vehicle-damade-dash.git
cd vehicle-damade-dash
```

For an existing clone:

```powershell
git pull
```

## 2. Install Python 3.11

If Python is not installed:

```powershell
winget install --exact --id Python.Python.3.11
```

Close and reopen PowerShell after installation, then confirm:

```powershell
py -3.11 --version
```

## 3. Create a fresh environment

Run these commands from the repository folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If `.venv` was copied from another computer, delete only that `.venv` folder
and recreate it using the commands above.

## 4. Optional NVIDIA RTX setup

The CPU setup above works without CUDA. For the previously tested CUDA 12.8
PyTorch build, activate `.venv` and run:

```powershell
pip uninstall -y torch torchvision
pip install torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu128
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NOT DETECTED')"
```

Continue only when the command prints `CUDA: True` for GPU execution. The
dashboard still works on CPU if CUDA is unavailable.

## 5. Verify models and inference

Run:

```powershell
python verify_setup.py
```

The final line must be:

```text
SETUP VERIFIED
```

This checks package imports, model checksums, class names, and performs a small
inference with both model files.

The correct SHA-256 hashes are:

```text
best.pt:    C9D86E67A4C14F65047F33C17B4C4357613A0A15B52F919D76FF1C8542C0D541
yolov8n.pt: F59B3D833E2FF32E194B5BB8E08D211DC7C5BDF144B90D2C8412C47CCFC83B36
```

## 6. Start the dashboard

```powershell
.\start_model_tester.ps1
```

Or:

```powershell
python -m streamlit run model_tester.py
```

Open <http://localhost:8501>.

## When an image shows no damage

First decide whether it is a setup failure or a model limitation:

1. Confirm `python verify_setup.py` succeeds.
2. Set **Damage confidence** to `0.20`.
3. For a full-vehicle photograph, leave **Require vehicle confirmation** on.
4. For a close-up bumper, door, lamp, or body panel, turn
   **Require vehicle confirmation** off and analyze again.

The general `yolov8n.pt` model often cannot identify a vehicle from a very tight
close-up because the full vehicle shape is missing. With confirmation enabled,
the dashboard intentionally withholds damage predictions. This does not mean
that `best.pt` failed to load.

If confirmation is off and no damage appears even at confidence `0.10`, the
trained model did not recognize that example. The saved model has approximately
40.6% mask recall, so some real damage will be missed. More representative
training images are required to improve that limitation.

## Common errors

### `Virtual environment not found`

Create `.venv` using section 3.

### `ModuleNotFoundError`

Activate `.venv`, then run:

```powershell
pip install -r requirements.txt
```

### Model checksum mismatch

The model download is incomplete or modified. Run:

```powershell
git restore Runscomplete/runs/vehicle_damage_seg-2/weights/best.pt yolov8n.pt
git pull
```

Then run `python verify_setup.py` again.

### Port 8501 is already in use

Run:

```powershell
python -m streamlit run model_tester.py --server.port 8502
```

Then open <http://localhost:8502>.

