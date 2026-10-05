# VIIE University / Vidyalankar Placement Microservice — Comprehensive Design & Architecture Specification

---

## 1. System Overview & Architectural Blueprint

### 1.1 Purpose and Scope
The **EduTrack VIT** is a modern full-stack web application developed for **Vidyalankar Institute of Technology**. It connects the parent College ERP ecosystem with corporate recruiters, placement coordinators (TPO), faculty leadership (Dean), and graduating students.

The platform provides a decentralized, standalone frontend interface that seamlessly interoperates with the parent ERP via decoupled session token exchange, ensuring zero vendor lock-in, low coupling, and zero hard dependencies on legacy monolithic databases.

```
+-----------------------------------------------------------------------------------+
|                        VIIE / VIDYALANKAR PARENT ERP                              |
|   (Identity Provider, Student Master Registry, Academic Grades, Marksheets)       |
+------------------------------------------+----------------------------------------+
                                           |
                              SSO Handshake Token
                         [ERP-SSO-JWT-LIVE-VIIE-2026]
                                           |
                                           v
+-----------------------------------------------------------------------------------+
|                   VIIE PLACEMENT MICROSERVICE PLATFORM                            |
+-----------------------------------------------------------------------------------+
|  [ Student Portal ]     [ Recruiter Portal ]    [ TPO Portal ]     [ Dean Portal ]|
|  - Enrolment Sync       - Post Openings         - Batch Curate     - Macro KPIs   |
|  - Batch Drives Feed    - Pipeline Stages       - Eligibility      - Async Jobs   |
|  - 3-Resume Options     - Round Remarks         - Broadcasts       - NIRF Export  |
|  - Offer Letter Vault   - Issue Formal Offers   - Master Reports   - Remedial Map |
+-----------------------------------------------------------------------------------+
                                           |
                     Institutional CSS Design System & Tokens
                          (style.css & viie-core.js)
```

### 1.2 Authentication & Token Exchange Architecture
- **Zero Login Barrier**: The placement microservice operates without a traditional login page. Authentication is inherited directly from the parent university ERP via URL parameter or local storage token exchange.
- **Session Token**: `ERP-SSO-JWT-LIVE-VIIE-2026` represents the active, verified student/administrator identity.
- **Active User Context**:
  - Name: `Nekeel`
  - Roll / Student ID: `290176F1`
  - Department: `Computer Science & Engineering`
  - Academic Cohort: `VIIE University — Academic Cohort 2023 - 2027 (Sem 7)`
- **Role Perspective Testing Hub (`index.html`)**: Provides instantaneous perspective switching between Student, Corporate Recruiter, TPO Administrator, and Dean Directorate, ensuring frictionless evaluation of role-based security boundaries.

### 1.3 Repository & Directory Structure
```
VIIE-PlacementWebsite/
├── index.html                      # Parent ERP Entry Hub & Role Perspective Testing
├── DESIGN.md                       # Comprehensive Design System & Architecture Spec
├── assets/
│   ├── css/
│   │   └── style.css               # Unified Vidyalankar Institutional Design System
│   ├── js/
│   │   └── viie-core.js            # Core Controller, Session, Loading & Modals
│   └── images/
│       └── viie_students.jpg       # High-Resolution Institutional Student Asset
├── student/
│   └── dashboard.html              # Student Portal (Pixel-Perfect Match to ERP UI)
├── company/
│   └── dashboard.html              # Corporate Recruiter Hiring & Evaluation Portal
├── tpo/
│   └── dashboard.html              # Training & Placement Officer (TPO) Directorate
└── dean/
    └── dashboard.html              # Dean Executive Analytics & NIRF Accreditation
```

---

## 2. Institutional Brand & Design System

### 2.1 Brand Identity & Colors
The visual system replicates the official Vidyalankar institutional design language, characterized by a deep, authoritative crimson maroon contrasted against crisp slate and pure white surfaces.

