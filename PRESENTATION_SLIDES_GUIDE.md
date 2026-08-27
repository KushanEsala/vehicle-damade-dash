# 🎙️ 5-MINUTE PRESENTATION SLIDES & SPEAKER SCRIPT

**Project Title:** Web Based Information System for Vehicle Damage Assessment and Insurance ERP  
**Subtitle:** A Role-Based Automotive Claims Assessment and Enterprise Resource Planning Platform  
**Candidate:** P.A.B. Silva (Reg No: IT2026/ERP/042)  
**Department:** Department of Information Technology, Sri Lanka International Buddhist Academy (SIBA Campus)  
**Supervisor:** Dr. ABC PQR  
**Total Allocated Time:** 5 Minutes (approx. 45–50 seconds per slide)

---

## ⏱️ PRESENTATION TIMING BREAKDOWN

| Slide # | Slide Section | Recommended Time | Focus Area |
| :---: | :--- | :---: | :--- |
| **Slide 1** | Title & Introduction | 0:20 | Title, Candidate Details, Institution |
| **Slide 2** | 1.1 Project Introduction & Problem Definition | 0:50 | Background, Domain Bottlenecks, Problem Statement |
| **Slide 3** | 1.2 Project Objectives & Goals | 0:50 | Primary & Secondary Goals, Solution Alignment, Expected Outcomes |
| **Slide 4** | 1.3 Methodology & System Approach | 0:50 | Agile Methodology, Tech Stack, 3-Tier Architecture |
| **Slide 5** | 1.4 Key Achievements & Innovative Features | 0:50 | AI Dual-Gating, Automated Costing/PDF, Migration Improvements |
| **Slide 6** | 1.5 Technical Challenges & Solutions | 0:50 | GPU Transfer Resume, Spatial Gating, Security Cookies |
| **Slide 7** | 1.6 Limitations & Future Improvements | 0:40 | Current Scope Boundaries, Phase 2 Roadmap, Conclusion |

---

# 📑 SLIDE-BY-SLIDE CONTENT & SPEAKER SCRIPTS

---

## SLIDE 1: Title Slide

### Slide Content:
- **Title:** WEB BASED INFORMATION SYSTEM FOR VEHICLE DAMAGE ASSESSMENT AND INSURANCE ERP
- **Subtitle:** A Role-Based Automotive Claims Assessment & Enterprise Resource Planning Platform
- **Presenter:** P.A.B. SILVA (Reg No: IT2026/ERP/042)
- **Department:** Department of Information Technology
- **Institution:** Sri Lanka International Buddhist Academy (SIBA Campus), Pallekele
- **Supervisor:** Dr. ABC PQR
- **Year:** 2026

### 💬 Speaker Script (0:00 - 0:20):
> *"Good morning respected supervisor and members of the panel. I am P.A.B. Silva, and today I am pleased to present my undergraduate final project titled **'Web Based Information System for Vehicle Damage Assessment and Insurance ERP'** — a role-based automotive claims assessment and enterprise resource planning platform developed under the supervision of Dr. ABC PQR."*

---

## SLIDE 2: 1.1 Project Introduction

### Slide Content:
- **Background & Domain:**
  - Motor insurance claims rely heavily on manual field inspections by claims assessors.
  - Manual damage recording, body panel mapping, and cost estimation transcribed into legacy databases.
- **Motivation:**
  - Extended processing delays (2 to 5 business days per claim settlement cycle).
  - High operational overheads and paper-based workflow bottlenecks.
  - Subjective variance between assessors leading to inconsistent financial repair estimates.
  - Vulnerability to fraudulent claim submissions.
- **Problem Statement:**
  - Existing insurance management portals lack real-time visual AI integration.
  - No automated validation to verify whether uploaded inspection photographs contain legitimate vehicles or off-target background objects.
  - Fragmented role workflows for System Administrators, Claims Assessors, and Policyholders.

