# Vehicle Damage Insurance ERP — Master Implementation Plan

## 1. Document purpose

This document is the complete implementation blueprint for converting the
existing Streamlit vehicle-damage testing dashboard into a role-based insurance
company ERP.

The implementation must:

- Preserve the existing trained damage model and analysis methodology.
- Preserve the current dark automotive-inspection visual identity.
- Add secure authentication and role-based access.
- Register customers and their vehicles.
- Store vehicle images and analysis history.
- Allow operators to review model predictions and add repair costs.
- Give customers a mobile-responsive portal.
- Generate detailed, printable vehicle-damage reports.
- Store business data in MySQL database `Vehicle_Analyzis`.
- Use phpMyAdmin only to administer MySQL, not as the application backend.
- Support additional trained models later without redesigning the ERP.
- Deliver a polished, professional interface at least equal to the existing
  damage dashboard.
- Use no stock photographs, AI-generated illustrations, decorative hero
  images, or unrelated background imagery.

This plan intentionally divides the work into independently testable phases.
Do not start a later phase until the validation gate for the current phase
passes.

---

## 2. Existing assets that must be preserved

### 2.1 Damage model

Canonical model:

```text
Runscomplete/runs/vehicle_damage_seg-2/weights/best.pt
```

Expected SHA-256:

```text
C9D86E67A4C14F65047F33C17B4C4357613A0A15B52F919D76FF1C8542C0D541
```

Damage classes:

1. `scratch`
2. `dent`
3. `tear`
4. `missing_part`
5. `broken_lamp`
6. `puncture`
7. `broken_glass`

### 2.2 Vehicle-confirmation model

Canonical model:

```text
yolov8n.pt
```

Expected SHA-256:

```text
F59B3D833E2FF32E194B5BB8E08D211DC7C5BDF144B90D2C8412C47CCFC83B36
```

Supported COCO vehicle classes:

- Car
- Motorcycle
- Bus
- Truck

### 2.3 Existing analysis behavior

The current workflow in `model_tester.py` must initially remain behaviorally
equivalent:

1. Load an uploaded image as RGB.
2. Run the vehicle-confirmation model.
3. Keep supported vehicle boxes.
4. Run the trained segmentation model.
5. Obtain class, confidence, box and segmentation polygon.
6. When confirmation is required, accept damage only when its centre is inside
   a vehicle box or at least 20% of its box overlaps a vehicle box.
7. Render vehicle boxes, damage boxes, masks and labels.
8. Show damage confidence and class.

The refactor must be proven against fixed regression images before ERP
development continues.

### 2.4 Known model limitations

- Mask precision is approximately 53.78%.
- Mask recall is approximately 40.57%.
- Mask mAP50 is approximately 41.20%.
- Mask mAP50-95 is approximately 22.15%.
- The vehicle model can fail on close-up panels because a complete vehicle
  shape is not visible.
- A prediction is advisory and must never automatically approve an insurance
  claim.
- Operators require an override option for legitimate close-up images.
- Every override and manual correction must be recorded in the audit log.

---

## 3. Scope

### 3.1 Included in the first complete release

- Secure login and logout
- Password change
- Forced password change after account creation/reset
- Admin, operator and customer roles
- User activation and deactivation
- Company profile and logo
- Insurance plan management
- Customer registration and maintenance
- Vehicle registration and maintenance
- Vehicle image management
- Damage analysis using the existing models
- Vehicle-confirmation override
- Operator review of predictions
- Manual damage entry
- Damage rejection and correction
- Damage severity and notes
- Cost entry for each damage
- Analysis total calculation
- Analysis finalization
- Detailed PDF report generation
- Customer portal
- Customer vehicle and report viewing
- Customer total-cost viewing
- Administrative dashboards
- Customer reports
- Vehicle reports
- Analysis reports
- Cost reports
- CSV export where appropriate
- Audit logs
- Database migrations
- Backup and restore documentation
- Automated tests
- Windows deployment documentation

### 3.2 Explicitly outside the first release

- Automatic claim approval
- Payment gateway
- Repair-shop procurement
- Parts inventory
- Accounting ledger
- Email/SMS sending unless credentials are later provided
- Native Android or iOS applications
- Customer self-registration
- Automatic cost prediction by AI
- Facial recognition
- Live camera streaming
- Multi-company tenancy

These may be added later without changing the core schema.

---

## 4. Required technology stack

### 4.1 Application

- Python 3.11 or 3.12
- Streamlit multipage interface
- SQLAlchemy 2.x ORM
- Alembic database migrations
- PyMySQL MySQL driver
- Pydantic Settings for configuration
- Argon2 password hashing
- Ultralytics pinned to the verified compatible version
- PyTorch
- OpenCV
- Pillow
- Pandas
- ReportLab for deterministic PDF generation

### 4.2 Database

- MySQL 8.x
- Database: `Vehicle_Analyzis`
- Character set: `utf8mb4`
- Collation: `utf8mb4_unicode_ci`
- phpMyAdmin for administration

### 4.3 Deployment

- Windows host for the first deployment
- Local filesystem for protected image/report storage
- HTTPS reverse proxy for any network-accessible deployment
- MySQL application user with limited privileges
- The MySQL `root` account must not be used by the Streamlit application

---

## 5. Proposed project structure

```text
vehicle-damade-dash/
├── app.py
├── requirements.txt
├── .env.example
├── alembic.ini
├── README.md
├── INSURANCE_ERP_MASTER_PLAN.md
│
├── assets/
│   ├── styles.css
│   ├── company_logo_placeholder.png
│   └── report/
│
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── constants.py
│   ├── exceptions.py
│   ├── logging_config.py
│   ├── security.py
│   ├── session.py
│   └── permissions.py
│
├── database/
│   ├── __init__.py
│   ├── base.py
│   ├── connection.py
│   ├── models/
│   │   ├── user.py
│   │   ├── customer.py
│   │   ├── vehicle.py
│   │   ├── plan.py
│   │   ├── analysis.py
│   │   ├── report.py
│   │   ├── company.py
│   │   └── audit.py
│   └── repositories/
│       ├── user_repository.py
│       ├── customer_repository.py
│       ├── vehicle_repository.py
│       ├── plan_repository.py
│       ├── analysis_repository.py
│       ├── report_repository.py
│       └── audit_repository.py
│
├── services/
│   ├── authentication_service.py
│   ├── user_service.py
│   ├── customer_service.py
│   ├── vehicle_service.py
│   ├── plan_service.py
│   ├── analysis_service.py
│   ├── costing_service.py
│   ├── report_service.py
│   ├── storage_service.py
│   └── dashboard_service.py
│
├── ml/
│   ├── __init__.py
│   ├── model_registry.py
│   ├── vehicle_validator.py
│   ├── damage_analyzer.py
│   ├── matching.py
│   ├── annotator.py
│   ├── pipeline.py
│   └── types.py
│
├── ui/
│   ├── layout.py
│   ├── navigation.py
│   ├── theme.py
│   ├── forms.py
│   ├── tables.py
│   ├── messages.py
│   └── cards.py
│
├── pages/
│   ├── login.py
│   ├── admin_dashboard.py
│   ├── operator_dashboard.py
│   ├── customer_dashboard.py
│   ├── users.py
│   ├── customers.py
│   ├── customer_detail.py
│   ├── vehicles.py
│   ├── vehicle_detail.py
│   ├── analysis_new.py
│   ├── analysis_review.py
│   ├── analysis_detail.py
│   ├── reports.py
│   ├── plans.py
│   ├── company_settings.py
│   ├── audit_logs.py
│   ├── profile.py
│   └── change_password.py
│
├── reports/
│   ├── pdf_builder.py
│   ├── report_styles.py
│   ├── sections.py
│   └── templates/
│
├── migrations/
│   ├── env.py
│   └── versions/
│
├── scripts/
│   ├── bootstrap_database.py
│   ├── create_admin.py
│   ├── verify_environment.py
│   ├── backup_database.ps1
│   └── restore_database.ps1
│
├── storage/
│   ├── company/
│   ├── customers/
│   ├── vehicles/
│   ├── analyses/
│   ├── reports/
│   └── temp/
│
├── models/
│   ├── damage/
│   │   └── best.pt
│   └── vehicle/
│       └── yolov8n.pt
│
└── tests/
    ├── unit/
    ├── integration/
    ├── permissions/
    ├── ml_regression/
    ├── reports/
    └── fixtures/
```