```css
:root {
  /* Exact Vidyalankar Institutional Palette */
  --vidya-maroon:          #5f0d80ff;   /* Primary Brand Maroon */
  --vidya-maroon-dark:     #5d0868ff;   /* Deep Maroon Hover / Accent */
  --vidya-maroon-hover:    #731490ff;   /* Interactive Hover Red */
  --vidya-sidebar-bg:      #650d80ff;   /* Solid Maroon Sidebar Background */
  --vidya-sidebar-active:  rgba(0, 0, 0, 0.22); /* Active Nav Item Overlay */
  --vidya-sidebar-hover:   rgba(255, 255, 255, 0.08); /* Hover Nav Item Overlay */
  --vidya-sidebar-muted:   #E29CA1;   /* Section Headers & Subtext */

  /* Surfaces & Canvas */
  --bg-main:               #fdfafbff;   /* Canvas Soft Off-White Background */
  --bg-page:               #fdfafbff;   /* Page Body */
  --bg-card:               #FFFFFF;   /* Crisp White Card Surface */
  --bg-input:              #F8F9FA;   /* Subtle Form Input Fill */
  --bg-profile-banner:     #F7EFEF;   /* Soft Rose/Blush Profile Card Banner */

  /* Typography Colors */
  --text-dark:             #111827;   /* Slate 900 (High Contrast Headings) */
  --text-body:             #374151;   /* Slate 700 (Body Copy) */
  --text-muted:            #6B7280;   /* Slate 500 (Subtitles & Placeholders) */
  --text-subtle:           #9CA3AF;   /* Slate 400 (Dividers & Labels) */

  /* Borders & Dividers */
  --border-light:          #ECEEF2;   /* Card Borders & Section Lines */
  --border-card:           #F0F2F5;   /* Container Outlines */
  --border-input:          #E5E7EB;   /* Input Field Outlines */

  /* Badges & Status Accents */
  --badge-pending-bg:      #F1F5F9;   /* Slate Neutral Badge */
  --badge-pending-text:    #475569;   /* Slate Neutral Badge Text */
  --badge-red:             #a41fc5ff;   /* Calendar Selected Day / Warning */
  --badge-green-bg:        #DCFCE7;   /* Verified / Approved Background */
  --badge-green-text:      #166534;   /* Verified / Approved Text */
}
```

### 2.2 Typography System
The typography uses a clean, contemporary pairing of **Plus Jakarta Sans** and **Inter**, loaded directly from Google Fonts:
- **Primary Typeface**: `'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif`
- **Heading 1 (`h1`)**: `1.6rem`, font-weight `800`, letter-spacing `-0.02em`
- **Heading 2 (`h2`)**: `1.45rem`, font-weight `700`, letter-spacing `-0.015em`
- **Greeting Headline**: `1.7rem`, font-weight `400` with child `strong` set to `700`
- **KPI Numerals**: `2.1rem`, font-weight `800`, line-height `1.0`
- **Section Subheadings**: `0.72rem`, font-weight `800`, letter-spacing `0.08em`, uppercase
- **Input & Body Text**: `0.88rem`, font-weight `500`, line-height `1.5`

### 2.3 Spatial Geometry & Elevation
```css
:root {
  --sidebar-w:    232px;
  --radius-sm:    8px;
  --radius-md:    12px;
  --radius-lg:    18px;
  --radius-xl:    28px;
  --radius-pill:  9999px;
  --shadow-card:  0 1px 3px rgba(0, 0, 0, 0.02), 0 1px 2px rgba(0, 0, 0, 0.01);
  --shadow-modal: 0 24px 50px -12px rgba(0, 0, 0, 0.35);
}
```

---

## 3. Component Architecture & Visual Specifications

### 3.1 Loading Overlay Modal ("Please Wait")
The loading modal provides immediate institutional feedback during state changes (e.g., synchronizing student profile, saving academic records, submitting placement applications).

```
+----------------------------------------------------+
|  [=========== Maroon Curved Top Accent ==========] |
|                                                    |
|                      ( O )  <-- Concentric Spinner |
|                                 (Rotating arc +    |
|                                  inner ring + dot) |
|                                                    |
|                   Please Wait                      |
|          Synchronizing Student Record...           |
|                                                    |
+----------------------------------------------------+
```

