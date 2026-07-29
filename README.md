# Vehicle Damage Insurance ERP

A role-based insurance assessment system with a Next.js web interface, FastAPI
backend, MySQL database, PDF reports, and the trained vehicle-damage models.

## Main features

- Secure sign-in for administrators, operators, and registered customers
- Customer, vehicle, insurance-plan, company, and user management
- New vehicle-damage assessments with editable findings and costing
- Reanalysis with adjustable damage and vehicle confidence thresholds
- Separate assessment review and finalized report pages
- Marked damage images and downloadable PDF reports
- Customer access restricted to their own vehicles and reports
- Optional server-side Gemini visual cross-check

The trained damage classes are `scratch`, `dent`, `tear`, `missing_part`,
`broken_lamp`, `puncture`, and `broken_glass`.

## Included models

The required model files are committed with the project:

```text
Runscomplete/runs/vehicle_damage_seg-2/weights/best.pt
yolov8n.pt
```

Training datasets are intentionally excluded.

## Requirements

- Windows 10 or 11
- Python 3.11
- Node.js 20 or newer, including npm
- MySQL or MariaDB through XAMPP/phpMyAdmin
- Git

The application works on CPU. A supported CUDA-enabled NVIDIA GPU is optional
and can speed up local model inference.

## First-time setup

Open PowerShell in the folder where you want the project:

```powershell
git clone https://github.com/KushanEsala/vehicle-damade-dash.git
cd vehicle-damade-dash
Set-ExecutionPolicy -Scope Process Bypass
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
cd frontend
npm install
cd ..
```

If `py -3.11` is unavailable, install Python 3.11 first and make sure the
Python launcher is enabled.

## Database setup

1. Start Apache and MySQL from XAMPP.
2. Open phpMyAdmin.
3. Import `scripts/schema_vehicle_analyzis.sql`. It creates and selects the
   `Vehicle_Analyzis` database.
4. Create the local configuration:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set `MYSQL_USER` and `MYSQL_PASSWORD` to a MySQL account that has access to
`Vehicle_Analyzis`. The `.env` file is ignored by Git.

For a local development account, run this in phpMyAdmin's SQL tab and use the
same password in `.env`:

```sql
CREATE USER IF NOT EXISTS 'vehicle_erp_app'@'localhost'
IDENTIFIED BY 'choose-a-strong-local-password';
GRANT ALL PRIVILEGES ON Vehicle_Analyzis.* TO 'vehicle_erp_app'@'localhost';
FLUSH PRIVILEGES;
```

The backend can fall back to a local SQLite database in development if MySQL is
unavailable. Use MySQL for the shared/base project so all records remain in the
intended database.

## Optional visual cross-check

The application can send only the inspection image to Gemini from the backend
to refine damage labels, parts, and masks. The API key must be installed
separately on every computer and is never committed.

Follow [README_SECRET.md](README_SECRET.md). The application continues with the
local YOLO models when this optional service is not configured or unavailable.

## Verify and start

```powershell
.\.venv\Scripts\Activate.ps1
python verify_setup.py
.\.venv\Scripts\python.exe -m pytest -q
cd frontend
npm run build
cd ..
.\start_web_app.ps1
```

Open:

- Web application: <http://localhost:3000>
- Backend health check: <http://localhost:8000/api/health>

Initial administrator:

```text
Username: admin
Password: Admin@123456
```

Change the password after the first sign-in. Customers cannot self-register;
an administrator or operator must create the customer account.

## Updating an existing clone

Commit or save any work on the cloned computer before pulling. Then run:

```powershell
cd "D:\FinalProject 2026\vehicle_damade_dash_cloned"
git status
git pull origin main
Set-ExecutionPolicy -Scope Process Bypass

if (-not (Test-Path .\.venv\Scripts\python.exe)) {
    py -3.11 -m venv .venv
}

.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
cd frontend
npm install
cd ..
python verify_setup.py
.\start_web_app.ps1
```

If the visual cross-check has not been configured on that computer, run
`.\configure_vision.ps1` once after installing the requirements.

## Troubleshooting

- Full web setup: [WEB_APP_SETUP.md](WEB_APP_SETUP.md)
- Model and environment checks:
  [SETUP_AND_TROUBLESHOOTING.md](SETUP_AND_TROUBLESHOOTING.md)
- Visual-validation behavior:
  [VISION_VALIDATION_SETUP.md](VISION_VALIDATION_SETUP.md)
- Backend logs: `backend-api.log` and `backend-api-error.log`
- Frontend logs: `frontend-web.log` and `frontend-web-error.log`

Do not commit `.env`, `.venv`, datasets, uploaded customer images, generated
reports, database files, logs, or API keys.

This system provides assessment support. Every finding and cost must be
reviewed by an authorized person before a report is finalized.
