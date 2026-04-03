# UI/UX Design & Frontend Implementation Specification
# Land Intelligence Management Platform (LIMP)
**For:** Figma Designer + Frontend Developer  
**Version:** 1.0 | **Date:** March 2026  
**Platform:** Web (Desktop-first, responsive down to tablet)  
**Frontend Stack:** Next.js (App Router) + React 19 + TypeScript strict + shadcn/ui + Tailwind CSS v4. Backend data platform (CockroachDB, Kafka, Cassandra) does not change UI patterns — all data via `/api/v1/`.

*Engineering tracking:* [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) · [COMPLETED.md](COMPLETED.md) · [BACKLOG.md](BACKLOG.md).

---

## Table of Contents
1. [Product Context](#1-product-context)
2. [Design Direction & Tone](#2-design-direction--tone)
3. [Design System](#3-design-system)
4. [User Roles & What They See](#4-user-roles--what-they-see)
5. [Navigation & Layout Structure](#5-navigation--layout-structure)
6. [Page-by-Page Specifications](#6-page-by-page-specifications)
7. [Component Library](#7-component-library)
8. [Interaction & UX Rules](#8-interaction--ux-rules)
9. [Frontend Developer Handoff Notes](#9-frontend-developer-handoff-notes)

---

## 1. Product Context

### What is this?
LIMP is an **internal enterprise operations platform** used daily by a land acquisition company in Karnataka. It is not a public-facing product. Users are professionals — advocates, revenue officers, surveyors, and management — who will use this for hours every day.

### Who uses it?
| User | Primary use | Usage pattern |
|------|-------------|---------------|
| Founder | Monitor everything, make decisions | Daily, from mobile/desktop anywhere |
| Management | View land files, assign tasks | Daily, desktop |
| In-House Advocates | Manage legal cases and hearings | Daily, desktop |
| External Advocates | Upload documents for their cases | Few times a week, any device |
| Revenue Team | Track government workflows | Daily, desktop |
| Surveyors | View assignments, upload survey data | Field use, tablet/mobile |
| Field Staff | View and complete assigned tasks | Mobile, field conditions |

### Design priorities (in order)
1. **Clarity over decoration** — users are doing real work under time pressure
2. **Information density** — the founder needs to see a lot at once; don't waste space
3. **Trust and professionalism** — this handles legal and financial data; it must feel secure and authoritative
4. **Speed** — every interaction should feel immediate
5. **Role awareness** — each user should see exactly what they need, nothing extra

---

## 2. Design Direction & Tone

### Visual Identity
**Direction:** Enterprise-grade, authoritative, and calm — not a startup SaaS product. Think of Bloomberg Terminal meets modern enterprise software. Dark sidebar, clean content area, strong typography hierarchy.

**Feeling the design should evoke:** "I am in control. I can see everything. I trust this system."

**What to avoid:**
- Rounded, playful UI (this is not a consumer app)
- Purple gradients, neon accents, glassmorphism
- Excessive animation (distracting in a work tool)
- Overly sparse layouts (users need data density)
- Generic card grids everywhere

### Color Palette

```
Primary (Brand Blue)    #1A3C6E   — sidebar, headers, primary actions
Accent Blue             #2E5FA3   — interactive elements, links, badges
Light Blue (Tint)       #E8F0FB   — table row hover, info panels
Dark Background         #0F1E35   — sidebar background
Content Background      #F5F7FA   — main content area
White                   #FFFFFF   — cards, form areas
Dark Text               #1A1A2E   — primary body text
Muted Text              #6B7280   — secondary labels, placeholders
Border                  #E2E8F0   — card borders, dividers

Status Colors:
Success Green           #16A34A   — completed, active, obtained
Warning Amber           #D97706   — pending, in progress, approaching deadline
Danger Red              #DC2626   — overdue, blocked, failed compliance
Info Blue               #2563EB   — neutral info, scheduled items
Neutral Gray            #6B7280   — not applicable, inactive
```

### Typography

```
Display / Headings:     DM Sans (Google Fonts) — clean, geometric, authoritative
Body / UI:              Inter — highly readable at small sizes
Monospace (IDs/codes):  JetBrains Mono — for Land IDs, case numbers, dates
```

**Type Scale:**
```
Page title:       24px / DM Sans / Bold     / #1A1A2E
Section heading:  18px / DM Sans / SemiBold / #1A1A2E
Card title:       15px / DM Sans / SemiBold / #1A1A2E
Body:             14px / Inter  / Regular   / #1A1A2E
Secondary label:  12px / Inter  / Regular   / #6B7280
Data value:       14px / Inter  / Medium    / #1A1A2E
Land ID / code:   13px / JetBrains Mono / Regular / #2E5FA3
```

### Spacing System
Base unit: 4px

```
xs:   4px    (tight inline gaps)
sm:   8px    (icon-to-label, tag padding)
md:   16px   (card internal padding, form field gaps)
lg:   24px   (section gaps, card-to-card)
xl:   32px   (page section separation)
2xl:  48px   (major section separation)
```

### Border Radius
```
sm:   4px    (tags, badges, small inputs)
md:   8px    (cards, modals, buttons)
lg:   12px   (larger containers)
```

### Shadows
```
card:    0 1px 3px rgba(0,0,0,0.08), 0 1px 2px rgba(0,0,0,0.04)
modal:   0 20px 60px rgba(0,0,0,0.15)
dropdown: 0 8px 24px rgba(0,0,0,0.12)
```

---

## 3. Design System

### 3.1 Buttons

```
Primary:    bg=#1A3C6E  text=white   hover=bg #2E5FA3   — main CTA actions
Secondary:  bg=white    text=#1A3C6E border=#1A3C6E     hover=bg #E8F0FB
Danger:     bg=#DC2626  text=white   hover=bg #B91C1C   — destructive actions
Ghost:      bg=transparent text=#6B7280 hover=text #1A3C6E — low-emphasis actions

Size:
  sm:   height 32px / padding 8px 16px / font 13px
  md:   height 38px / padding 10px 20px / font 14px  (default)
  lg:   height 44px / padding 12px 24px / font 15px
```

### 3.2 Status Badges

Used throughout the app for case status, task status, document status, workflow status.

```
Design: pill shape (border-radius: 9999px), padding 3px 10px, font 12px medium

ACTIVE / COMPLETED / OBTAINED     →  bg #DCFCE7  text #16A34A  (green)
PENDING / IN PROGRESS / APPLIED   →  bg #FEF3C7  text #D97706  (amber)
OVERDUE / BLOCKED / FAILED        →  bg #FEE2E2  text #DC2626  (red)
SCHEDULED / SUBMITTED             →  bg #DBEAFE  text #2563EB  (blue)
CLOSED / DISPOSED / NOT APPLICABLE→  bg #F3F4F6  text #6B7280  (gray)
```

### 3.3 Data Tables

Used for: land file lists, case lists, task lists, hearing lists.

```
Header row:     bg #F5F7FA  text #6B7280 uppercase 11px tracking-wide
Body row:       bg white    text #1A1A2E 14px
Row hover:      bg #F0F7FF
Row selected:   bg #E8F0FB left-border 3px solid #2E5FA3
Border:         1px solid #E2E8F0 (horizontal lines only, no vertical borders)
Row height:     48px (comfortable data density)
Cell padding:   0 16px
Sticky header:  Yes — header stays fixed on scroll
```

### 3.4 Form Inputs

```
Height:           38px
Border:           1px solid #E2E8F0
Border (focus):   2px solid #2E5FA3
Border (error):   1px solid #DC2626
Background:       white
Border-radius:    6px
Font:             14px Inter
Placeholder:      #9CA3AF
Label:            12px Inter SemiBold #374151 — always above the field, never inside
Error message:    12px Inter #DC2626 — below the field, with a small warning icon
```

### 3.5 Cards

```
Background:     white
Border:         1px solid #E2E8F0
Border-radius:  8px
Shadow:         card shadow (see above)
Padding:        20px 24px
Card header:    title 15px DM Sans SemiBold + optional right-aligned action
Divider:        1px solid #E2E8F0 between header and content
```

### 3.6 Empty States

Every list and module must have a designed empty state.

```
Layout: centered vertically and horizontally in the content area
Icon: relevant icon (document for vault, scales for legal, etc.) — 48px, color #E2E8F0
Heading: 16px DM Sans SemiBold #1A1A2E — "No land files yet"
Sub-text: 14px Inter #6B7280 — "Create your first land file to get started."
CTA button: Primary button — only if the user role has create permission
```

### 3.7 Alert / Notification Banners

```
Danger (red):   bg #FEF2F2  border-left 4px #DC2626  icon ⚠️
Warning (amber): bg #FFFBEB  border-left 4px #D97706  icon ℹ️
Success (green): bg #F0FDF4  border-left 4px #16A34A  icon ✓
Info (blue):    bg #EFF6FF  border-left 4px #2563EB  icon ℹ
```

---

## 4. User Roles & What They See

### Navigation visibility by role

| Nav Item | Founder | Mgmt | In-House Adv | External Adv | Revenue | Surveyor IH | Surveyor FL | Field Staff |
|----------|---------|------|--------------|--------------|---------|-------------|-------------|-------------|
| Dashboard | ✅ Full | ✅ | ✅ Legal KPIs | ❌ | ✅ Revenue | ✅ Survey | ❌ | ❌ |
| Land Files | ✅ | ✅ | ✅ Read only | ❌ | ✅ Read only | ✅ Read only | ❌ | ❌ |
| Legal | ✅ | ✅ Read | ✅ Full | ✅ Own cases | ❌ | ❌ | ❌ | ❌ |
| Documents | ✅ | ✅ | ✅ Legal docs | ✅ Case docs | ✅ Rev docs | ✅ Survey | ❌ | ❌ |
| Tasks | ✅ All | ✅ Team | ✅ Own | ✅ Own | ✅ Own | ✅ Own | ✅ Own | ✅ Own |
| Revenue | ✅ | ✅ Read | ❌ | ❌ | ✅ Full | ❌ | ❌ | ❌ |
| Survey | ✅ | ✅ Read | ❌ | ❌ | ❌ | ✅ Full | ✅ Own task | ❌ |
| Users | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

**Rule for designer/developer:** Nav items not accessible to a role must be completely absent from the sidebar — not greyed out, not disabled. They should not exist in the DOM.

---

## 5. Navigation & Layout Structure

### 5.1 Overall Layout

```
┌────────────────────────────────────────────────────────────┐
│  TOPBAR (60px)                                             │
│  [Hamburger] [Page Title]      [Search] [Alerts] [Avatar]  │
├──────────────┬─────────────────────────────────────────────┤
│              │                                             │
│  SIDEBAR     │   MAIN CONTENT AREA                         │
│  (240px)     │                                             │
│              │   ┌─────────────────────────────────────┐   │
│  [Logo]      │   │  Page Header                        │   │
│              │   │  (breadcrumb + page title + CTA)    │   │
│  [Nav Item]  │   └─────────────────────────────────────┘   │
│  [Nav Item]  │                                             │
│  [Nav Item]  │   ┌─────────────────────────────────────┐   │
│  [Nav Item]  │   │  Content (table / form / cards)     │   │
│  ─────────── │   │                                     │   │
│  [Nav Item]  │   │                                     │   │
│              │   └─────────────────────────────────────┘   │
│  ─────────── │                                             │
│  [User Info] │                                             │
│  [Logout]    │                                             │
│              │                                             │
└──────────────┴─────────────────────────────────────────────┘
```

### 5.2 Sidebar Design

```
Width:              240px (collapsed: 64px with icons only)
Background:         #0F1E35 (dark navy)
Text color:         #CBD5E1
Active item:        bg #1A3C6E, text white, left-border 3px #2E5FA3
Hover item:         bg rgba(255,255,255,0.06)
Nav item height:    44px
Nav item padding:   0 16px
Icon size:          18px, right margin 10px
Section divider:    1px solid rgba(255,255,255,0.08)
Logo area:          60px height, padding 0 16px, text "LIMP" in DM Sans Bold white
```

### 5.3 Topbar

```
Height:         60px
Background:     white
Border-bottom:  1px solid #E2E8F0
Shadow:         0 1px 4px rgba(0,0,0,0.06)

Left:   Breadcrumb (Home > Land Files > LIMP-2026-0012)
Right:  [Global Search icon] [Notification bell with badge] [User avatar + name]
```

### 5.4 Page Header (within content area)

```
Layout:     flex, space-between, align-center
Title:      24px DM Sans Bold #1A1A2E
Subtitle:   14px Inter #6B7280 (optional — e.g. "23 active land files")
Right:      Primary action button (e.g. "+ New Land File")
Margin-bottom: 24px
```

---

## 6. Page-by-Page Specifications

---

### PAGE 1 — Login

**Purpose:** Secure entry point. Single form. Authoritative feel.

**Layout:** Centered card (420px wide) on a dark blue (#0F1E35) background with a subtle topographic pattern texture.

**Elements:**
- LIMP logo + "Land Intelligence Management Platform" title
- Email input
- Password input with show/hide toggle
- "Sign In" primary button (full width)
- "Forgot Password?" ghost link

**Notes:**
- No sign-up link (all accounts are admin-created)
- After 5 failed attempts, show a lockout message with countdown timer
- Redirect to role-specific home page on success

---

### PAGE 2 — Founder Dashboard

**Purpose:** Command centre. The founder should be able to assess the state of the entire business in under 10 seconds.

**Layout:** KPI cards row at top, then two-column layout below.

**Section 1 — KPI Cards (top row, 4 cards)**
```
Card 1: Total Land Files
  - Large number (e.g. "34")
  - Breakdown below: "12 Active · 8 Under Negotiation · 5 Committed · 9 Closed"
  - Link: "View all →"

Card 2: Court Hearings
  - "3 Today · 7 This Week"
  - Sub-text: last hearing outcome
  - Status badge: number of overdue POAs in red if > 0

Card 3: Open Tasks
  - Total count
  - "5 Overdue" in red badge
  - "12 Due Today" in amber

Card 4: Documents Pending
  - Number of land files with incomplete document checklist
  - "8 files need attention"
```

**Section 2 — Left column (60% width)**
```
Hearings This Week
  - Timeline/list view: date, case number, court, advocate name, POA status badge
  - Click row → opens case detail

Overdue Tasks
  - Table: task name, assigned to, module, how many days overdue
  - Sorted by most overdue first
```

**Section 3 — Right column (40% width)**
```
Advocate Compliance
  - List of all advocates with upcoming hearings
  - POA status for each (submitted / pending / overdue)
  - Red badge on name if overdue

Recent Activity Feed
  - Last 15 actions across the system
  - Format: "[User] [action] [object] · [time ago]"
  - e.g. "Ravi uploaded court order for Case OS-2024-112 · 2 hrs ago"
```

**Travel Mode:**
- Toggle in top-right of dashboard
- When ON: collapses to ONLY show red/critical items
- Background subtly shifts to a darker tint to indicate mode
- "Travel Mode ON" badge visible in topbar

---

### PAGE 3 — Land Files (List)

**Purpose:** Master list of all land parcels.

**Filters (top of page, horizontal row):**
```
[District dropdown] [Taluk dropdown] [Classification dropdown] [Status dropdown] [Search by Sy No / Land ID]
```

**Table columns:**
```
Land ID        | LIMP-2026-0012 (monospace, blue, clickable)
Location       | Village, Hobli, Taluk (stacked, two lines)
Survey No.     | Sy No + Hissa
Extent         | X Acres Y Guntas
Classification | Badge: Agricultural / Converted / Approved
Status         | Badge: Active / Committed / etc.
Legal Cases    | Number (e.g. "3") with blue badge
Documents      | Progress bar (e.g. 6/8 docs) with % complete
Last Updated   | Relative time (e.g. "2 days ago")
Actions        | View · Edit (role-based)
```

**Notes:**
- Clicking the Land ID opens the Land File Detail page
- Rows with overdue legal compliance should have a subtle left red border
- Paginated: 20 per page with pagination controls at bottom

---

### PAGE 4 — Land File Detail

**Purpose:** The master file view. Everything about one piece of land.

**Layout:** Full-width page with a sticky tab bar.

**Top section (always visible):**
```
Land ID badge (LIMP-2026-0012) — large, monospace
Location: Village → Hobli → Taluk → District (breadcrumb style)
Survey No. + Hissa + Extent + Classification
Status badge + last updated
```

**Tab Bar (sticky below the top section):**
```
[Overview] [Legal] [Documents] [Revenue] [Survey] [Valuation] [Tasks]
```
Only tabs relevant to the logged-in role are shown.

**Tab: Overview**
```
Two columns:
Left:  All land details (editable for Founder/Management)
Right: Quick stats — open tasks count, legal cases count, document completeness ring chart
```

**Tab: Legal**
```
Top: "+ Add Case" button (in-house advocate and above only)
Case cards (one per case):
  - Case number + type + court (header)
  - Party role badge + status badge
  - Assigned advocate name
  - Next hearing date (highlighted in amber if < 7 days, red if today)
  - "View Case" button

Clicking "View Case" → opens Case Detail page (new page or slide-over panel)
```

**Tab: Documents**
```
Document checklist — grid of document cards, one per doc type:
  Card shows:
    - Document name (e.g. "RTC")
    - Status badge (Certified Obtained / Applied & Pending / Not Applicable)
    - Last updated date + by whom
    - "View" button (if uploaded) / "Upload" button (if pending)
    - Version history link (e.g. "v3 · see history")
```

**Tab: Tasks**
```
List of tasks linked to this land file
Filter: All / My Tasks / Overdue
Same table as Tasks module but pre-filtered to this land
```

---

### PAGE 5 — Legal Case Detail

**Purpose:** Full case file view with hearing history and compliance tracking.

**Top section:**
```
Case number (large) + case type badge + status badge
Court jurisdiction · Party role
Assigned advocates (avatar chips with names)
Opposite advocate details (name + firm)
```

**Section: Hearing History (timeline)**
```
Timeline design (vertical, latest at top):
Each hearing entry:
  ├── Date (large, DM Sans)
  ├── Stage / what happened (notes)
  ├── POA status badge (Submitted / Overdue / Pending)
  ├── Court order (download link if uploaded)
  ├── Audio/Video summary (play icon if uploaded)
  └── Next date set
```

**Section: Documents (case-level)**
```
Plaint — version list with download links
Written Statement — version list with download links
Legal opinions received
```

**For External Advocates (restricted view):**
- Only see their assigned case — no other cases
- Can upload Plan of Action, hearing notes, court orders
- Cannot see: land file financial data, revenue data, investor data
- Upload area is prominent and easy — they mainly come here to upload

---

### PAGE 6 — Legal Calendar

**Purpose:** All hearings across all cases in a calendar view.

**Modes:** Month / Week / Day (toggle in top-right)

**Calendar events show:**
```
Case number + court name
Advocate name
POA status indicator (green dot = submitted, red dot = overdue, grey = pending)
```

**Filters:**
```
[Advocate filter] [Court filter] [Status filter: Show overdue only]
```

**Clicking an event:** Opens case detail as a slide-over panel.

---

### PAGE 7 — Tasks

**Purpose:** Task management for each user's assigned work.

**For Founder:** sees all tasks across all users.
**For all others:** sees only their own tasks.

**Tabs:**
```
[All] [Pending] [In Progress] [Overdue] [Completed]
```

**Table columns:**
```
Title         | Task name (clickable)
Land File     | Land ID link (if applicable)
Module        | Badge: Legal / Revenue / Survey / General
Assigned To   | Avatar + name (Founder view only)
Due Date      | Date (red if overdue, amber if due today)
Priority      | Badge: High / Medium / Low
Status        | Status badge
```

**Task Detail (slide-over panel on row click):**
```
Full title + description
Land file link
Module + Priority + Status
Due date + created date
Assigned to + created by
Status update button (Mark In Progress / Mark Complete)
Activity log (status changes with timestamps)
```

---

### PAGE 8 — Users & Access Management

**Founder only.**

**Table columns:**
```
Name | Email | Phone | Role (badge) | Status (Active/Inactive) | Last Login | Actions
```

**Create/Edit User:**
```
Form fields: Full name, Email, Phone, Role (dropdown), Status
For External Advocates: Case assignment section — multi-select of active cases
For Freelance Surveyors: Task assignment section
```

---

## 7. Component Library

Design and build these as reusable components. Every page is built from these.

| Component | Description |
|-----------|-------------|
| `LandIDTag` | Monospace blue pill showing "LIMP-2026-XXXX" — always clickable |
| `StatusBadge` | Pill badge with color by status type (see Section 3.2) |
| `PriorityBadge` | High / Medium / Low with color coding |
| `UserAvatar` | Avatar circle with initials fallback + name tooltip |
| `DocumentCard` | Document checklist item with status, upload, version history |
| `HearingTimelineItem` | Single entry in the hearing history timeline |
| `KPICard` | Dashboard stat card with large number, breakdown, and link |
| `ComplianceIndicator` | Green/Amber/Red dot with label for POA status |
| `FileUploadZone` | Drag-and-drop upload area with progress bar |
| `VersionHistory` | Expandable list of file versions with uploader + date |
| `RoleGuard` | Wrapper that shows children only for specified roles |
| `EmptyState` | Icon + heading + subtitle + optional CTA button |
| `ConfirmModal` | "Are you sure?" confirmation dialog for destructive actions |
| `PageHeader` | Title + subtitle + right-side CTA, consistent across all pages |
| `FilterBar` | Row of dropdowns + search input for list pages |
| `SlideOver` | Side panel overlay for detail views without full navigation |
| `ActivityFeed` | Scrollable list of timestamped activity events |
| `AlertBanner` | Contextual alert banner with left color border |

---

## 8. Interaction & UX Rules

### Loading States
- Every list page shows a skeleton loader (not a spinner) while data loads
- Every submit button shows a spinner and disables itself on click
- File uploads show a progress bar for files > 500KB

### Confirmation
- Any delete/archive action requires a confirmation modal
- Modal must name the specific item being deleted: "Archive land file LIMP-2026-0012?"
- Destructive button text must be specific: "Archive" not "OK"

### Form Behaviour
- All forms validate on blur (field loses focus), not on submit
- Form errors appear inline below the relevant field with a warning icon
- On submit error from API, show an alert banner at top of form — never silent failure
- On submit success, show a brief success toast (3 seconds) and redirect if applicable

### Notifications (in-app)
- Notification bell in topbar shows count badge
- Clicking opens a dropdown panel with the 10 most recent notifications
- Each notification has: icon, message, time ago, link to relevant item
- "Mark all as read" button at top of panel

### Error Pages
- `/403` — "You don't have permission to view this page" + button to go back
- `/404` — "Page not found" + button to go to dashboard
- Both pages should use the full layout (sidebar + topbar) if the user is authenticated

### Responsive Behaviour
- Desktop (1280px+): Full sidebar visible, full table layout
- Tablet (768–1279px): Sidebar collapses to icon-only, tables scroll horizontally
- Mobile (< 768px): Sidebar becomes a bottom sheet or hamburger drawer; tables become card lists

---

## 9. Frontend Developer Handoff Notes

### Tech Stack
```
Next.js 16 (App Router, Turbopack in dev)
React 19, TypeScript strict
@tanstack/react-query (server state, API caching)
Zustand (global client state: auth, user, UI state)
Axios (HTTP client with interceptors)
shadcn/ui + Tailwind CSS v4 (component library)
React Hook Form + Zod (form handling + validation)
lucide-react (icons)
```

### File Structure
```
src/
├── api/                    # One file per module (land.js, legal.js, tasks.js)
├── components/             # Reusable components (see Component Library above)
│   ├── ui/                 # Base design system components (Button, Badge, Card, etc.)
│   └── modules/            # Domain components (LandIDTag, HearingTimelineItem, etc.)
├── pages/                  # Route-level components
│   ├── auth/               # Login
│   ├── dashboard/          # Founder dashboard
│   ├── land/               # Land list + detail
│   ├── legal/              # Cases + calendar
│   ├── documents/          # Document vault
│   ├── tasks/              # Tasks
│   ├── revenue/            # Revenue workflows (Phase 2)
│   └── survey/             # Survey (Phase 2)
├── hooks/                  # Custom hooks (useCurrentUser, useLandFiles, etc.)
├── store/                  # Zustand stores (authStore, uiStore)
├── routes/                 # Route definitions + ProtectedRoute + RoleGuard
├── utils/                  # Formatters, constants, validators
└── styles/                 # Global CSS, CSS variables, typography
```

### API Conventions
```javascript
// All API calls use the configured Axios instance from src/api/client.js
// Never use raw fetch() in components
// All data fetching done with React Query — no useEffect for API calls

// Example:
const { data: landFiles, isLoading } = useQuery({
  queryKey: ['land-files', filters],
  queryFn: () => fetchLandFiles(filters)
})
```

### Auth Flow
```
1. POST /api/v1/auth/login/ → access token + refresh token
2. Access token: stored in Zustand store (memory only)
3. Refresh token: stored in httpOnly cookie
4. Axios interceptor: injects "Authorization: Bearer {token}" on every request
5. 401 response: attempt token refresh, if fails → logout + redirect to /login
6. 403 response: redirect to /403 page
```

### Role-Based Rendering
```jsx
// Use RoleGuard wrapper for all conditionally rendered UI
import { RoleGuard } from '@/components/ui/RoleGuard'

<RoleGuard roles={['FOUNDER', 'MANAGEMENT']}>
  <Button>Edit Land File</Button>
</RoleGuard>

// Use useCurrentUser hook to get role in logic
const { user } = useCurrentUser()
```

### File Upload Flow
```
1. User selects file
2. Call POST /api/v1/files/presigned-upload/ with {land_id, doc_type, filename, file_size}
3. Receive {s3_key, upload_url}
4. PUT file directly to upload_url (S3) — show progress bar
5. On S3 upload success, call POST /api/v1/files/confirm-upload/ with {s3_key, land_document_id}
6. React Query invalidates the document list for this land file
```

### Environment Variables
```
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

### Key UX Rules for Developer
- Every list page must have a loading skeleton — use shadcn Skeleton or build custom
- All forms: use React Hook Form, validate on blur, show inline errors
- Never store auth tokens in localStorage — memory + httpOnly cookie only
- All destructive actions need a ConfirmModal — no direct execution on click
- Tables must support keyboard navigation (tab between rows, enter to open)
- Page titles in `<title>` tag must update on route change

---

*Document Version: 1.0 | For: UI/UX Designer (Figma) + Frontend Developer | March 2026*