---

## 6. Configuration and environment variables

Create `.env.example` with placeholders only:

```dotenv
APP_ENV=development
APP_NAME=Vehicle Damage Insurance ERP
APP_BASE_URL=http://localhost:8501
SESSION_TIMEOUT_MINUTES=30

MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=Vehicle_Analyzis
MYSQL_USER=vehicle_erp_app
MYSQL_PASSWORD=change-this-password

STORAGE_ROOT=storage
DAMAGE_MODEL_PATH=models/damage/best.pt
VEHICLE_MODEL_PATH=models/vehicle/yolov8n.pt

DEFAULT_DAMAGE_CONFIDENCE=0.30
DEFAULT_VEHICLE_CONFIDENCE=0.25
DEFAULT_REQUIRE_VEHICLE=true
DEFAULT_CURRENCY=LKR

LOG_LEVEL=INFO
```

Rules:

- Commit `.env.example`.
- Never commit `.env`.
- Never log database passwords.
- Fail application startup with a clear message when required values are
  missing.
- Validate storage and model paths during startup.
- Display model hashes in the admin diagnostics page.

---

## 7. MySQL setup

### 7.1 Create database

Run through phpMyAdmin SQL or the MySQL command line:

```sql
CREATE DATABASE IF NOT EXISTS Vehicle_Analyzis
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;
```

### 7.2 Create application user

Example:

```sql
CREATE USER IF NOT EXISTS 'vehicle_erp_app'@'localhost'
IDENTIFIED BY 'replace-with-a-long-random-password';

GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX
ON Vehicle_Analyzis.*
TO 'vehicle_erp_app'@'localhost';

FLUSH PRIVILEGES;
```

Do not grant:

- Global privileges
- User-management privileges
- File privileges
- Shutdown privileges

### 7.3 Migration policy

- All schema changes must use Alembic migrations.
- Never manually edit production table structures in phpMyAdmin.
- Every migration must have an upgrade and downgrade path.
- Take a backup before applying a production migration.
- Record the migration version in deployment notes.

---

## 8. Database design

All primary keys use unsigned `BIGINT`.
All timestamps are stored in UTC.
Application screens display the configured local timezone.

### 8.1 `roles`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `code` | VARCHAR(30) | Unique; `admin`, `operator`, `customer` |
| `name` | VARCHAR(60) | Display name |
| `description` | VARCHAR(255) | Nullable |
| `created_at` | DATETIME | Required |

Seed exactly three roles.

### 8.2 `users`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `role_id` | BIGINT | FK to `roles.id` |
| `customer_id` | BIGINT | Nullable FK to `customers.id` |
| `username` | VARCHAR(80) | Unique, case-insensitive |
| `email` | VARCHAR(255) | Unique, normalized lowercase |
| `password_hash` | VARCHAR(255) | Argon2 hash only |
| `must_change_password` | BOOLEAN | Default true for created/reset accounts |
| `is_active` | BOOLEAN | Default true |
| `failed_login_count` | INT | Default 0 |
| `locked_until` | DATETIME | Nullable |
| `last_login_at` | DATETIME | Nullable |
| `password_changed_at` | DATETIME | Nullable |
| `created_by` | BIGINT | Nullable FK to users |
| `created_at` | DATETIME | Required |
| `updated_at` | DATETIME | Required |

Constraints:

- Customer-role users must have `customer_id`.
- Admin/operator users must not require `customer_id`.
- Deactivating a customer does not delete their report history.
- Password hashes and temporary passwords never appear in logs.

Indexes:

- Unique `username`
- Unique `email`
- Index `role_id`
- Index `customer_id`
- Index `is_active`

### 8.3 `customers`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `customer_code` | VARCHAR(30) | Unique, generated |
| `full_name` | VARCHAR(150) | Required |
| `nic_or_passport` | VARCHAR(60) | Unique when present |
| `date_of_birth` | DATE | Nullable |
| `phone_primary` | VARCHAR(30) | Required |
| `phone_secondary` | VARCHAR(30) | Nullable |
| `email` | VARCHAR(255) | Required |
| `address_line_1` | VARCHAR(255) | Required |
| `address_line_2` | VARCHAR(255) | Nullable |
| `city` | VARCHAR(100) | Required |
| `postal_code` | VARCHAR(20) | Nullable |
| `notes` | TEXT | Nullable; internal only |
| `status` | VARCHAR(20) | `active`, `inactive` |
| `created_by` | BIGINT | FK to users |
| `created_at` | DATETIME | Required |
| `updated_at` | DATETIME | Required |

Customer code format:

```text
CUS-YYYY-000001
```

### 8.4 `vehicles`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `customer_id` | BIGINT | Required FK |
| `vehicle_code` | VARCHAR(30) | Unique, generated |
| `registration_number` | VARCHAR(40) | Unique, normalized uppercase |
| `chassis_number` | VARCHAR(80) | Unique when present |
| `engine_number` | VARCHAR(80) | Nullable |
| `make` | VARCHAR(100) | Required |
| `model` | VARCHAR(100) | Required |
| `manufactured_year` | SMALLINT | Valid range |
| `colour` | VARCHAR(60) | Required |
| `vehicle_type` | VARCHAR(40) | Car, motorcycle, bus or truck |
| `fuel_type` | VARCHAR(40) | Nullable |
| `odometer_km` | INT | Nullable, non-negative |
| `primary_image_id` | BIGINT | Nullable until image exists |
| `status` | VARCHAR(20) | Active, inactive, sold |
| `created_by` | BIGINT | FK to users |
| `created_at` | DATETIME | Required |
| `updated_at` | DATETIME | Required |

