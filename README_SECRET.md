# Private API-key installation

This guide explains how to configure the optional Gemini visual cross-check
without putting the API key in Git, `.env`, source code, frontend JavaScript,
the database, a command argument, or PowerShell history.

**No API key is stored in this file or anywhere else in the repository.**

## Before you begin

1. Obtain a Gemini API key from the provider account used for this project.
2. Clone or pull the project.
3. Create `.venv` and install `requirements.txt` as described in `README.md`.

Each Windows computer needs its own one-time installation. Windows Credential
Manager entries do not transfer through Git, ZIP files, or a copied `.venv`.

## Install the key securely

Open PowerShell in the project root:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\configure_vision.ps1
```

The script:

1. asks for the key using a hidden prompt;
2. asks for it again to prevent typing mistakes;
3. verifies it without printing or logging it; and
4. stores it in Windows Credential Manager through the operating-system
   keyring.

Paste the key only into that hidden prompt.

## Check the installation

```powershell
.\configure_vision.ps1 -Status
```

Expected result:

```text
Visual validation credential: configured
```

Start or restart the application with:

```powershell
.\start_web_app.ps1
```

Create a new assessment or use **Reanalyze**. Previously saved assessments are
not changed automatically.

## Replace the key

Run the installation command again:

```powershell
.\configure_vision.ps1
```

The verified replacement takes effect on the next assessment.

## Remove the key

```powershell
.\configure_vision.ps1 -Remove
```

The local YOLO models continue working without Gemini.

## Security rules

- Never add the key to `.env`, README files, Python/TypeScript code, SQL, curl
  examples, screenshots, chat messages, Git commits, or frontend storage.
- Never pass the key directly on a command line.
- Do not copy Windows Credential Manager exports to another computer.
- Rotate the key immediately in the provider console if it is exposed.
- Browser DevTools will show calls to the local FastAPI service. The provider
  request and credential remain server-side and are not sent to the browser.
- Uploaded inspection images are sent to the configured provider for the
  optional cross-check; customer identity, policy, and cost data are not.

For technical details and fallback behavior, see
`VISION_VALIDATION_SETUP.md`.