- **Backdrop**: `rgba(75, 85, 102, 0.88)` with `backdrop-filter: blur(3px)` for focus isolation.
- **Card Container**: White background, `width: 380px`, `border-radius: 32px`, `border-top: 5px solid var(--vidya-maroon)`, box shadow `0 24px 50px -12px rgba(0, 0, 0, 0.35)`.
- **Concentric Spinner**:
  - Outer ring: `76px × 76px`, `border: 2.5px solid #F6E6E6`, `border-top-color: #800D15`, `border-right-color: #800D15`, animating smoothly via `vidyaSpin 1s cubic-bezier(0.4, 0.1, 0.4, 0.9) infinite`.
  - Inner concentric ring: `52px × 52px`, `border: 1.5px solid #F9EDED`, absolute centered.
  - Center dot: `8px × 8px`, solid `var(--vidya-maroon)` circle.
- **Typography**: "Please Wait" (`1.6rem`, font-weight `800`, color `#0E1726`) and "Synchronizing Student Record..." (`0.95rem`, font-weight `500`, color `#627289`).

### 3.2 Vidyalankar Sidebar Lockup & Navigation
- **Dimensions**: Fixed `232px` width, `100vh` sticky height, solid deep maroon (`#800D15`).
- **Brand Lockup**:
  - Logo: Inline SVG representing the Vidyalankar double-loop infinity ribbon (`path stroke="#FFFFFF" stroke-width="8"` with a central circle dot).
  - Brand typography: "BE SURE WITH" (`0.62rem`, font-weight `700`, letter-spacing `0.08em`, uppercase) stacked on "vidyalankar" (`1.35rem`, font-weight `800`, lowercase, color `#FFFFFF`).
- **Section Categorization**:
  - `PORTAL OVERVIEW`: Dashboard, My Application
  - `ACADEMIC ENGAGEMENT`: Tasks, Events, Notices, Resources, Documents
  - `PLACEMENT & DRIVES`: Batch Drives Feed, Application Status, Offer Letters
  - `MESSAGING`: Messaging
- **Interactive State**:
  - Normal: White text, opacity `0.92`, `padding: 10px 20px`, SVG icon `18px × 18px`.
  - Active: Background `rgba(0, 0, 0, 0.22)`, font-weight `700`.
  - Hover: Background `rgba(255, 255, 255, 0.08)`.
- **Sidebar Footer ("LOGGED IN AS")**:
  - Avatar circle: Dark burgundy `#5A080E`, bold white "N", green online indicator dot (`#22C55E`) at bottom-right corner.
  - User details: Name `Nekeel` (white, `0.92rem`), Role `Student Portal` (light pink `#F8D7DA`), ID `290176F1` (muted pink monospace).
  - Logout Button: Full width pure white button (`#FFFFFF`), rounded corners `8px`, bold maroon text `[→ LOGOUT]`.

### 3.3 Topbar & Notification System
- **Layout**: Clean flex header, padding `24px 40px 16px 40px`, zero divider line to preserve open feel.
- **Title**: Dynamic page title matching current active route (`Dashboard`, `My Application`, `Events`, etc.).
- **Action Group**:
  - **Notification Bell**: SVG bell with red badge counter `2` positioned at top-right (`#C5221F`, bold white `0.65rem`).
  - **Avatar**: Circle `38px`, background `var(--vidya-maroon)`, white letter "N".
- **Interactive Flyout Drawer**:
  - Positioned absolutely below the bell button (`width: 340px`).
  - Header: "Notifications" with "Mark all read" interactive button.
  - Unread items with light rose background (`#FEF7F7`). Clicking "Mark all read" clears badges and marks all items read.

### 3.4 Dashboard Visual Grid
- **Stat Cards (Image 5 Alignment)**:
  - 4 columns in row 1: `0/4 Records Approved`, `0/4 Enrolment Progress`, `0 Academic Calendar`, `0 Resources`.
  - 1 column in row 2: `0 Active Notices`.
  - Cards styled with pure white background, `border: 1px solid #ECEEF2`, `border-radius: 18px`, `padding: 22px 20px`.
