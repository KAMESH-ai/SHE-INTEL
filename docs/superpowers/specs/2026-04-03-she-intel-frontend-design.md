# SHE-INTEL Frontend Specification

## Overview
- **Project**: SHE-INTEL Health Dashboard
- **Type**: Single-page web application (SPA)
- **Stack**: Vanilla HTML/CSS/JS, Lucide Icons
- **Target**: Premium dark-mode health analytics dashboard for Indian women

## Design Philosophy
- Glassmorphism with subtle transparency and blur
- Premium, minimal, AI + medical aesthetic
- Near-black background with soft card surfaces
- Accent colors only for alerts and positive indicators

## Color Palette
| Purpose | Color |
|---------|-------|
| Background | #0B0F14 |
| Card | #11161D |
| Border | #1F2933 |
| Text Primary | #E5E7EB |
| Text Secondary | #9CA3AF |
| Accent Red | #FF6B6B |
| Accent Green | #22C55E |
| Warning | #F59E0B |

## Typography
- Font: Inter (Google Fonts)
- Headings: Semi-bold (600)
- Body: Regular (400)
- Letter-spacing: slightly tight

## Layout
- Max-width: 1100px, centered
- Padding: 40px
- Border-radius: 12-16px
- Soft shadow: 0 10px 30px rgba(0,0,0,0.4)

---

## Pages & Components

### 1. Navigation Bar (All Pages)
- Fixed top position
- Background: #11161D with backdrop blur
- Logo: "SHE-INTEL" left aligned, accent style
- Region selector: dropdown with Indian states
- Profile section: avatar + name, logout button right
- Height: 64px

### 2. Dashboard Home (`#/` or `#dashboard`)
- Welcome heading: "Welcome, [User Name]" - large bold
- **Feature Cards Row** (3 cards):
  - Card 1: Calendar icon + "Calendar" + "View your cycles"
  - Card 2: Activity icon + "Health Analysis" + "Run AI analysis"
  - Card 3: Heart icon + "Log Period" + "Track your period"
- **Stats Card**:
  - Title: "Periods Logged"
  - Value: count number
  - Subtitle: "Total tracked cycles"

### 3. Health Analysis Input (`#analysis`)
- Form card with fields:
  - Age: dropdown (18-55)
  - State: dropdown (all Indian states from API)
  - Period Start: date picker
  - Period End: date picker
  - Symptoms: textarea placeholder "Describe your symptoms..."
- Buttons:
  - "Run Analysis" (primary, accent red)
  - "Load Demo" (secondary)
- Loading state: spinner while analyzing

### 4. Analysis Results (`#results`)
- **Risk Gauge**: 
  - Circular progress indicator (SVG)
  - 70% fill with animation
  - Center text: risk percentage
  - Below: condition label "PCOS – High Risk" in red
- **Insight Cards Grid** (2x2):
  - India Context: iron, vitamin D, general tips
  - Air Quality: AQI badge with color coding
  - Community Data: horizontal bar comparison
  - Research Gap: info card
- **Sections**:
  - Lab Test Recommendations (list)
  - Government Schemes (list)
  - Recommended Actions (checklist)
- **Disclaimer**: warning box at bottom with muted border

### 5. Calendar Page (`#calendar`)
- **Header**: Month/Year with prev/next arrows
- **Grid**: 7-column (Sun-Sat)
  - Period days: soft red background (#FF6B6B at 20% opacity)
  - Current day: subtle highlight
  - Empty days: muted gray (#1F2933)
- **Recent Periods List**:
  - Date range + flow level
  - Scrollable if >5 items
- **Add Button**: "+ Add Period" opens modal

### 6. Log Period Modal
- Centered overlay with backdrop blur
- Card with fields:
  - Start Date (date picker)
  - End Date (date picker)
  - Flow Level (dropdown: Light, Medium, Heavy)
  - Symptoms (textarea)
- Buttons:
  - "Cancel" (secondary)
  - "Save" (primary)

---

## API Integration

### Endpoints
| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/auth/me` | Get current user |
| POST | `/analyze` | Run health analysis |
| GET | `/periods` | Get user's periods |
| POST | `/periods` | Create new period |
| GET | `/periods/prediction` | Get cycle prediction |
| GET | `/states` | Get state list |

### Authentication
- JWT stored in localStorage
- Token sent in Authorization header
- Redirect to login if 401 response

### Demo Mode
- Button to load sample data for testing
- Pre-fills form with mock symptoms

---

## Visual Effects

### Animations
- Page transitions: fade in (200ms ease)
- Card hover: translateY(-2px) with shadow increase
- Circular gauge: stroke-dasharray animation on load
- Modal: fade + scale in

### Glassmorphism
- Navbar: background rgba(17,22,29,0.8) + backdrop-blur(12px)
- Modal backdrop: rgba(0,0,0,0.6) + blur(4px)

### Shadows
- Cards: 0 10px 30px rgba(0,0,0,0.4)
- Elevated: 0 20px 40px rgba(0,0,0,0.5)

---

## Acceptance Criteria

1. All 5 pages render correctly with dark theme
2. Navigation works via hash routes
3. API calls work with proper auth
4. Modal opens/closes smoothly
5. Calendar displays period days correctly
6. Risk gauge animates on results page
7. Form validation works
8. Responsive on mobile (min-width 320px)
9. No console errors on page load
10. All Lucide icons render correctly