# SmallBadge: Digital Badge Issuing & Verification Platform
## Phase 4: UI/UX Layout & Design Plan

---

## 1. Core Visual Design System (Design Tokens)
To make **SmallBadge** feel like a modern, premium enterprise web application (and impress examiners at your project viva), we will establish a dedicated styling guide inside our master `style.css` stylesheet.

### 1.1 Color Palette
We will avoid browser-default colors and use custom HSL CSS variables representing a professional corporate identity:
* **Primary (Deep Slate Blue)**: `hsl(215, 25%, 27%)` - Promotes security, authority, and professionalism.
* **Secondary (Muted Blue-Gray)**: `hsl(210, 16%, 93%)` - Clean background highlights.
* **Accent (Premium Golden Yellow)**: `hsl(38, 92%, 50%)` - Evokes badges, excellence, and achievement.
* **Success Green**: `hsl(142, 72%, 29%)` - Used for validated statuses.
* **Danger Red**: `hsl(0, 72%, 51%)` - Used for revoked status or delete actions.

### 1.2 Typography
* **Primary Font**: `Outfit` or `Inter` (embedded via Google Fonts).
* **Hierarchy**:
  * Titles: Bold, spacious tracking (`letter-spacing: -0.02em`).
  * Body: Regular Weight, highly readable (`line-height: 1.6`).

---

## 2. Key Screen Outlines & User Flows

### 2.1 Landing Page & Verification Portal (Public)
* **Purpose**: Allows anyone (employers, public) to check the validity of a badge.
* **Visual Structure**:
  * Centered minimalist search card with a glowing gold border.
  * Inputs: Large search field for Badge ID.
  * Secondary CTA: "Scan QR Code" which prompts webcam validation (advanced) or explains the QR flow.
  * Direct redirects: Navigating to `/verify/<badge_id>` renders the badge details directly.

### 2.2 Shared Login & Registration Portal
* **Purpose**: Secure entry point for Super Admins, Org Admins, and Students.
* **Visual Structure**:
  * Dual-card layout: Left side contains illustrative branding/promotional text; right side contains the form.
  * Select role input dropdown to guide login queries.
  * Organization Registration: An Org Admin can request registration by filling in corporate information. A pending message will show until approved by the Super Admin.

### 2.3 Super Admin Dashboard
* **Purpose**: System-wide governance and analytics.
* **Layout**:
  * Sidebar: Dashboard, Organization Approval Queue, User Management, Logs.
  * Main Content:
    * Four metrics cards: Active Organizations, Total Badges Issued, Pending Approval Requests, Audit Logs count.
    * Approval Queue Table: Displays Organization requests with inline action buttons (**Approve** with confirmation, **Reject** with reason modal).

### 2.4 Organization Admin Dashboard
* **Purpose**: Standard operational dashboard for colleges/institutes.
* **Layout**:
  * Sidebar: Overview, Courses, Students, Templates, Issue Badge, View Reports.
  * Main Content:
    * Metric panels: Courses Active, Students Enrolled, Badges Issued.
    * **CSV Upload Module**: Drag-and-drop file uploader area with styling to batch import students.
    * **Template Designer Page**: Input form to register background colors, text layouts, and upload badge badge icons.

### 2.5 Student Portfolio Dashboard
* **Purpose**: Students manage and share accomplishments.
* **Layout**:
  * Hero Section: Student profile details (avatar, name, email, institution name).
  * Badge Grid: A layout showing badge thumbnails with details (course, date).
  * **Interactive Badge Detail Modal**: Clicking a badge brings up:
    * Fully rendered badge certificate.
    * Download options (PDF, Image).
    * Social sharing handles (LinkedIn Add-to-Profile link generator).

---

## 3. Dynamic Page Verification Screen Layout
The public verification output page (`/verify/<badge_id>`) is the single most critical asset in the application:

```
┌──────────────────────────────────────────────────────────┐
│                   SMALLBADGE VERIFICATION                │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  [ ✅ VERIFIED DIGITAL CREDENTIAL ]                      │
│  This badge is authentic and issued by the institution.  │
│                                                          │
│  ┌────────────────────────────────────────────────────┐  │
│  │                                                    │  │
│  │                   GOLDEN BADGE                     │  │
│  │                                                    │  │
│  │              Awarded to: Rahul Sharma              │  │
│  │           For: Web Application Development         │  │
│  │                                                    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  Student: Rahul Sharma       Course: MCA-202             │
│  Issued: 2026-07-18          Id: b3d5e8f8...             │
│                                                          │
│  ┌───────────────┐           ┌────────────────────────┐  │
│  │  QR Code      │           │ Issuer Details:        │  │
│  │  [  Scan  ]   │           │ NIT Delhi (Approved)   │  │
│  └───────────────┘           └────────────────────────┘  │
│                                                          │
│  [ Download PDF Certificate ]    [ Add to LinkedIn ]     │
└──────────────────────────────────────────────────────────┘
```