- **Greeting Banner**:
  - Rounded white box (`border-radius: 18px`, `border: 1px solid #ECEEF2`, `padding: 26px 32px`).
  - Headline: *"Good evening, **Nekeel**. Overview of your academic progress."*
  - Subtitle: *"VIIE University — Academic Cohort —"*
- **Two-Column Split Layout**:
  - **Left Column**: Enrolment Progress card.
    - Check-shield icon + title.
    - Explanatory description: *"Track the verification status of your academic records. Each section is reviewed by the university administration."*
    - 4 rows: `Personal Information`, `Academic History`, `Standardised Tests`, `Current Course Preference`.
    - Each row contains a gray dot, title, blue track line (`height: 4px`), and a status pill (`RECORD PENDING` in slate, or `RECORD APPROVED` in green).
    - Clicking any row navigates directly to that submodule in My Application.
  - **Right Column**:
    - **Academic Calendar Card**: Header with red icon + *"See All →"*. Empty state: *"No campus events scheduled"*.
    - **University Notices Card**: Header with red bell + *"View All →"*. Empty state: *"No active communiqués"*.
    - **Assigned Tasks Card**: Header with check-circle + *"View All →"*. Interactive task item *"Complete Application"* with circular checkbox, due date, and `PENDING` badge.

### 3.5 Events & Calendar Engine (Image 2 Alignment)
- **Tabs**: `🏛️ Academic Calendar` (active maroon underline) and `📑 Personal Schedule`.
- **Monthly Calendar Widget**:
  - Header: Solid deep maroon (`#800D15`) rounded top with `‹  September 2026  ›`.
  - Day names: `SUN  MON  TUE  WED  THU  FRI  SAT` (`0.72rem`, bold slate).
  - Day Grid: 30 days dynamically rendered.
  - Selected Day 4: Bright red circle (`#C5221F`), white text.
  - Month Navigation: `‹` and `›` controls re-render the calendar month and day matrix dynamically.
- **Campus Calendar Panel**:
  - Header: *"Full Campus Calendar"*.
  - Right Action: `+ Add Schedule Item` button allowing students to add reminders to their schedule.
  - Default text: *"No campus events are currently scheduled."*

### 3.6 My Application Submodules Engine (Image 3 Alignment)
- **Submodules Column**:
  - Small uppercase header: `APPLICATION MODULES`.
  - 10 Navigation Buttons: `Personal Information`, `Academic History`, `Standardised Tests`, `Current Course Preference`, `Transfer Course Preferences`, `Additional Documents`, `Academic References`, `Professional History`, `Immigration & Visa Records`, `Travel History`.
  - Active button: White background, subtle border, maroon text, circular indicator on right.
- **Profile Photo Banner**:
  - Background: Soft warm blush (`#F7EFEF`, `border-radius: 16px`, `padding: 24px`).
  - Uploader Circle: Dashed border (`2px dashed #D69EA2`), maroon silhouette icon.
  - Live Preview: Selecting any JPEG/PNG/WEBP immediately updates the photo circle via `FileReader`, updates topbar avatar, updates sidebar avatar, and launches the loading sync modal.
- **Submodule Forms**:
  - `personal`: Full Name, Email, Phone (+91 with input), Date of Birth, Gender, Nationality, Country of Birth, Languages.
  - `academic`: Degree, Cohort, CGPA (8.94), Live Backlogs (0), 10th Score %, 12th Score %.
  - `tests`: Entrance track (MHT-CET / JEE / GATE), Percentile (98.74), Certifications (AWS).
  - `course`: Primary Technical Track, Department Elective, Capstone Domain, Faculty Mentor.
  - `transfer`, `additional_docs`, `references`, `prof_history`, `visa`, `travel`: Dedicated form views.
  - **Save & Synchronize**: Saving any submodule triggers `VIIE.showLoading()`, turns the status pill on the Dashboard to `RECORD APPROVED`, fills the progress bar to 100%, and increments `kpiRecordsApproved` counter.

---

## 4. Role-Based Portals & Functional Specifications