Vehicle code format:

```text
VEH-YYYY-000001
```

### 8.5 `vehicle_images`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `vehicle_id` | BIGINT | Required FK |
| `analysis_id` | BIGINT | Nullable FK |
| `image_category` | VARCHAR(40) | Profile, front, rear, left, right, damage, other |
| `original_filename` | VARCHAR(255) | Sanitized display value |
| `storage_path` | VARCHAR(500) | Relative path only |
| `mime_type` | VARCHAR(100) | Allow-listed |
| `file_size_bytes` | BIGINT | Required |
| `width_px` | INT | Required |
| `height_px` | INT | Required |
| `sha256` | CHAR(64) | Required |
| `is_primary` | BOOLEAN | Default false |
| `uploaded_by` | BIGINT | FK to users |
| `uploaded_at` | DATETIME | Required |

Rules:

- Allow JPEG, PNG and WEBP only.
- Decode every upload to confirm it is an image.
- Set a configurable maximum upload size.
- Generate a UUID storage filename.
- Never use the original filename as the disk filename.
- Keep only one primary image per vehicle.

### 8.6 `insurance_plans`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `plan_code` | VARCHAR(30) | Unique |
| `name` | VARCHAR(120) | Required |
| `description` | TEXT | Required |
| `coverage_limit` | DECIMAL(15,2) | Nullable |
| `deductible_amount` | DECIMAL(15,2) | Default 0 |
| `currency_code` | CHAR(3) | Required |
| `is_active` | BOOLEAN | Default true |
| `created_by` | BIGINT | FK to users |
| `created_at` | DATETIME | Required |
| `updated_at` | DATETIME | Required |

### 8.7 `vehicle_policies`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `vehicle_id` | BIGINT | Required FK |
| `plan_id` | BIGINT | Required FK |
| `policy_number` | VARCHAR(80) | Unique |
| `start_date` | DATE | Required |
| `end_date` | DATE | Required, after start |
| `premium_amount` | DECIMAL(15,2) | Nullable |
| `status` | VARCHAR(20) | Draft, active, expired, cancelled |
| `notes` | TEXT | Nullable |
| `created_by` | BIGINT | FK to users |
| `created_at` | DATETIME | Required |
| `updated_at` | DATETIME | Required |

### 8.8 `model_versions`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `model_key` | VARCHAR(80) | Unique internal key |
| `display_name` | VARCHAR(120) | Required |
| `model_type` | VARCHAR(40) | Vehicle detector, damage segmenter, part detector |
| `file_path` | VARCHAR(500) | Relative configured path |
| `sha256` | CHAR(64) | Required |
| `classes_json` | JSON | Required |
| `framework` | VARCHAR(80) | Example: Ultralytics |
| `framework_version` | VARCHAR(40) | Required |
| `is_active` | BOOLEAN | Default false |
| `created_at` | DATETIME | Required |

Only administrators may activate a model.
Historical analyses continue referencing the original model-version row.

### 8.9 `analyses`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `analysis_number` | VARCHAR(40) | Unique |
| `vehicle_id` | BIGINT | Required FK |
| `operator_id` | BIGINT | Required FK |
| `damage_model_version_id` | BIGINT | Required FK |
| `vehicle_model_version_id` | BIGINT | Required FK |
| `source_image_id` | BIGINT | Required FK |
| `annotated_image_path` | VARCHAR(500) | Nullable until inference |
| `status` | VARCHAR(30) | Draft, analyzed, under_review, finalized, superseded |
| `damage_confidence` | DECIMAL(5,4) | Required |
| `vehicle_confidence` | DECIMAL(5,4) | Required |
| `require_vehicle_confirmation` | BOOLEAN | Required |
| `vehicle_confirmed` | BOOLEAN | Required |
| `confirmation_overridden` | BOOLEAN | Default false |
| `override_reason` | VARCHAR(500) | Required when overridden |
| `raw_prediction_count` | INT | Required |
| `accepted_damage_count` | INT | Required |
| `rejected_damage_count` | INT | Required |
| `subtotal_cost` | DECIMAL(15,2) | Default 0 |
| `tax_amount` | DECIMAL(15,2) | Default 0 |
| `discount_amount` | DECIMAL(15,2) | Default 0 |
| `total_estimated_cost` | DECIMAL(15,2) | Default 0 |
| `currency_code` | CHAR(3) | Required |
| `operator_notes` | TEXT | Nullable |
| `analyzed_at` | DATETIME | Nullable |
| `finalized_at` | DATETIME | Nullable |
| `finalized_by` | BIGINT | Nullable FK |
| `created_at` | DATETIME | Required |
| `updated_at` | DATETIME | Required |

Analysis number format:

```text
VDA-YYYYMMDD-000001
```

Finalized analyses become immutable. Corrections create a revision.

### 8.10 `analysis_vehicle_detections`

Store raw vehicle-model output:

| Column | Type |
|---|---|
| `id` | BIGINT |
| `analysis_id` | BIGINT |
| `vehicle_class` | VARCHAR(60) |
| `confidence` | DECIMAL(7,6) |
| `box_json` | JSON |
| `created_at` | DATETIME |

### 8.11 `analysis_damages`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `analysis_id` | BIGINT | Required FK |
| `source` | VARCHAR(20) | Model or manual |
| `original_damage_class` | VARCHAR(80) | Nullable for manual |
| `final_damage_class` | VARCHAR(80) | Required |
| `vehicle_part` | VARCHAR(100) | Nullable until operator enters |
| `confidence` | DECIMAL(7,6) | Nullable for manual |
| `box_json` | JSON | Required |
| `polygon_json` | JSON | Nullable |
| `overlap_ratio` | DECIMAL(7,6) | Nullable |
| `passed_vehicle_gate` | BOOLEAN | Required |
| `review_status` | VARCHAR(20) | Pending, accepted, rejected, corrected |
| `severity` | VARCHAR(20) | Minor, moderate, severe, critical |
| `description` | TEXT | Customer-visible description |
| `internal_note` | TEXT | Staff-only |
| `estimated_cost` | DECIMAL(15,2) | Default 0 |
| `reviewed_by` | BIGINT | Nullable FK |
| `reviewed_at` | DATETIME | Nullable |
| `created_at` | DATETIME | Required |
| `updated_at` | DATETIME | Required |

Rejected detections remain stored for audit but do not appear in customer
reports or totals.

### 8.12 `analysis_revisions`

| Column | Type |
|---|---|
| `id` | BIGINT |
| `original_analysis_id` | BIGINT |
| `replacement_analysis_id` | BIGINT |
| `reason` | TEXT |
| `created_by` | BIGINT |
| `created_at` | DATETIME |

### 8.13 `reports`

