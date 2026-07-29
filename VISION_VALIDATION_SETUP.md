# Server-side visual validation

The application can use Gemini as an optional second opinion after the local
YOLO models run. YOLO remains the primary detector. The external review checks
the proposed regions, rejects obvious false positives, corrects supported
damage labels, suggests the vehicle part and provides a short description.
For every accepted finding, it also proposes a tight damage-only polygon in
full-image coordinates. The backend validates that polygon, matches it with a
local-model region where possible, and can recover a high-evidence region that
the local model missed.

This refinement applies to every trained damage class: scratch, dent, tear,
missing part, broken lamp, puncture and broken glass. The original YOLO polygon
is retained for fallback and audit purposes. Broken-glass overlays receive one
additional local crack-detail pass so the display marks the fracture network
instead of tinting an entire windscreen or window.

The full-image response is restricted to these system classes only:
`scratch`, `dent`, `tear`, `missing_part`, `broken_lamp`, `puncture`, and
`broken_glass`. Unsupported labels such as `other`, `paint_damage`, `crack`,
and `background` cannot be returned as report findings. Refined report images
show the vehicle part and damage label without the general COCO vehicle box.

If the service is unavailable or no credential is configured, the existing
YOLO workflow continues without interruption.

The server currently uses the stable `gemini-3.6-flash` model through the
Interactions endpoint. Uploaded JPG files are decoded and re-encoded before
the request; the outbound MIME type is always `image/jpeg`. `image/jpg` is not
used because it is not a supported media type.

## Privacy and browser isolation

- The credential is stored in Windows Credential Manager through Python's
  operating-system keyring integration.
- It is not written to Git, `.env`, the database, frontend JavaScript, browser
  storage, cookies, API payloads or application logs.
- The browser calls only the local FastAPI endpoint. The provider request is
  made by the backend process, so its URL and credential do not appear in
  browser DevTools.
- A browser Content Security Policy permits connections only to the local
  frontend and API, preventing frontend code from calling the provider.
- The submitted inspection image and detector candidate coordinates are sent
  for validation. Customer names, registration numbers, policies and costs are
  not included.
- Browser DevTools will still show the normal call from the frontend to
  `http://localhost:8000/api/analyses`. Normal application requests cannot be
  hidden from the browser that sends them.

## One-time setup

Open PowerShell in the project folder:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
.\configure_vision.ps1
```

Paste the Gemini API key only into the hidden PowerShell prompt. Enter it a
second time when requested. The setup command verifies it before saving. Do
not paste it into source code, chat, a command argument or a screenshot.

No restart is required. The next assessment reads the credential directly from
the operating-system vault.

## Check or remove the credential

```powershell
.\configure_vision.ps1 -Status
.\configure_vision.ps1 -Remove
```

Replacing or removing the credential takes effect on the next assessment.

## Applying refinement to an assessment

Only a new analysis or a reanalysis calls the visual refinement service.
Previously generated reports and marked images are not silently changed.
Choose **Reanalyze** on an assessment after changing the thresholds to produce
a new revision with the refined mask. If the external review is unavailable,
uncertain, outside the detector region or malformed, the application keeps the
original local-model mask.

The refinement improves presentation and reduces broad masks, but it is still
an automated estimate. An operator must review each finding before finalizing
costs or issuing a report.
