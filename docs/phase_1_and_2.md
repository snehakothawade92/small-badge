# SmallBadge: Digital Badge Issuing & Verification Platform
## Phase 1 & Phase 2: Requirement Analysis and System Design

---

## 1. Requirement Analysis (Phase 1)

### 1.1 Problem Statement
In traditional academic and professional environments, credentials (certificates, badges, accomplishments) are issued on paper or as simple PDF files. This approach introduces major challenges:
* **High Risk of Forgery**: Digital PDFs can be easily edited using basic image editors.
* **Complex Verification**: Employers wishing to verify credentials must manually contact the issuing institution via email/phone, causing delays.
* **Loss/Damage**: Paper certificates are subject to physical degradation or loss.
* **Lack of Shareability**: Traditional certificates are difficult to display dynamically on social profiles (like LinkedIn, personal portfolios).

### 1.2 Existing vs. Proposed System

| Feature | Existing System (Paper/PDF) | Proposed System (SmallBadge) |
| :--- | :--- | :--- |
| **Medium** | Physical paper or flat static PDF | Secure web platform with cloud storage |
| **Verification** | Manual (emails, calls, transcripts verification) | Real-time (Badge ID lookup, QR Code scan) |
| **Security** | Low (easily forged, edited, or replicated) | High (uniquely cryptographically hashed Badge IDs) |
| **Shareability** | Limited (must be scanned or emailed) | Immediate (direct link sharing, LinkedIn display) |
| **Scalability** | Slow (manual printing, signing, posting) | Instant (CSV import, batch issuing to thousands of users) |

### 1.3 Project Objectives
* **Security & Authenticity**: Every badge is mapped to a unique hash (Badge ID).
* **Speed**: Instantaneous verification through QR code scanning and direct ID lookup.
* **Role-Based Workspaces**: Custom workflows for Super Admin, Organization Admin, and Students.
* **Dynamic PDF Render**: Autogenerate highly detailed PDFs with verified metadata.

### 1.4 System Scope
SmallBadge is designed for:
* Universities & Colleges issuing extra-curricular or academic course badges.
* Tech Bootcamps & Training Institutes issuing certificates for quick courses.
* Corporate HR teams highlighting employee milestones.

### 1.5 Functional Requirements

#### 1. Super Admin
* Approve/Reject organization registration requests.
* Monitor global analytics (total orgs, badges issued, active users).
* Manage system-wide users and revoke compromised accounts.

#### 2. Organization Admin (Colleges/Institutes)
* Configure organization profile (logo, name, website).
* Add courses and upload student records via CSV.
* Manage badge templates (upload background structures, design placeholders).
* Issue badges to students (single or batch).
* Revoke badges if issued erroneously.

#### 3. Student
* Log in to a personalized dashboard.
* View all issued badges in a portfolio view.
* Download badge certificates as PDFs or image files.
* Direct share links to external social networks.

#### 4. Public User (Employer/Verifiers)
* View verification portal.
* Search badge validity using a Badge ID.
* Scan a badge's QR code to be routed instantly to its verification page.

### 1.6 Non-Functional Requirements
* **Security**: Hashed passwords using bcrypt, robust Role-Based Access Control (RBAC) to block unauthorized routes.
* **Usability**: Clean, mobile-friendly Bootstrap 5 UI/UX interface.
* **Performance**: Under 1-second badge rendering and page loads.
* **Scalability**: MongoDB document design allows millions of records without structural overhead.

---

## 2. System Design (Phase 2)

### 2.1 System Architecture
The application follows a standard **Three-Tier Architecture**:

1. **Presentation Layer (Frontend)**:
   * HTML5, CSS3 (Vanilla CSS + Bootstrap 5), and JavaScript.
   * Renders dashboards dynamically depending on the authenticated user's session role.
2. **Application Logic Layer (Backend)**:
   * Python & Flask.
   * Modularized using Flask **Blueprints** to isolate logical subsystems (Authentication, Org Administration, Student Portfolio, Public Portal).
   * Middleware/Decorators for Role-Based Access Control.
3. **Database & Services Layer**:
   * MongoDB for document-based data management.
   * `Pillow` and `ReportLab` for image manipulation and PDF generation.
   * `qrcode` for generating unique verification vectors.

### 2.2 System Workflow Diagram

```
[ Public User / Employer ] ──(Scan QR Code or Enter ID)──┐
                                                        │
[ Org Admin ] ──(Import CSV / Issue Badge)──> [ Database ] <──(View Dashboard)── [ Student ]
                                                     ▲
                                                     │ (Approve Registration)
                                                     │
                                            [ Super Admin ]
```

### 2.3 Proposed Directory Structure
The structure ensures clean separation of concerns and scales as we add features:

```
smallbadge/
│
├── run.py                 # Application entry point
├── config.py              # Environment configuration loader
├── requirements.txt       # Python packages list
├── .env                   # Local settings (DB URI, secret keys)
│
├── docs/                  # Project documentation for MCA Viva
│   └── phase_1_and_2.md
│
└── app/                   # Core Package
    ├── __init__.py        # Factory loader & DB initialization
    ├── db.py              # MongoDB Connection Helper
    ├── decorators.py      # Role-Based Access Control (RBAC) decorators
    │
    ├── routes/            # Blueprints
    │   ├── auth.py        # Authentication & Registration
    │   ├── admin.py       # Super Admin Dashboard & Approvals
    │   ├── org.py         # Courses, Templates, Students, Badge Issuance
    │   ├── student.py     # Student Portfolio, download, share
    │   └── public.py      # Badge verification
    │
    ├── static/            # Static assets
    │   ├── css/
    │   │   └── style.css  # Custom CSS aesthetics
    │   ├── js/
    │   └── uploads/       # QR codes, templates, generated badges
    │
    └── templates/         # HTML Templates
        ├── base.html      # Main Base Template (Layout)
        ├── auth/
        ├── admin/
        ├── org/
        ├── student/
        └── public/
```