| Column | Type | Rules |
|---|---|---|
| `id` | BIGINT | Primary key |
| `report_number` | VARCHAR(50) | Unique |
| `analysis_id` | BIGINT | Required FK |
| `revision_number` | INT | Default 1 |
| `pdf_path` | VARCHAR(500) | Required |
| `sha256` | CHAR(64) | Required |
| `snapshot_json` | JSON | Required |
| `generated_by` | BIGINT | Required FK |
| `generated_at` | DATETIME | Required |
| `is_current` | BOOLEAN | Default true |

Report number format:

```text
RPT-VDA-YYYYMMDD-000001-R01
```

### 8.14 `company_information`

Use one active row:

| Column | Type |
|---|---|
| `id` | BIGINT |
| `company_name` | VARCHAR(200) |
| `registration_number` | VARCHAR(100) |
| `address_line_1` | VARCHAR(255) |
| `address_line_2` | VARCHAR(255) |
| `city` | VARCHAR(100) |
| `phone` | VARCHAR(40) |
| `email` | VARCHAR(255) |
| `website` | VARCHAR(255) |
| `logo_path` | VARCHAR(500) |
| `currency_code` | CHAR(3) |
| `tax_label` | VARCHAR(30) |
| `tax_rate` | DECIMAL(7,4) |
| `report_footer` | TEXT |
| `updated_by` | BIGINT |
| `updated_at` | DATETIME |

### 8.15 `audit_logs`

| Column | Type |
|---|---|
| `id` | BIGINT |
| `user_id` | BIGINT nullable |
| `action` | VARCHAR(100) |
| `entity_type` | VARCHAR(80) |
| `entity_id` | BIGINT nullable |
| `old_values_json` | JSON nullable |
| `new_values_json` | JSON nullable |
| `ip_address` | VARCHAR(64) nullable |
| `user_agent` | VARCHAR(500) nullable |
| `success` | BOOLEAN |
| `failure_reason` | VARCHAR(500) nullable |
| `created_at` | DATETIME |

Never place password hashes, passwords or database credentials in audit values.

---

## 9. Authentication and session requirements

### 9.1 Login

Login accepts username or email plus password.

Process:

1. Normalize the submitted identifier.
2. Find an active user.
3. Check account lock.
4. Verify Argon2 hash.
5. On failure, increment failed-login count.
6. Lock temporarily after the configured number of failures.
7. On success, clear failure count.
8. Store only user ID, role and authentication timestamp in session.
9. Record successful or failed login in audit log.
10. Redirect to the role-specific dashboard.
11. If `must_change_password` is true, redirect only to password change.

### 9.2 Password rules

- Minimum 10 characters
- At least one uppercase character
- At least one lowercase character
- At least one number
- At least one symbol
- Must differ from the current password
- Never display an existing password
- Hash with Argon2id

### 9.3 Password change

Customer process:

1. Enter current password.
2. Enter new password.
3. Confirm new password.
4. Validate strength.
5. Replace hash.
6. Set `must_change_password` false.
7. Record audit event.
8. Keep the current user logged in.

### 9.4 Administrative reset

- Admin may reset any account.
- Operator may reset customer accounts only.
- Generate a temporary password.
- Display it once.
- Store only its hash.
- Set `must_change_password` true.
- Audit the reset without recording the temporary password.

### 9.5 Session behavior

- Idle timeout default: 30 minutes.
- Logout clears all session data.
- Role checks occur on every protected page.
- Direct navigation to a forbidden page redirects to an access-denied page.
- A deactivated user is logged out on the next database-backed permission check.

---

## 10. Permission matrix

| Function | Admin | Operator | Customer |
|---|---:|---:|---:|
| Login/logout | Yes | Yes | Yes |
| Change own password | Yes | Yes | Yes |
| View company information | Yes | Yes | Yes |
| Edit company information | Yes | No | No |
| Manage admins | Yes | No | No |
| Manage operators | Yes | No | No |
| Create customer account | Yes | Yes | No |
| Edit customer | Yes | Yes | Own profile fields only if enabled |
| Disable customer | Yes | No | No |
| View customers | All | All | Self only |
| Register vehicle | Yes | Yes | No |
| Edit vehicle | Yes | Yes | No |
| View vehicle | All | All | Own only |
| Upload vehicle images | Yes | Yes | No |
| Run analysis | Yes | Yes | No |
| Override vehicle check | Yes | Yes with reason | No |
| Review predictions | Yes | Yes | No |
| Add damage cost | Yes | Yes | No |
| Finalize analysis | Yes | Yes | No |
| Revise finalized analysis | Yes | No | No |
| View analysis | All | All | Own finalized only |
| Download report | Yes | Yes | Own finalized only |
| Manage insurance plans | Yes | No | No |
| View aggregate reports | Yes | Limited operational | No |
| View audit log | Yes | No | No |
| Activate model version | Yes | No | No |

Permission checks must exist in both UI navigation and service methods.

---

## 11. User interface design system

### 11.1 Visual direction

The product is a professional insurance inspection workspace. Its visual
language must come from vehicle inspection records, evidence marking, claim
review and cost assessment—not generic dashboard decoration.

Preserve and refine the existing automotive inspection interface:

- Deep graphite background
- Cool steel surfaces
- Teal/green confirmation state
- Amber caution state
- Red destructive/error state
- Blue damage overlays
- Existing rounded inspection cards
- High-contrast data labels
- Precise spacing and alignment
- Restrained use of colour
- Consistent field, table and status styling
- Clear visual distinction between model output and human decisions

Suggested tokens:

```text
Canvas:       #090D12
Surface:      #101820
Surface high: #17222D
Border:       #26313D
Text:         #E9F0F5
Muted text:   #91A1AE
Verified:     #50DBB7
Caution:      #FFBD59
Danger:       #FF5964
Analysis:     #46BEFF
```

Professional-quality requirements:

- Do not use default unstyled Streamlit components where a shared styled
  component exists.
- Use one consistent spacing scale across every page.
- Use one consistent radius scale across cards, inputs and dialogs.
- Keep page widths, gutters and section spacing consistent.
- Use short, direct labels such as `Register vehicle`, `Run analysis`,
  `Finalize report` and `Save cost`.
- Never use decorative gradients or glows unless they communicate analysis
  status.
- Avoid excessive KPI cards; display a metric only when it supports a decision.
- Use tables for dense operational records and cards for customer/mobile
  summaries.
- Empty states must explain the next valid action.
- Errors must say what failed and how the user can correct it.

### 11.2 Typography

Typography must remain readable and professional rather than decorative:

- Display/page headings: a restrained technical sans-serif, semibold.
- Body and form text: a highly legible UI sans-serif.
- Registration numbers, report numbers, model versions, currency totals and
  confidence values: tabular/monospaced utility styling where supported.
- Use sentence case for headings, fields and buttons.
- Do not use oversized marketing-style hero text inside the authenticated ERP.
- Maintain a clear scale for page title, section heading, field label, body,
  helper text and table metadata.