### 💬 Speaker Script (0:20 - 1:10):
> *"To begin with the project introduction: in the motor insurance industry, traditional claim processing relies on manual field inspections. Assessors evaluate vehicle damage, record affected panels, estimate repair costs, and manually transcribe findings into legacy ERP databases. This manual workflow creates severe operational bottlenecks, taking anywhere from 2 to 5 business days per claim. It is also subject to human error, subjective costing variations between assessors, and potential fraud. Existing claim portals lack real-time visual AI integration and cannot automatically verify whether uploaded photos actually contain a vehicle. Our project addresses this problem by integrating deep learning instance segmentation directly into a role-based enterprise ERP framework."*

---

## SLIDE 3: 1.2 Project Objectives and Goals

### Slide Content:
- **Primary Objective:**
  - Design, implement, and evaluate a role-based web ERP platform integrating deep learning visual instance segmentation for automated vehicle damage assessment, interactive review, financial costing, and claim report generation.
- **Secondary Objectives & Goals:**
  1. Fine-tune a 7-class YOLOv8 nano instance segmentation model (`scratch`, `dent`, `tear`, `missing_part`, `broken_lamp`, `puncture`, `broken_glass`).
  2. Implement a dual-model spatial validation gate using a general COCO vehicle detector (`yolov8n.pt`) with $\ge 20\%$ IoU overlap rules and manual operator close-up override.
  3. Integrate Google Generative AI Gemini Vision to describe vehicle damage.
  4. Develop a responsive Next.js 14 frontend and FastAPI Python backend backed by a 15-table MySQL database (`Vehicle_Analyzis`).
  5. Establish strict Role-Based Access Control (Admin, Claims Operator, Policyholder) with automated PDF claim report generation, 15% VAT & deductible calculation, and security audit logging.
- **Expected Outcomes:**
  - Real-time inspection response (< 2 seconds), 78% reduction in background false positives, standardized line-item repair costing, and transparent self-service customer claim tracking.

### 💬 Speaker Script (1:10 - 2:00):
> *"Our primary objective was to build a full enterprise ERP system powered by deep learning visual assessment. Specific technical goals included: fine-tuning a YOLOv8 nano instance segmentation model across 7 damage classes; engineering a dual-model validation gate using a COCO vehicle detector to reject off-target background predictions; incorporating Gemini Vision to describe damage; building a Next.js 14 frontend and FastAPI backend with a 15-table MySQL database; and establishing role-based access for Administrators, Claims Operators, and Customers. This system directly solves the problem by providing real-time AI visual overlays, standardizing line-item repair costs with automatic 15% VAT and deductible calculations, and generating official PDF claim reports instantly."*

---

## SLIDE 4: 1.3 Methodology and Approach

### Slide Content:
- **Development Methodology:**
  - Agile Iterative Software Development Lifecycle across 5 phases (Requirements Analysis, Dataset Curation & Model Training, Schema & REST API Engineering, Next.js Portal Development, Security & Audit Verification).
- **Technology Stack & Frameworks:**
  - **Frontend:** Next.js 14.2 App Router, React, TypeScript, Tailwind CSS (Dark Automotive Inspection Visual Identity).
  - **Backend Service:** FastAPI (Python 3.11), SQLAlchemy ORM, Uvicorn Server (Port 8000).
  - **AI / Computer Vision:** PyTorch 2.2, Ultralytics YOLOv8 nano instance segmentation, OpenCV, COCO vehicle gate.
  - **Data Tier:** MySQL 8.0 / MariaDB (`Vehicle_Analyzis` database, 15 relational tables).
  - **Vision Description Service:** Google Generative AI Gemini 1.5 Flash Vision SDK.
- **System Architecture:**
  - Decoupled 3-Tier Architecture: Presentation Layer (Next.js Port 3000) $\leftrightarrow$ Application API Layer (FastAPI Port 8000) $\leftrightarrow$ Data & AI Layer (PyTorch CUDA GPU / MySQL Port 3306).

### 💬 Speaker Script (2:00 - 2:50):
> *"Moving to our methodology and approach: we adopted an Agile iterative engineering workflow. Our technology stack combines Next.js 14 and TypeScript for a high-performance dark automotive dashboard UI, FastAPI and Python 3.11 for high-speed RESTful backend microservices, and a 15-table MySQL database managed via SQLAlchemy ORM. The computer vision pipeline utilizes PyTorch and Ultralytics YOLOv8 nano for instance segmentation, paired with Google Gemini Vision to describe damage. The system follows a decoupled 3-tier client-server architecture where model inference remains isolated on the Python backend, ensuring the browser never downloads raw model weights."*