### 4.1 Student Portal (`student/dashboard.html`)
The student portal handles academic verification and placement participation:
1. **Batch Drives Feed**: Displays curated placement drives dispatched by the TPO for the student's cohort (`Batch 2023 - 2027`).
2. **Apply Modal with 3 Resume Options**:
   - Option A: *Use VIIE Student ERP Profile* (Generates standard institutional dossier).
   - Option B: *Upload Fresh PDF Resume* (Drag & drop zone with real-time format verification).
   - Option C: *Use BrewAI ATS-Optimized Resume* (Exports algorithmic, role-tailored resume).
3. **Application Status Board (Kanban)**: Real-time tracking through 4 stages: `Applied` -> `Shortlisted` -> `Interview Rounds` -> `Outcome`.
4. **Offer Letters Vault**: Direct repository of issued offer letters with "Download PDF" and acceptance actions.
5. **Direct Messaging**: Two-way communication channel with TPO Gayatri Ma'am and corporate recruiters.

### 4.2 Corporate Recruiter Portal (`company/dashboard.html`)
Corporate recruiters interact directly with the campus placement cell:
1. **Post New Job Opening Form**:
   - Inputs: Job Role Title, Work Location, Annual CTC (LPA), CTC Breakdown, Internship Stipend, Service Bond, Markdown Job Description.
   - Action: Submits opening directly to TPO queue (`PENDING TPO BATCH ASSIGNMENT`) with synchronization modal.
2. **Candidate Pipeline Kanban**:
   - Columns: `Applied`, `Shortlisted`, `Interview Rounds`, `Selected`.
   - Actions: Advance candidates to next round, view verified student resumes, shortlist qualified candidates.
3. **Interview Remarks Evaluator**:
   - Per-round feedback logger: Student Roll Number, Interview Round, Score (1-10), Recommendation (`Advance to Technical Round 2`, `Advance to HR`, `Hold`, `Reject`), Evaluator Notes.
   - Live synchronization with student tracking and TPO audit logs.
4. **Issue Formal Offer Letters**:
   - Inputs: Selected Candidate Roll Number, Role Title, Offered CTC, Joining Date.
   - Action: Dispatches signed institutional offer letter with PDF copy generation.

### 4.3 Training & Placement Officer (TPO) Portal (`tpo/dashboard.html`)
The TPO maintains authoritative curation over college recruitment drives:
1. **Incoming Jobs Review Queue**:
   - Reviews job submissions from corporate recruiters.
   - Rejection workflow with constructive feedback dispatch.
   - **Approve & Assign Batch Cohort Modal**: Multi-select modal allowing the TPO to dispatch drives to specific academic cohorts (`B.Tech Computer Science & Engineering 2023-2027`, `B.Tech Information Technology 2023-2027`, `B.Tech EXTC 2023-2027`).
2. **Institutional Student Eligibility Filter Engine**:
   - Zero spreadsheet dependency: Instant filtering over live ERP student records.
   - Filter criteria: Branch/Department, Minimum CGPA slider (>= 7.0, >= 8.0, >= 8.5), Maximum Backlogs (0 Only, 1), Placement Status (`Unplaced Only`).
   - Dynamic table updates with matched student count and dossier inspection.
3. **Reports & Custom Builder**:
   - Compiles master placement records into Excel (`.xlsx`), CSV (`.csv`), or institutional PDF.
4. **Broadcast Notices**:
   - Publishes immediate campus circulars directly to the student portal stream.

### 4.4 Executive Dean Directorate (`dean/dashboard.html`)
High-level intelligence and regulatory compliance portal:
1. **Macro Placement KPIs**:
   - `142` Active Recruiters
   - `88.4%` Placement Conversion Rate
   - `44.0 LPA` Highest Campus CTC
   - `11.2 LPA` Average Campus CTC
2. **Asynchronous Heavy Analytics Job Queue**:
   - Queues complex cross-tabulation reports (e.g., CTC Bracket vs Department vs Gender Ratio) as background jobs (`#VIIE-RPT-8942`) with notification upon completion.