### 11.3 Functional-image policy

The ERP must not use decorative imagery.

Prohibited:

- Stock insurance photographs
- Stock vehicle photographs
- AI-generated illustrations
- Decorative hero/banner images
- Decorative image backgrounds
- Unrelated icons rendered as raster images
- Random avatars

Allowed because they serve a required business function:

- Company logo uploaded by an administrator
- Customer vehicle photographs
- Source inspection photographs
- Model-annotated damage photographs
- Cropped damage evidence generated from an inspection photograph
- Signature image only if the company later explicitly enables it
- QR/barcode generated for a report only if later required

Rules for allowed images:

- Every displayed image must have a business purpose and accessible label.
- Vehicle evidence images retain aspect ratio and may not be cosmetically
  altered.
- Thumbnails may be resized, but original files must remain unchanged.
- The UI must never substitute an example/stock vehicle image when no customer
  image exists.
- Missing images use a neutral text-and-icon empty state, not a placeholder
  photograph.
- Reports use only company and case-specific images.
- No remote image URL is loaded without validation and explicit business need.

### 11.4 Signature interface element

The product’s memorable element will be the **Inspection Evidence Rail**:

```text
Vehicle record → Source photo → Model findings → Operator decisions → Cost → Report
```

This rail represents the real insurance-review sequence. It appears on analysis
pages as a compact status trail and gives each step an explicit state:

- Not started
- In progress
- Needs review
- Completed
- Blocked

It replaces decorative hero imagery with meaningful case progress.

### 11.5 Navigation

Desktop:

- Persistent left navigation
- Company logo/name at top
- Role label
- Current-user menu
- Page title and context actions

Mobile customer portal:

- Compact top header
- Bottom navigation with Dashboard, Vehicles, Reports and Profile
- No persistent wide sidebar
- Single-column cards
- 44-pixel minimum touch targets

### 11.6 Shared components

- Page header
- Breadcrumb
- Search field
- Filter bar
- Status badge
- Empty state
- Confirmation dialog
- Success/error toast
- Pagination
- Audit metadata block
- Currency display
- Vehicle summary card
- Customer identity card
- Damage line-item card
- PDF download action

All components require normal, hover, focus, active, disabled, loading, success
and error states where applicable.

### 11.7 Accessibility

- Keyboard-visible focus
- Labels for every input
- Error text adjacent to input
- Colour is never the only status indicator
- Sufficient contrast
- Responsive at 320, 375, 768, 1024 and 1440 pixels
- Reduced-motion preference respected

### 11.8 Responsive behavior

Desktop:

- Persistent navigation
- Two-column image comparison where space permits
- Dense tables with filter controls
- Sticky case actions on long review pages

Tablet:

- Collapsible navigation
- Two-column layouts reduce to one or two columns based on width
- Tables allow deliberate horizontal scrolling only when unavoidable

Customer mobile:

- Single-column layout
- Bottom navigation
- Vehicle image shown before technical details
- Damage list displayed as stacked cards
- Total cost remains prominent but does not obstruct content
- Report download remains reachable with one hand
- No desktop table is merely shrunk to mobile width

### 11.9 UI review gate

Before completing each functional phase:

1. Capture desktop and mobile screenshots.
2. Compare spacing, typography and states with the existing dashboard.
3. Confirm no decorative/stock image was introduced.
4. Confirm every visible image is company- or case-specific.
5. Test keyboard navigation and focus.
6. Test empty, loading, success and failure states.
7. Remove any component that is decorative without supporting a decision.

---

## 12. Functional specifications by screen

### 12.1 Login screen

Fields:

- Username or email
- Password
- Show/hide password
- Sign in

Behavior:

- Do not reveal whether a username exists.
- Show lockout message with remaining time.
- Redirect based on role.
- Show company name and logo.
- Mobile responsive.

### 12.2 Admin dashboard

Display:

- Total active customers
- Total active vehicles
- Analyses today
- Analyses this month
- Finalized analyses
- Draft/under-review analyses
- Estimated total repair cost
- Damage count grouped by class
- Analysis trend by month
- Recent analyses
- Recently registered customers
- Expiring policies

Filters:

- Date range
- Operator
- Vehicle type
- Analysis status
- Damage type

### 12.3 Operator dashboard

Display:

- Create customer
- Register vehicle
- Start analysis
- Analyses awaiting review
- Draft analyses owned by operator
- Recently handled vehicles
- Today’s finalized reports

### 12.4 Customer dashboard

Display:

- Greeting and customer code
- Active policy summary
- Vehicle cards with primary images
- Latest finalized analysis per vehicle
- Damage count
- Total estimated cost
- Download latest report
- Company contact details

Customer screens must never expose:

- Other customers
- Internal notes
- Rejected model detections
- Audit history
- Raw model polygons
- Staff-only confidence controls

### 12.5 User management

Admin functions:

- Search users
- Filter by role/status
- Create admin/operator
- Edit name, email and username
- Activate/deactivate
- Reset password
- View last login
- View account lock status
- Unlock account

Deletion is not allowed when history references the user.
Use deactivation instead.

### 12.6 Customer list

Functions:

- Search by name, code, NIC/passport, phone or email
- Filter active/inactive
- Sort newest/name/code
- Paginate
- Create customer
- Open customer detail
- Export authorized customer summary CSV

### 12.7 Create/edit customer

Validation:

- Required name, phone, email and address
- Valid email format
- Normalized phone
- Unique NIC/passport when supplied
- Duplicate email warning

Optional account creation:

- Generate username
- Enter or generate temporary password
- Force password change
- Display password once

### 12.8 Customer detail

Sections:

- Identity and contact details
- Account status
- Registered vehicles
- Policy summary
- Analysis history
- Reports
- Internal notes for staff
- Audit timeline for admin

### 12.9 Vehicle list

Functions:

- Search registration, chassis, make, model and customer
- Filter type/status/policy
- Vehicle image thumbnail
- Customer link
- Latest analysis status
- Register vehicle
- Export summary

### 12.10 Vehicle registration

Fields:

- Owner/customer
- Registration number
- Chassis number
- Engine number
- Make
- Model
- Year
- Colour
- Vehicle type
- Fuel type
- Odometer
- Policy and plan
- Primary image

Validation:

- Unique registration
- Plausible year
- Non-negative odometer
- Image validation
- Owner must be active

### 12.11 Vehicle detail

Sections:

- Primary image and specifications
- Customer
- Current policy
- Image gallery
- Analysis timeline
- Latest damage summary
- Reports

Actions:

- Edit
- Upload image
- Start analysis
- View report

### 12.12 New analysis

Steps:

1. Choose customer.
2. Choose one of that customer’s vehicles.
3. Upload/select source image.
4. Select active model versions.
5. Configure thresholds if permitted.
6. Choose whether vehicle confirmation is mandatory.
7. Run analysis.
8. Display progress.
9. Store raw output transactionally.
10. Redirect to review.

Errors:

