# Resume Training on the NVIDIA RTX PC

The checkpoint in `runs\vehicle_damage_seg-2\weights\last.pt` contains 15
completed epochs. Resuming it will start at epoch 16.

## 1. Extract and open PowerShell

Extract the ZIP on the RTX PC. Open PowerShell inside the extracted
`vehicle_damage_yolo_desktop` folder.

## 2. Create a new virtual environment

Do not copy or reuse the virtual environment from the original PC.

```powershell
Set-ExecutionPolicy -Scope Process Bypass
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 3. Install CUDA-enabled PyTorch

The NVIDIA graphics driver must already be installed and current.
The complete CUDA Toolkit is not normally required because the PyTorch wheel
includes the required CUDA runtime.

```powershell
pip install torch==2.11.0 torchvision==0.26.0 --index-url https://download.pytorch.org/whl/cu128
pip install -r requirements.txt
```

## 4. Confirm that PyTorch detects the RTX GPU

```powershell
python -c "import torch; print('CUDA:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NOT DETECTED')"
```

Do not resume unless the result contains:

```text
CUDA: True
GPU: NVIDIA GeForce RTX ...
```

If it says `CUDA: False`, stop and correct the NVIDIA driver or PyTorch
installation first.

## 5. Regenerate dataset paths for the new PC

```powershell
python prepare_dataset.py --data-dir .\yolo_dataset
```

This replaces the original PC's absolute dataset path in
`prepared_dataset.yaml`.

## 6. Resume at epoch 16 on the RTX GPU

```powershell
python -c "from pathlib import Path; from ultralytics import YOLO; r=Path.cwd(); YOLO(str(r/'runs'/'vehicle_damage_seg-2'/'weights'/'last.pt')).train(resume=True, data=str(r/'prepared_dataset.yaml'), device=0, batch=16, workers=4, save_dir=str(r/'runs'/'vehicle_damage_seg-2'))"
```

Confirm that the output shows:

- Training resumes at epoch 16.
- The device is the NVIDIA RTX GPU.
- `GPU_mem` is greater than `0G`.

If CUDA reports an out-of-memory error, repeat the resume command with
`batch=8`.

## 7. Watch training

Open a second PowerShell window in the project folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\watch_training.ps1
```

Open `http://localhost:6006` if TensorBoard does not open automatically.

## Important files

- Resume checkpoint: `runs\vehicle_damage_seg-2\weights\last.pt`
- Best checkpoint so far: `runs\vehicle_damage_seg-2\weights\best.pt`
- Dataset: `yolo_dataset`
- Dataset configuration: `prepared_dataset.yaml`

Keep the complete `runs\vehicle_damage_seg-2` directory during transfer.