---

## SLIDE 5: 1.4 Key Achievements

### Slide Content:
- **Major Implemented Functionalities:**
  - **Dual-Model Visual Inspection Pipeline:** Real-time damage mask overlay bounded by vehicle detection spatial gating (< 2 sec processing time).
  - **Interactive Operator Review Workspace:** Allows claims assessors to review AI predictions, edit severity levels, adjust line-item pricing, auto-calculate 15% VAT, and subtract policy deductibles.
  - **Automated Official PDF Claim Generation:** Generates downloadable, tamper-proof PDF claim reports complete with vehicle metadata, visual inspection image overlay, financial breakdown, and company branding.
  - **Role-Based Portals:** Admin system management, Operator inspection workspace, and Customer vehicle tracking portal.
- **Innovative Features & Contributions:**
  - Dual-model spatial gating ($\ge 20\%$ IoU) suppressing 78% of off-target background false positives.
  - Gemini Vision integration to describe damage.
  - Opaque `HttpOnly`, `Secure`, `SameSite=Lax` session token cookies protecting against XSS/CSRF token theft.
- **Improvements Beyond Initial Proposal:**
  - Upgraded architecture from Streamlit to Next.js 14 + FastAPI to eliminate widget rerun artifacts and state loss.
  - Integrated Windows Credential Manager (`configure_vision.ps1`) to securely store API keys outside code and git repositories.

### 💬 Speaker Script (2:50 - 3:40):
> *"Our key achievements include: successfully building an end-to-end visual inspection pipeline that delivers pixel-level damage masks in under 2 seconds; an interactive operator review workspace with automated 15% VAT and policy deductible calculations; automated one-click PDF claim report generation; and secure multi-role portals for Admins, Operators, and Customers. Key innovations include our dual-model spatial gating rule which suppressed 78% of background false positives, Gemini Vision integration to describe damage, and enterprise cookie security. Furthermore, we exceeded our original proposal by migrating from Streamlit to Next.js 14 and FastAPI to achieve a production-grade enterprise application."*

---

## SLIDE 6: 1.5 Challenges Encountered and Solutions Implemented

### Slide Content:
- **Challenge 1: CPU Model Training Bottlenecks**
  - *Problem:* Initial training on CPU required ~24 hours for 15 epochs.
  - *Solution:* Transferred checkpoint (`last.pt`) to NVIDIA RTX GPU with CUDA 12.8 PyTorch wheel, regenerated paths via `prepare_dataset.py`, resuming training at Epoch 16 to finish 50 epochs in 45 minutes.
- **Challenge 2: False Positive Damage Predictions on Non-Vehicle Backgrounds**
  - *Problem:* Standalone damage segmenter flagged background clutter (walls, fences) as vehicle damage.
  - *Solution:* Engineered spatial overlap gating requiring $\ge 20\%$ IoU overlap with COCO vehicle bounding box.
- **Challenge 3: Tight Body Panel Close-Up Photographs**
  - *Problem:* COCO vehicle detector failed on tight close-up photographs of doors or lamps where full vehicle shape was missing.
  - *Solution:* Added manual "Require vehicle confirmation" toggle in operator UI to allow manual gating override for close-ups.
- **Challenge 4: Browser Session Security & Token Leakage**
  - *Problem:* Storing JWTs in browser LocalStorage exposed tokens to XSS script theft.
  - *Solution:* Implemented server-side token hashes in MySQL and `HttpOnly`, `Secure`, `SameSite=Lax` session cookies.

### 💬 Speaker Script (3:40 - 4:30):
> *"During development, we encountered and resolved four major technical challenges: First, CPU training latency was too high. We solved this by creating a GPU resume workflow, transferring our Epoch 15 checkpoint to an NVIDIA RTX GPU with CUDA 12.8, completing all 50 epochs in just 45 minutes. Second, background clutter produced false damage detections. We solved this by developing a 20% IoU spatial gating rule against COCO vehicle boxes. Third, COCO detectors missed tight panel close-ups. We added an operator UI toggle to safely override vehicle confirmation for close-up shots. Fourth, browser LocalStorage posed XSS security risks. We replaced LocalStorage tokens with server-side token hashing and HttpOnly secure cookies."*

