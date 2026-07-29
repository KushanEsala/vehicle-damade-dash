# Vehicle Insurance ERP — Next.js and FastAPI Migration Plan

## 1. Decision

Replace the Streamlit presentation layer with:

- **Next.js App Router + TypeScript** for the web application.
- **FastAPI** for authentication, ERP operations, reports, uploads, and model inference.
- **Existing Python YOLO pipeline** retained behind FastAPI services.
- **MySQL `Vehicle_Analyzis`** retained as the primary database.
- **SQLAlchemy models and business rules** retained and adapted rather than rewritten.

This separation removes Streamlit rerun artifacts, stale widgets, delayed page replacement, automatic framework controls, and mixed login/dashboard rendering.

## 2. Proposed Architecture

```text
Browser / Mobile Browser
        |
        v
Next.js web application
  - Route layouts
  - Role navigation
  - Forms and tables
  - Image upload and result viewer
  - Responsive customer portal
        |
        | HTTPS JSON / multipart requests
        v
FastAPI application
  - Session authentication
  - Role and ownership authorization
  - Customer, vehicle, plan and report services
  - Damage analysis orchestration
  - PDF report generation
        |
        +---- MySQL: Vehicle_Analyzis
        +---- Existing YOLO models
        +---- Existing Python inference pipeline
        +---- Protected file storage
```

The browser must never load `.pt` model files. Models remain on the Python server and are loaded once by the FastAPI process.

## 3. Repository Layout

```text
vehicle-damade-dash-repo/
├── frontend/
│   ├── app/
│   │   ├── (public)/
│   │   │   └── login/
│   │   ├── (admin)/
│   │   ├── (operator)/
│   │   ├── (customer)/
│   │   ├── api/
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── application-shell/
│   │   ├── forms/
│   │   ├── tables/
│   │   ├── damage-viewer/
│   │   ├── reports/
│   │   └── ui/
│   ├── lib/
│   │   ├── api-client.ts
│   │   ├── auth.ts
│   │   ├── permissions.ts
│   │   └── validation.ts
│   ├── public/
│   ├── middleware.ts
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── api/
│   │   ├── auth.py
│   │   ├── customers.py
│   │   ├── vehicles.py
│   │   ├── analyses.py
│   │   ├── reports.py
│   │   ├── plans.py
│   │   ├── users.py
│   │   ├── company.py
│   │   └── audit.py
│   ├── schemas/
│   ├── dependencies/
│   └── middleware/
│
├── core/
├── database/
├── ml/
├── reports/
├── services/
├── storage/
├── Runscomplete/
└── yolov8n.pt
```

The existing `core`, `database`, `ml`, `reports`, and `services` packages stay in Python. FastAPI routes call those services.

## 4. Authentication Rules

### 4.1 Login boundary

- `/login` is the only unauthenticated application page.
- Every ERP route is protected by Next.js middleware.
- Every FastAPI endpoint independently verifies authentication.
- Invalid or expired sessions return `401`.
- Unauthorized roles return `403`.
- A new browser session requires login.
- Page navigation within an active session does not require repeated login.
- Session timeout remains configurable.
- Logout invalidates the server session and clears the secure cookie.

### 4.2 Session implementation

Use a random server-side session token:

- Store only an opaque token in an `HttpOnly`, `Secure`, `SameSite=Lax` cookie.
- Store the token hash, user ID, expiry, and last activity in the database.
- Rotate the session token after login and password change.
- Never store roles, customer IDs, or authorization decisions only in browser storage.
- Do not use local storage for authentication tokens.

### 4.3 Customer account creation

There is **no public registration page**.

A customer can log in only when:

1. An admin or operator registers a customer in the ERP.
2. “Create customer portal account” is selected.
3. The backend creates a user with role `customer`.
4. The user record is linked to that exact `customer_id`.
5. A temporary password is issued.
6. The customer changes the password on first login.

The backend rejects any customer login whose account has no linked customer record.

## 5. Role and Page Matrix

| Area | Admin | Operator | Customer |
|---|---|---|---|
| Overview | System-wide | Operations | Own vehicles and reports |
| New analysis | Create | Create | No access |
| Analysis review | Edit/finalize | Edit/finalize | Own finalized analyses, read-only |
| Damage reports | All | All | Own reports only |
| Customers | Manage | Manage | No access |
| Vehicles | Manage | Manage | No management page |
| Insurance plans | Manage | View only | No access |
| User management | Manage | No access | No access |
| Company settings | Manage | No access | No access |
| Audit logs | View | No access | No access |
| Model diagnostics | View/test | No access | No access |
| Profile/password | Own account | Own account | Own account |

