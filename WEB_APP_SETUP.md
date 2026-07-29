# Web application setup

The current interface uses Next.js for the browser and FastAPI for the Python services. The trained damage model and the existing analysis services remain unchanged.

## First setup

Open PowerShell in the project folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
cd frontend
npm install
cd ..
```

Copy `.env.example` to `.env` and enter the working MySQL credentials for the `Vehicle_Analyzis` database. In development only, the backend uses the local SQLite file when MySQL cannot be reached.

## Start both services

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\start_web_app.ps1
```

Open `http://localhost:3000`. The API runs at `http://localhost:8000`.

Initial local administrator:

- Username: `admin`
- Password: `Admin@123456`

Change this password after the first sign-in. Customer accounts cannot be self-registered. An administrator or operator creates them from **Customers**, and the generated temporary password is shown once.

## Manual start for troubleshooting

PowerShell window 1:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

PowerShell window 2:

```powershell
cd frontend
npm run dev
```

## Verification

```powershell
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
npm run build
```

The former Streamlit application remains in the repository as a rollback option and is not required by the new interface.

## Optional visual cross-check

The FastAPI backend can use Gemini as a conservative second opinion after the
local YOLO models run. Follow [VISION_VALIDATION_SETUP.md](VISION_VALIDATION_SETUP.md)
to save the credential in Windows Credential Manager without placing it in the
repository, `.env`, frontend, database or browser.

## Damage reports

Each finalized assessment creates a separate report page. The page displays the marked vehicle image, accepted damage items, confidence, descriptions, individual costs and the total estimate. The PDF can be viewed inside the page, opened in a separate browser tab, or downloaded.

- Administrators can view company-wide finalized reports.
- Operators can view finalized operational reports.
- Customers can only view and download reports belonging to their own registered vehicles.