- Missing model
- Corrupt image
- Unsupported image
- Out-of-memory
- Inference exception
- Database failure
- Storage failure

An inference failure must not create a falsely completed analysis.

### 12.13 Analysis review

Show:

- Original image
- Annotated image
- Vehicle detections
- Accepted damages
- Rejected damages
- Confidence values
- Vehicle-confirmation status
- Model/version information

For each damage:

- Accept
- Reject
- Correct class
- Choose vehicle part
- Choose severity
- Enter customer-visible description
- Enter internal note
- Enter estimated cost

Additional actions:

- Add manual damage
- Override vehicle confirmation with mandatory reason
- Re-run with different threshold as a new attempt
- Save draft
- Mark reviewed
- Finalize

Finalization validation:

- At least one accepted/manual damage or explicit “no damage found” outcome
- Every accepted damage has severity
- Every accepted damage has a non-negative cost
- Vehicle and customer are valid
- Override reason exists when required
- Annotated image exists

### 12.14 Analysis detail

Show immutable finalized data:

- Analysis metadata
- Customer and vehicle
- Model versions
- Original/annotated images
- Final damage list
- Cost summary
- Report history
- Revision relationship

### 12.15 Insurance plan management

Admin can:

- Create plan
- Edit plan
- Activate/deactivate
- Set coverage limit
- Set deductible
- Assign plan to vehicle policy

Historical policies retain the original selected plan values in report
snapshots.

### 12.16 Company settings

Admin can edit:

- Company name
- Registration number
- Addresses
- Telephone
- Email
- Website
- Currency
- Tax label/rate
- Report footer
- Logo

Changes affect future reports only.

### 12.17 Report centre

Report types:

1. Detailed vehicle-damage report
2. Customer summary
3. Customer vehicle report
4. Vehicle detail/history report
5. Analysis register
6. Damage-type summary
7. Operator productivity report
8. Estimated repair-cost report
9. Policy/plan assignment report

Common filters:

- Date range
- Customer
- Vehicle
- Operator
- Damage class
- Severity
- Status
- Insurance plan

Export:

- PDF for formatted reports
- CSV for table reports

### 12.18 Customer reports

Customer may:

- View finalized reports for owned vehicles
- Filter by vehicle/date
- View total estimated cost
- Download PDF

Customer may not:

- View drafts
- View superseded report unless marked available
- Modify costs
- Access another customer’s report URL

### 12.19 Profile and password

All roles:

- View username, email and role
- Change password
- View last login

Customer may edit only explicitly permitted contact fields.

---

## 13. Machine-learning integration

### 13.1 Model registry

`model_registry.py` must:

- Load configured active models lazily.
- Cache models per process.
- Verify file existence.
- Calculate/verify SHA-256.
- Expose class names.
- Expose model version metadata.
- Provide a health check.
- Prevent an inactive model from being selected for new analysis.

### 13.2 Typed inference output

Define dataclasses:

```text
VehicleDetection
DamageDetection
InferenceRequest
InferenceResult
ModelMetadata
```

Each damage output contains:

- Class
- Confidence
- Bounding box
- Polygon
- Gate result
- Overlap ratio

### 13.3 Analysis transaction

Safe sequence:

1. Validate request.
2. Save source image to a temporary path.
3. Decode and normalize image.
4. Run models outside the database transaction.
5. Generate annotated image to temporary path.
6. Begin database transaction.
7. Create analysis.
8. Create vehicle detections.
9. Create damage detections.
10. Move images to permanent storage.
11. Commit.
12. If any step fails, roll back DB and remove temporary files.

### 13.4 Multiple-model support

Future models may include:

- Close-up vehicle/part classifier
- Vehicle-part detector
- Improved damage model
- Damage-severity classifier

Do not place model-specific code in UI pages.
Every model must implement an adapter interface.

### 13.5 Operator override

When vehicle confirmation fails:

- Show the raw damage predictions separately.
- Explain that they were withheld by the gate.
- Allow authorized operator override.
- Require a reason.
- Mark the analysis/report as manually confirmed.
- Audit operator, timestamp and reason.

---

## 14. Costing requirements

### 14.1 Damage-level cost

Each accepted/manual damage has:

- Estimated labour cost
- Estimated parts cost
- Other cost
- Computed line total

If the first release keeps one cost field, schema/service should still allow
future cost breakdown.

### 14.2 Analysis totals

```text
subtotal = sum(accepted damage line totals)
tax = subtotal × configured tax rate
gross = subtotal + tax
total = max(0, gross - discount)
```

Rules:

- Rejected damage cost is excluded.
- Decimal arithmetic only; do not use binary floating point.
- Currency has exactly two displayed decimal places unless configured otherwise.
- Every total recalculates server-side.
- Customers cannot modify costs.
- Finalized totals are stored in report snapshot.

---

## 15. Detailed PDF damage report

### 15.1 Page structure

Page 1:

- Company logo/name
- Report title
- Report number/revision
- Generated date
- Customer details
- Vehicle details
- Policy details
- Analysis status

Page 2 onward:

- Original vehicle image
- Annotated image
- Vehicle-confirmation result
- Damage summary table
- Detailed damage sections
- Cost breakdown
- Total
- Operator/finalizer
- Notes
- Disclaimer
- Signature fields

### 15.2 Damage table columns

- Item number
- Damage type
- Vehicle part
- Confidence
- Severity
- Description
- Estimated cost

### 15.3 Report rules

- Use finalized records only.
- Customer-visible content must exclude internal notes.
- Include model version/hash for audit.
- Include override disclosure when used.
- Store PDF hash.
- Keep revision history.
- Use consistent pagination.
- Repeat table headers across pages.
- Ensure images retain aspect ratio.
- Render and visually inspect sample reports before release.

---

## 16. Storage design

```text
storage/
├── company/logo/
├── customers/{customer_id}/
├── vehicles/{vehicle_id}/profile/
├── vehicles/{vehicle_id}/analyses/{analysis_id}/original/
├── vehicles/{vehicle_id}/analyses/{analysis_id}/annotated/
├── reports/{year}/{month}/
└── temp/
```

Rules:

- Store relative paths in MySQL.
- Generate UUID filenames.
- Deny executable extensions.
- Never serve arbitrary filesystem paths from user input.
- Remove abandoned temporary files.
- Back up database and storage together.
- Report deletion requires administrative retention policy, not ordinary CRUD.

---

## 17. Audit requirements

Audit:

- Login success/failure
- Logout
- Password change/reset
- Account creation/edit/activation
- Customer creation/edit/status change
- Vehicle creation/edit/status change
- Image upload/delete
- Analysis creation
- Model run
- Threshold changes
- Vehicle-confirmation override
- Damage acceptance/rejection/correction
- Manual damage
- Cost changes
- Analysis finalization
- Analysis revision
- Report generation/download by staff
- Company setting changes
- Plan/policy changes
- Model activation

Audit records are append-only through the application.

---

## 18. Security checklist