Frontend visibility is for usability. FastAPI permissions remain the real enforcement.

## 6. Customer Ownership Rules

All customer-facing database queries must include the authenticated `customer_id`.

- Customer vehicles: `vehicles.customer_id == session.customer_id`
- Customer analyses: analysis vehicle belongs to `session.customer_id`
- Customer reports: report analysis vehicle belongs to `session.customer_id`
- Customer downloads: ownership is checked again before returning the PDF
- Customers see only finalized analyses
- Customers cannot see internal notes, override reasons intended for staff, audit data, model paths, or model hashes
- Customers cannot change damage classes, severity, repair costs, review status, or finalization status
- Guessing or changing an ID must return `404` without revealing whether another customer’s record exists

## 7. API Plan

### Authentication

```text
POST   /api/auth/login
POST   /api/auth/logout
GET    /api/auth/session
POST   /api/auth/change-password
```

### Customers and accounts

```text
GET    /api/customers
POST   /api/customers
GET    /api/customers/{id}
PATCH  /api/customers/{id}
POST   /api/customers/{id}/portal-account
```

### Vehicles

```text
GET    /api/vehicles
POST   /api/vehicles
GET    /api/vehicles/{id}
PATCH  /api/vehicles/{id}
POST   /api/vehicles/{id}/images
```

### Analysis and model processing

```text
POST   /api/analyses
GET    /api/analyses
GET    /api/analyses/{id}
PATCH  /api/analyses/{id}/damages/{damage_id}
POST   /api/analyses/{id}/vehicle-override
POST   /api/analyses/{id}/finalize
```

### Reports

```text
GET    /api/reports
GET    /api/reports/{id}
GET    /api/reports/{id}/pdf
```

### Administration

```text
GET/POST/PATCH /api/plans
GET/POST/PATCH /api/users
GET/PATCH      /api/company
GET            /api/audit-logs
GET            /api/system/models
```

## 8. Model Functionality

The model process remains Python-based:

1. Next.js uploads an image to FastAPI using `multipart/form-data`.
2. FastAPI validates MIME type, extension, file signature, dimensions, and maximum size.
3. The current EXIF correction is applied.
4. `yolov8n.pt` performs vehicle confirmation.
5. `best.pt` performs damage segmentation.
6. Vehicle and damage overlap validation runs unchanged.
7. FastAPI stores the original image, annotated image, detections, thresholds, and model hashes.
8. FastAPI returns structured JSON with damage polygons, boxes, labels, confidence, and status.
9. Next.js renders the overlay using an HTML canvas or positioned SVG generated from coordinates.
10. Operators review findings and assign repair details.
11. Finalization creates the existing PDF report.

The trained model files are not converted and are not retrained during the frontend migration.

## 9. Frontend Application Plan

### 9.1 Application shell

- Fixed desktop sidebar with grouped role navigation
- Mobile drawer navigation
- Top bar with page title, theme switch, account menu, and logout
- No framework controls or development branding
- Route loading indicator
- Skeletons only inside the section being loaded
- Previous page content is removed immediately when navigation begins
- Error boundaries for page and component failures
- Toasts for completed actions

### 9.2 Theme system

- Use CSS variables and a `data-theme="light|dark"` attribute
- Persist appearance preference in a non-sensitive cookie
- Respect operating-system preference on first visit
- Both themes define every component state
- Test normal, hover, focus, selected, disabled, loading, success, warning, and error states

### 9.3 Icons

- Use one consistent React icon library such as **Lucide React**
- No emojis
- No manually embedded SVG markup in page files
- Icons always have accessible labels where needed

### 9.4 Forms

- React Hook Form
- Zod validation
- Field-specific error messages
- Submit buttons show progress and prevent duplicate requests
- Cancelled or failed requests restore controls correctly
- Unsaved-change warning for long forms

### 9.5 Tables

- TanStack Table
- Server pagination and filtering
- Responsive card representation on narrow screens
- Clear empty, loading, and error states
- Accessible row actions

## 10. Mobile Customer Portal

The customer portal is designed mobile-first at 320 px and above.

### Customer overview

- Customer name
- Registered vehicles
- Vehicle photo
- Latest finalized assessment status
- Total estimated repair cost
- Direct report access

### Vehicle page

- Registration number
- Make, model, year, and colour
- Current policy summary
- Vehicle photo
- Assessment history