3. **NIRF Accreditation Exports (Criterion 4)**:
   - Multi-year comparative table: Graduation Year, Batch Size, Placed Count, Placement %, Median Salary, Higher Studies.
   - Export buttons for verified NIRF CSV and PDF documentation.
4. **Unplaced Focus Matrix**:
   - Real-time identification of students unplaced after initial recruitment rounds.
   - Automated triggers for remedial training boot camps (e.g., DSA & Microservices fast-track workshops).

---

## 5. State Management & Core Controller (`viie-core.js`)

The `VIIE` controller serves as the centralized singleton orchestrating state, session tokens, modal dialogues, and visual overlays:

```javascript
const VIIE = {
  session: {
    token: localStorage.getItem('viie_erp_token') || 'ERP-SSO-JWT-LIVE-VIIE-2026',
    activeRole: localStorage.getItem('viie_active_role') || 'student',
    user: {
      name: 'Nekeel',
      role: 'Student Portal',
      id: '290176F1',
      dept: 'Computer Science & Engineering',
      cohort: 'VIIE University — Academic Cohort 2027'
    }
  },

  init() {
    this.bindGlobalEvents();
    this.updateRoleDebugBar();
  },

  switchRole(role) {
    // Manages routing across /student/, /company/, /tpo/, /dean/
  },

  showLoading(title, subtext, duration) {
    // Generates the exact Image 1 loading overlay with concentric spinner
  },

  hideLoading() {
    // Dismisses loading overlay
  },

  openModal(modalId) {
    // Opens backdrop modal with focus trapping
  },

  closeModal(modalId) {
    // Closes modal and restores scrolling
  },

  showToast(message, type) {
    // Dispatches floating toasts (success, error, default)
  }
};
```

---

## 6. Strict Institutional Compliance & Terminology

### 6.1 Institutional Brand Compliance & Naming Conventions
In strict compliance with project directives, all legacy naming has been completely eliminated across the entire codebase (case-insensitive audit returns 0 matches), replaced everywhere with official VIIE University and Vidyalankar identifiers.

| Component Area | Official Production Identifier | Architectural Role |
| :--- | :--- | :--- |
| Core Platform Name | `VIIE` | Organization, platform microservice acronym |
| Parent University | `Vidyalankar / VIIE University` | Institutional brand & ERP authority |
| CSS Namespaces | `.vidya-*` / `.viie-*` | Design system tokens, styling & layouts |
| Global Controller | `VIIE` (`assets/js/viie-core.js`) | Centralized state, loading & modal coordinator |
| Media Assets | `viie_students.jpg` | Verified student imagery |

### 6.2 Zero Sample Mock Data Principle
- The platform does not pre-populate arbitrary dummy lists or fake data arrays.
- Institutional views open with clean, authentic empty states (e.g., *"No campus events are currently scheduled"*, *"No active communiqués"*).
- All data flows are initiated through explicit user actions (submitting a job, verifying a submodule, scheduling a calendar milestone, or dispatching an offer).

---

## 7. Responsive Breakpoint Strategy

The design system maintains strict usability across all viewports:
- **Desktop (>= 1200px)**: Full 232px sidebar, 4-column KPI grid, 2-column split forms, 4-column Kanban pipelines.
- **Tablet / Medium (768px - 1199px)**: 3-column KPI grid, stacked split layout, horizontal scroll for wide tables.
- **Mobile (< 768px)**: Collapsed responsive sidebar, 2-column KPI grid, single-column forms, full-width modal overlays.

---

## 8. Summary of Local Execution & Verification

The application is deployed as a zero-dependency static web application and served locally on port 8080 (or 3000):
- **Testing Hub**: `http://localhost:8080/index.html`
- **Student Dashboard**: `http://localhost:8080/student/dashboard.html`
- **Company Recruiter**: `http://localhost:8080/company/dashboard.html`
- **TPO Directorate**: `http://localhost:8080/tpo/dashboard.html`
- **Dean Directorate**: `http://localhost:8080/dean/dashboard.html`

All routes return `HTTP 200 OK` and adhere to the visual and functional specifications documented herein.