- Argon2id password hashing
- Parameterized queries through SQLAlchemy
- CSRF/session limitations documented for Streamlit
- HTTPS for network deployment
- Secure database user
- Secrets in `.env`
- File-type and size validation
- UUID filenames
- Role checks in service layer
- Customer ownership checks in every customer query
- Login rate limiting/lockout
- Session timeout
- No sensitive data in logs
- No stack traces shown to customers
- Backups encrypted where possible
- Database and storage access restricted to application/service accounts

If public internet exposure is required, conduct an additional security review
because Streamlit is best suited to controlled/internal application deployment.

---

## 19. Implementation phases

### Phase 0 — Baseline and source control

Tasks:

1. Create feature branch.
2. Record current package versions.
3. Verify model hashes.
4. Select fixed regression images.
5. Save expected predictions for those images.
6. Run current Streamlit tester.
7. Record screenshots and inference JSON.
8. Ensure datasets remain outside Git.

Validation gate:

- `verify_setup.py` passes.
- Model hashes match.
- Baseline predictions are recorded.
- Working tree contains no dataset.

### Phase 1 — Application scaffold and configuration

Tasks:

1. Create new directory structure.
2. Add `.env.example`.
3. Add configuration validation.
4. Add structured logging.
5. Add common exceptions.
6. Add global theme/layout.
7. Keep legacy tester available temporarily.

Validation gate:

- Application starts with valid config.
- Invalid config gives actionable errors.
- Secrets are not committed.
- Existing tester still runs.

### Phase 2 — Refactor ML pipeline

Tasks:

1. Move model loading to registry.
2. Move vehicle prediction to validator.
3. Move damage prediction to analyzer.
4. Move overlap logic to matching module.
5. Move annotation to annotator.
6. Add typed outputs.
7. Add regression tests.
8. Compare old/new outputs.

Validation gate:

- Same images produce equivalent classes/confidences/regions within tolerance.
- No UI dependency inside `ml/`.
- CPU inference succeeds.
- Missing/corrupt model errors are clear.

### Phase 3 — Database foundation

Tasks:

1. Create MySQL database/user.
2. Configure SQLAlchemy.
3. Configure connection pooling.
4. Create ORM models.
5. Create Alembic.
6. Generate initial migration.
7. Seed roles.
8. Seed company placeholder.
9. Add repository tests.

Validation gate:

- Migration upgrades empty database.
- Downgrade succeeds in test database.
- Unique/FK constraints behave correctly.
- Connection failure is handled.

### Phase 4 — Authentication and RBAC

Tasks:

1. Add password hashing.
2. Add initial-admin script.
3. Add login/logout.
4. Add session timeout.
5. Add lockout.
6. Add password change.
7. Add reset workflow.
8. Add permission decorators/helpers.
9. Add audit events.

Validation gate:

- Each role reaches only authorized pages.
- Direct URL navigation is blocked.
- Customer ownership enforcement passes.
- Plain passwords never reach DB/logs.

### Phase 5 — Company, users and plans

Tasks:

1. Company settings CRUD.
2. Logo upload.
3. User management.
4. Operator management.
5. Plan CRUD.
6. Policy assignment structures.
7. Audit logging.

Validation gate:

- Only admin edits company/plans/staff.
- Invalid logo rejected.
- Deactivated users cannot log in.
- Historical references remain intact.

### Phase 6 — Customers

Tasks:

1. Customer list/search/filter/pagination.
2. Create/edit customer.
3. Duplicate detection.
4. Customer account creation.
5. Temporary password flow.
6. Customer detail.
7. Customer summary export.

Validation gate:

- Duplicate constraints work.
- Operator can create customers.
- Customer can only view self.
- Temporary password forces change.

### Phase 7 — Vehicles and images

Tasks:

1. Vehicle list/search/filter.
2. Registration form.
3. Customer ownership link.
4. Policy assignment.
5. Image upload/storage.
6. Primary image.
7. Vehicle detail/history.
8. Image security tests.

Validation gate:

- Registration/chassis uniqueness works.
- Invalid image rejected.
- Paths remain inside storage root.
- Customer sees only owned vehicles.

### Phase 8 — Analysis workflow

Tasks:

1. New-analysis wizard.
2. Select/upload image.
3. Run vehicle and damage models.
4. Save raw output.
5. Render annotated image.
6. Review screen.
7. Accept/reject/correct.
8. Manual damage.
9. Override confirmation.
10. Severity/part/notes.
11. Draft saving.

Validation gate:

- Analysis matches standalone tester.
- Failed inference leaves no completed record.
- Override requires reason.
- Every change is audited.

### Phase 9 — Costing and finalization

Tasks:

1. Damage costs.
2. Totals.
3. Tax/discount.
4. Finalization checks.
5. Record locking.
6. Revision workflow.

Validation gate:

- Decimal totals are exact.
- Rejected damage excluded.
- Customer cannot alter cost.
- Finalized analysis cannot be edited directly.

### Phase 10 — PDF reports

Tasks:

1. Snapshot builder.
2. PDF template.
3. Image rendering.
4. Damage table.
5. Cost section.
6. Footer/disclaimer.
7. Revision numbering.
8. Download permissions.

Validation gate:

- PDF renders without clipped text/images.
- Snapshot matches finalized data.
- Customer accesses only own report.
- File hash stored and verified.

### Phase 11 — Customer mobile portal

Tasks:

1. Mobile navigation.
2. Customer dashboard.
3. Vehicle cards.
4. Vehicle detail.
5. Damage list.
6. Cost summary.
7. Report download.
8. Profile/password.
9. Responsive tests.

Validation gate:

- Tested at 320/375/768-pixel widths.
- No horizontal overflow.
- Touch targets meet minimum size.
- Ownership restrictions pass.

### Phase 12 — Dashboards and aggregate reports

Tasks:

1. KPI queries.
2. Trends.
3. Customer report.
4. Vehicle report.
5. Analysis register.
6. Damage summary.
7. Cost report.
8. Operator report.
9. CSV exports.

Validation gate:

- Totals reconcile with database.
- Filters apply consistently.
- Exports match displayed filters.
- Customer cannot access aggregate reports.

### Phase 13 — Hardening and deployment

Tasks:

1. Error pages.
2. Performance profiling.
3. Database indexes.
4. Backup scripts.
5. Restore test.
6. HTTPS/reverse proxy.
7. Windows service configuration.
8. Production `.env`.
9. Admin runbook.
10. User acceptance testing.

Validation gate:

- Full test suite passes.
- Backup restores to clean environment.
- Production uses non-root DB user.
- HTTPS enabled for network use.
- Models, storage and reports are backed up.

---

## 20. Testing strategy

### 20.1 Unit tests

- Password validation/hash
- Permission checks
- Customer code generation
- Vehicle code generation
- Analysis/report numbers
- Cost calculation
- Overlap calculation
- Storage path validation
- Report snapshot construction

### 20.2 Integration tests