---

## SLIDE 7: 1.6 Limitations and Future Improvements

### Slide Content:
- **Current System Limitations:**
  - Bounded to 2D visual surface inspection photos; internal mechanical, engine, or structural chassis defects are not detected.
  - Fine-tuned on 7 damage classes without dedicated negative background training images or an 18-part vehicle panel validator.
  - Mask recall stands at 40.57% (mAP50 = 41.20%), requiring mandatory human assessor review before report finalization.
- **Directions for Future Work & Phase 2 Training Roadmap:**
  1. **Dataset Augmentation:** Incorporate explicit negative/background images with empty label files to further reduce false positives.
  2. **Dedicated Panel Segmentation Model:** Train an 18-part vehicle body panel segmentation model (bumper, fender, bonnet, door, lamp) for exact panel localization.
  3. **Untouched Held-Out Test Set Audit:** Conduct benchmark evaluation comparing baseline (`best.pt`) against Phase 2 models on an independent test dataset.
  4. **Mobile App Integration:** Extend web application to native iOS/Android inspection apps supporting live video damage detection stream.
- **Conclusion:**
  - Successfully demonstrated that integrating deep learning visual segmentation with an ERP framework standardizes repair estimates, eliminates paper bottlenecks, and modernizes motor insurance claim management.

### 💬 Speaker Script (4:30 - 5:00):
> *"To conclude with limitations and future work: our current system is designed for 2D surface damage, meaning internal mechanical or engine defects are outside scope. Because mask recall is 40.57% with mAP50 of 41.20%, human operator review remains mandatory before report finalization. For Phase 2 future work, we plan to add negative background dataset images, train an 18-part vehicle body panel segmentation model, conduct an independent held-out test set audit, and develop native mobile inspection apps. In conclusion, our project successfully proves that combining deep learning vision with a role-based ERP framework standardizes repair costing and modernizes insurance claim assessment. Thank you for your time, and I welcome any questions."*

---

# 📊 SUMMARY OF KEY PROJECT FACTS FOR Q&A

| Fact Category | Exact Project Value / Metric |
| :--- | :--- |
| **Primary AI Model** | YOLOv8 nano instance segmentation (`best.pt`, SHA-256: `C9D86E...`) |
| **Damage Categories (7)** | `scratch`, `dent`, `tear`, `missing_part`, `broken_lamp`, `puncture`, `broken_glass` |
| **Vehicle Gate Model** | COCO Pretrained YOLOv8 nano (`yolov8n.pt`, SHA-256: `F59B3D...`) |
| **Dataset Size** | 13,945 total images (11,621 train [83.33%], 2,324 val [16.67%]) |
| **Training Execution** | 50 Epochs total (Epochs 1–15 CPU ~24h 9m, Epochs 16–50 RTX GPU CUDA 12 ~45m 32s) |
| **Validation Metrics (Epoch 44)** | Box mAP50 = 44.80%, Mask mAP50 = 41.20%, Box Precision = 55.91%, Mask Precision = 53.78% |
| **Optimal F1 Score** | 0.48 at confidence 0.267 (box) / 0.46 at confidence 0.278 (mask) |
| **Web Tech Stack** | Next.js 14.2 App Router, TypeScript, Tailwind CSS, FastAPI 0.110, Python 3.11 |
| **Database Schema** | MySQL 8.0 `Vehicle_Analyzis` (15 relational tables) |
| **Vision Description Service** | Google Generative AI Gemini 1.5 Flash Vision API |
| **Security Standards** | Argon2id password hashing, `HttpOnly`, `Secure`, `SameSite=Lax` session cookies |
| **Financial Formulas** | $\text{Subtotal} = \sum \text{Damage Costs}$; $\text{VAT} = 15\%$; $\text{Final Claim} = (\text{Subtotal} + \text{VAT}) - \text{Deductible}$ |