### Assessment page

- Original and annotated image viewer
- Pinch-friendly image area
- Damage cards with part, type, severity, confidence, description, and approved cost
- No edit controls
- No internal staff notes

### Report page

- Report summary
- Damage list
- Cost totals
- PDF download
- Large touch targets

### Mobile requirements

- No horizontal page scrolling
- Minimum 44 px touch targets
- Forms usable with the on-screen keyboard
- Safe-area padding
- Responsive text without clipped headings
- Tested at 320, 360, 390, 430, 768, and 1024 px widths

## 11. Interface Writing Rules

Do not use promotional or generic generated-sounding text.

Avoid wording such as:

> A secure workspace for policyholders and claims teams to register vehicles, review model-assisted damage findings, and issue traceable assessment reports.

Use short operational copy:

- Login: `Sign in to continue`
- Admin overview: `Customers, vehicles and assessment activity`
- Operator overview: `Open assessments and recent reports`
- Customer overview: `Your vehicles and damage reports`
- New analysis: `Upload a vehicle image and review detected damage`
- Empty reports: `No finalized reports are available`
- Failure: `The image could not be processed. Try another image or contact an administrator`

Other copy rules:

- Do not describe ordinary functions as intelligent, revolutionary, seamless, or powerful
- Use “damage detection” or “model result” only where technically useful
- Prefer verbs: `Create customer`, `Register vehicle`, `Run analysis`, `Save costs`, `Finalize report`
- Keep labels and confirmation messages consistent
- Do not expose implementation terms to customers

## 12. Migration Phases

### Phase 1 — Freeze and contract

- Freeze new Streamlit UI work
- Inventory existing screens and permissions
- Define Pydantic request and response schemas
- Record current model regression images and expected outputs
- Back up the MySQL database and storage directory

### Phase 2 — FastAPI foundation

- Add FastAPI application
- Add configuration and startup validation
- Add session tables and cookie authentication
- Add role and ownership dependencies
- Expose health and authenticated-session endpoints
- Add OpenAPI tests

### Phase 3 — ERP APIs

- Customers
- Customer portal account creation
- Vehicles and images
- Plans
- Users
- Company information
- Audit logs

### Phase 4 — Model and report APIs

- Image upload
- Existing inference pipeline adapter
- Analysis persistence
- Operator review and costing
- Finalization
- PDF generation and protected download

### Phase 5 — Next.js foundation

- App Router
- Public login layout
- Protected layouts
- Role middleware
- API client
- Theme provider
- Application shell and navigation

### Phase 6 — Admin and operator screens

- Role overview
- Customers
- Vehicles
- New analysis
- Analysis review
- Reports
- Plans
- Administration screens

### Phase 7 — Customer portal

- Customer overview
- Own vehicle details
- Own finalized assessments
- Own reports
- Profile and password change
- Mobile accessibility and responsive testing

### Phase 8 — Verification and cutover

- API unit and integration tests
- Permission matrix tests
- Cross-customer isolation tests
- Model regression tests
- PDF tests
- Playwright browser tests
- Mobile viewport tests
- Parallel comparison with Streamlit
- Data backup
- Final cutover
- Retain Streamlit only as a temporary rollback option

## 13. Test Requirements

- Unauthenticated access to every protected URL redirects to login
- Admin routes are inaccessible to operator and customer accounts
- Customer A cannot access Customer B data using modified IDs
- Operator cannot modify plans
- Customer cannot call mutation endpoints
- Expired and logged-out sessions fail immediately
- Duplicate form submissions do not create duplicate records
- Image upload validation rejects corrupted or oversized files
- Model outputs match saved regression expectations
- PDF downloads require ownership
- Light and dark themes pass contrast checks
- Navigation never leaves elements from the previous route
- Customer screens pass all defined mobile widths

## 14. Cutover Acceptance Criteria

- No Streamlit UI is used in the production workflow
- Existing model artifacts run unchanged
- Existing damage classes and review flow remain available
- All role navigation matches the permission matrix
- Customer login exists only for customers registered by staff
- Customer data is isolated by backend ownership checks
- Customer portal is fully usable on mobile
- Light and dark modes style every control
- PDF reports generate and download correctly
- MySQL is the active database
- Automated tests pass
- No old page remains visible during navigation

## 15. Recommendation

Proceed with **Next.js + FastAPI**.

Do not rewrite model inference in Node.js. Keep Python responsible for model loading, image processing, reporting, and ERP services. Use Next.js only for the web interface and browser-side interactions.