- MySQL repositories
- Migration upgrade/downgrade
- Customer and vehicle transactions
- Analysis persistence
- Finalization and report creation
- Audit logging

### 20.3 Permission tests

For every service method test:

- Admin allowed/denied
- Operator allowed/denied
- Customer own resource allowed
- Customer other resource denied
- Anonymous denied
- Inactive user denied

### 20.4 ML regression tests

For fixed images record:

- Vehicle count
- Vehicle classes
- Damage count
- Damage classes
- Confidence tolerance
- Mask/box tolerance
- Annotated image dimensions

### 20.5 Report tests

- One damage
- Many damages across pages
- Long customer/vehicle fields
- Missing optional fields
- Large image
- Revision
- Currency/tax

### 20.6 Responsive tests

- 320×568
- 375×667
- 390×844
- 768×1024
- 1366×768
- 1920×1080

### 20.7 User acceptance scenarios

1. Admin creates operator.
2. Operator creates customer and login.
3. Customer changes temporary password.
4. Operator registers vehicle.
5. Operator uploads vehicle image.
6. Operator runs analysis.
7. Operator overrides close-up confirmation with reason.
8. Operator reviews three damages.
9. Operator rejects false positive.
10. Operator adds cost and finalizes.
11. Operator generates report.
12. Customer logs in on phone.
13. Customer sees vehicle, damages, total and PDF.
14. Customer cannot open another customer’s report.
15. Admin sees totals and audit entries.

---

## 21. Performance requirements

- Cache loaded ML models.
- Do not reload models on every Streamlit rerun.
- Use database indexes specified above.
- Paginate large tables.
- Resize display thumbnails while retaining originals.
- Limit upload size.
- Run inference once per explicit action.
- Prevent duplicate analysis submissions.
- Show progress during inference/report generation.
- Do not block all users with a long aggregate query.

---

## 22. Backup and recovery

Back up together:

- MySQL database
- `storage/`
- Model files
- `.env` through a secure secrets backup, not ordinary source control

Schedule:

- Daily database backup
- Daily incremental storage backup
- Weekly full backup
- Retention according to company policy

Recovery test:

1. Create empty recovery environment.
2. Restore MySQL dump.
3. Restore storage.
4. Restore models.
5. Configure `.env`.
6. Run migrations.
7. Run health checks.
8. Open historical report.
9. Verify image and PDF hashes.

---

## 23. Deployment runbook outline

1. Install Python.
2. Install MySQL and phpMyAdmin stack.
3. Create `Vehicle_Analyzis`.
4. Create limited application user.
5. Clone repository.
6. Create `.venv`.
7. Install pinned requirements.
8. Copy `.env.example` to `.env`.
9. Configure secure values.
10. Verify model hashes.
11. Run Alembic migration.
12. Create first administrator.
13. Run automated tests.
14. Start application on internal port.
15. Configure HTTPS reverse proxy.
16. Restrict firewall.
17. Configure Windows service.
18. Configure backup schedule.
19. Complete acceptance test.
20. Record deployed commit and migration version.

---

## 24. Final acceptance checklist

### Authentication

- [ ] Admin login works
- [ ] Operator login works
- [ ] Customer login works
- [ ] Logout works
- [ ] Password change works
- [ ] Forced password change works
- [ ] Lockout works
- [ ] Inactive user blocked

### Administration

- [ ] Company information editable by admin only
- [ ] Logo appears in application/report
- [ ] Users managed correctly
- [ ] Plans managed correctly
- [ ] Audit logs available

### Customers

- [ ] Customer registration works
- [ ] Customer login account created
- [ ] Duplicate prevention works
- [ ] Customer ownership permissions work

### Vehicles

- [ ] Vehicle registration works
- [ ] Vehicle image works
- [ ] Policy assignment works
- [ ] Vehicle belongs to correct customer

### Analysis

- [ ] Correct `best.pt` loaded
- [ ] Correct `yolov8n.pt` loaded
- [ ] Vehicle confirmation runs
- [ ] Damage segmentation runs
- [ ] Close-up override works
- [ ] Raw predictions stored
- [ ] Review/correction works
- [ ] Manual damage works
- [ ] Annotated image stored

### Costing

- [ ] Individual cost stored
- [ ] Totals calculate correctly
- [ ] Tax/discount calculate correctly
- [ ] Customer sees final total only

### Reports

- [ ] PDF contains company
- [ ] PDF contains customer
- [ ] PDF contains vehicle
- [ ] PDF contains images
- [ ] PDF contains damage details
- [ ] PDF contains costs
- [ ] PDF downloads
- [ ] Revision works

### Customer mobile portal

- [ ] Mobile login usable
- [ ] Vehicle image visible
- [ ] Damage list visible
- [ ] Total visible
- [ ] Report downloadable
- [ ] Password change usable
- [ ] No horizontal overflow

### Professional UI and image policy

- [ ] Visual quality is equal to or better than the current dashboard
- [ ] All pages use the shared spacing, typography and component system
- [ ] Desktop navigation and layouts remain consistent
- [ ] Customer screens are designed directly for mobile
- [ ] Loading, empty, success and error states are complete
- [ ] Keyboard focus is visible
- [ ] No stock photographs are used
- [ ] No AI-generated illustrations are used
- [ ] No decorative hero/background images are used
- [ ] Every displayed image is a company logo or case-specific vehicle evidence
- [ ] Missing vehicle images use a neutral empty state
- [ ] PDF reports contain only company and case-specific images

### Security and operations

- [ ] Passwords hashed
- [ ] Secrets excluded from Git
- [ ] Non-root MySQL user used
- [ ] Permission tests pass
- [ ] Upload validation passes
- [ ] Backup succeeds
- [ ] Restore succeeds
- [ ] HTTPS enabled for network access

---

## 25. Decisions to confirm before implementation

These do not block the architecture, but must be confirmed before their phase:

1. Official company name and logo
2. Company registration/contact details
3. Default currency
4. Tax label and tax rate
5. Required customer identity fields
6. Required vehicle fields
7. Insurance-plan definitions
8. Whether customers may edit contact details
9. Whether operators may finalize or admin approval is required
10. Cost breakdown: single amount or labour/parts/other
11. Report disclaimer text
12. Report signature requirements
13. Image/report retention period
14. Maximum upload size
15. Internal-only or internet-accessible deployment
16. Backup location and retention

Until confirmed, implementation must use configurable placeholders rather than
hard-coded business values.

---

## 26. Recommended implementation order summary

```text
Baseline
  → Refactor ML
  → Database
  → Authentication/RBAC
  → Company/Users/Plans
  → Customers
  → Vehicles/Images
  → Analysis/Review
  → Costing/Finalization
  → PDF Reports
  → Customer Mobile Portal
  → Admin Reporting
  → Security/Deployment
```

The first coding task must be the inference regression harness. The ERP should
not be built around the model until the refactored pipeline proves that it
produces the same output as the existing dashboard.
