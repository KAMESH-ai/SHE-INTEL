# SHE-INTEL Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a premium dark-mode health dashboard SPA with glassmorphism UI that connects to the existing FastAPI backend.

**Architecture:** Single HTML file with vanilla JS router, CSS variables for theming, Lucide icons via CDN. All pages in one SPA with hash-based routing.

**Tech Stack:** Vanilla HTML/CSS/JS, Lucide Icons CDN, Google Fonts (Inter)

---

## File Structure

- `index.html` - Main SPA entry point with all HTML, CSS, JS
- `backend/main.py` - Existing FastAPI backend (no changes needed)
- `backend/models.py` - Existing models
- `backend/database.py` - Existing database

---

## Task 1: Setup Base HTML & CSS Variables

**Files:**
- Modify: `index.html` - Replace entirely

- [ ] **Step 1: Write base HTML structure with CSS variables**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>SHE-INTEL | Health Intelligence</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <script src="https://unpkg.com/lucide@latest"></script>
  <style>
    :root {
      --bg-primary: #0B0F14;
      --bg-card: #11161D;
      --border: #1F2933;
      --text-primary: #E5E7EB;
      --text-secondary: #9CA3AF;
      --accent-red: #FF6B6B;
      --accent-green: #22C55E;
      --warning: #F59E0B;
      --radius: 12px;
      --shadow: 0 10px 30px rgba(0,0,0,0.4);
      --shadow-elevated: 0 20px 40px rgba(0,0,0,0.5);
    }
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: 'Inter', sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      min-height: 100vh;
      line-height: 1.6;
    }
    .container { max-width: 1100px; margin: 0 auto; padding: 0 40px; }
    .card {
      background: var(--bg-card);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 24px;
      box-shadow: var(--shadow);
    }
    .btn {
      padding: 12px 24px;
      border-radius: var(--radius);
      border: none;
      cursor: pointer;
      font-weight: 500;
      font-family: inherit;
      transition: all 0.2s ease;
    }
    .btn-primary {
      background: var(--accent-red);
      color: white;
    }
    .btn-primary:hover { opacity: 0.9; transform: translateY(-1px); }
    .btn-secondary {
      background: transparent;
      border: 1px solid var(--border);
      color: var(--text-primary);
    }
    .btn-secondary:hover { border-color: var(--text-secondary); }
  </style>
</head>
<body>
  <div id="app"></div>
  <script src="app.js"></script>
</body>
</html>
```

- [ ] **Step 2: Create empty app.js with router skeleton**

```javascript
const App = {
  init() {
    this.renderNavbar();
    this.render();
    window.addEventListener('hashchange', () => this.render());
  },
  renderNavbar() { /* TODO */ },
  render() {
    const route = window.location.hash || '#dashboard';
    const app = document.getElementById('app');
    if (route === '#dashboard') app.innerHTML = Dashboard.render();
    else if (route === '#analysis') app.innerHTML = Analysis.render();
    else if (route === '#results') app.innerHTML = Results.render();
    else if (route === '#calendar') app.innerHTML = Calendar.render();
  }
};
document.addEventListener('DOMContentLoaded', () => App.init());
```

- [ ] **Step 3: Test base loads without errors**

Open `index.html` in browser - should see minimal page with no console errors.

- [ ] **Step 4: Commit**

```bash
git add index.html && git commit -m "feat: base HTML structure with CSS variables"
```

---

## Task 2: Navigation Bar Component

**Files:**
- Modify: `index.html` - Add navbar HTML/CSS
- Modify: `app.js` - Add navbar render function

- [ ] **Step 1: Add navbar styles**

```css
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: rgba(17,22,29,0.8);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--border);
  z-index: 100;
}
.navbar .container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
}
.logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--accent-red);
  letter-spacing: -0.5px;
}
.nav-center { display: flex; gap: 8px; }
.nav-link {
  padding: 8px 16px;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
}
.nav-link:hover, .nav-link.active {
  color: var(--text-primary);
  background: var(--border);
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.profile-section {
  display: flex;
  align-items: center;
  gap: 12px;
}
.profile-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--accent-red);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
}
.profile-name {
  font-size: 14px;
  color: var(--text-primary);
}
.logout-btn {
  color: var(--text-secondary);
  font-size: 13px;
  cursor: pointer;
  background: none;
  border: none;
}
.logout-btn:hover { color: var(--accent-red); }
```

- [ ] **Step 2: Add navbar HTML to App.renderNavbar()**

```javascript
renderNavbar() {
  const navItems = [
    { hash: '#dashboard', label: 'Dashboard', icon: 'home' },
    { hash: '#analysis', label: 'Analysis', icon: 'activity' },
    { hash: '#calendar', label: 'Calendar', icon: 'calendar' },
  ];
  const activeRoute = window.location.hash || '#dashboard';
  return `
    <nav class="navbar">
      <div class="container">
        <div class="logo">SHE-INTEL</div>
        <div class="nav-center">
          ${navItems.map(item => `
            <a href="${item.hash}" class="nav-link ${activeRoute === item.hash ? 'active' : ''}">
              <i data-lucide="${item.icon}" style="width:16px;height:16px;margin-right:6px;vertical-align:middle"></i>
              ${item.label}
            </a>
          `).join('')}
        </div>
        <div class="nav-right">
          <div class="profile-section">
            <div class="profile-avatar">D</div>
            <span class="profile-name">Demo User</span>
          </div>
          <button class="logout-btn" onclick="App.logout()">Logout</button>
        </div>
      </div>
    </nav>
    <div style="padding-top: 64px"></div>
  `;
}
```

- [ ] **Step 3: Add Lucide icon initialization**

After app.innerHTML assignment, call:
```javascript
if (window.lucide) window.lucide.createIcons();
```

- [ ] **Step 4: Test navbar renders**

Verify logo, nav links, and profile section all display correctly.

- [ ] **Step 5: Commit**

```bash
git add index.html app.js && git commit -m "feat: add navigation bar component"
```

---

## Task 3: Dashboard Home Page

**Files:**
- Modify: `app.js` - Add Dashboard object

- [ ] **Step 1: Add Dashboard.render() with welcome section**

```javascript
const Dashboard = {
  render() {
    return `
      <div class="container" style="padding: 40px 40px">
        <h1 style="font-size:32px;font-weight:600;margin-bottom:8px">Welcome, Demo User</h1>
        <p style="color:var(--text-secondary);margin-bottom:32px">Your health dashboard at a glance</p>
        
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:20px;margin-bottom:32px">
          <div class="card" style="cursor:pointer;transition:all 0.2s" onclick="window.location.hash='#calendar'">
            <i data-lucide="calendar" style="color:var(--accent-red);margin-bottom:12px"></i>
            <h3 style="font-size:18px;font-weight:600;margin-bottom:4px">Calendar</h3>
            <p style="color:var(--text-secondary);font-size:14px">View your cycles</p>
          </div>
          <div class="card" style="cursor:pointer;transition:all 0.2s" onclick="window.location.hash='#analysis'">
            <i data-lucide="activity" style="color:var(--accent-red);margin-bottom:12px"></i>
            <h3 style="font-size:18px;font-weight:600;margin-bottom:4px">Health Analysis</h3>
            <p style="color:var(--text-secondary);font-size:14px">Run AI analysis</p>
          </div>
          <div class="card" style="cursor:pointer;transition:all 0.2s" onclick="App.openPeriodModal()">
            <i data-lucide="heart" style="color:var(--accent-red);margin-bottom:12px"></i>
            <h3 style="font-size:18px;font-weight:600;margin-bottom:4px">Log Period</h3>
            <p style="color:var(--text-secondary);font-size:14px">Track your period</p>
          </div>
        </div>
        
        <div class="card">
          <h3 style="font-size:20px;font-weight:600;margin-bottom:8px">Periods Logged</h3>
          <p style="font-size:36px;font-weight:700;color:var(--accent-green)">12</p>
          <p style="color:var(--text-secondary);font-size:14px">Total tracked cycles</p>
        </div>
      </div>
    `;
  }
};
```

- [ ] **Step 2: Update App.render() to include Dashboard**

```javascript
render() {
  const route = window.location.hash || '#dashboard';
  const app = document.getElementById('app');
  let html = this.renderNavbar();
  
  if (route === '#dashboard') html += Dashboard.render();
  else if (route === '#analysis') html += Analysis.render();
  else if (route === '#results') html += Results.render();
  else if (route === '#calendar') html += Calendar.render();
  
  app.innerHTML = html;
  if (window.lucide) window.lucide.createIcons();
}
```

- [ ] **Step 3: Test dashboard page**

Verify welcome heading, 3 feature cards, and stats card render correctly.

- [ ] **Step 4: Commit**

```bash
git add app.js && git commit -m "feat: add dashboard home page"
```

---

## Task 4: Health Analysis Input Page

**Files:**
- Modify: `app.js` - Add Analysis object

- [ ] **Step 1: Add Analysis.render() with form**

```javascript
const Analysis = {
  formData: { age: '', state: '', periodStart: '', periodEnd: '', symptoms: '' },
  
  async loadStates() {
    try {
      const res = await fetch('/states');
      return await res.json();
    } catch { return []; }
  },
  
  render() {
    return `
      <div class="container" style="padding: 40px 40px">
        <h1 style="font-size:32px;font-weight:600;margin-bottom:8px">Health Analysis</h1>
        <p style="color:var(--text-secondary);margin-bottom:32px">Enter your symptoms for AI-powered health insights</p>
        
        <div class="card" style="max-width:600px">
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px">
            <div>
              <label style="display:block;margin-bottom:8px;font-size:14px;color:var(--text-secondary)">Age</label>
              <select id="analysis-age" style="width:100%;padding:12px;border-radius:var(--radius);background:var(--bg-primary);border:1px solid var(--border);color:var(--text-primary);font-size:14px">
                <option value="">Select age</option>
                ${[...Array(38)].map((_,i)=>`<option value="${i+18}">${i+18}</option>`).join('')}
              </select>
            </div>
            <div>
              <label style="display:block;margin-bottom:8px;font-size:14px;color:var(--text-secondary)">State</label>
              <select id="analysis-state" style="width:100%;padding:12px;border-radius:var(--radius);background:var(--bg-primary);border:1px solid var(--border);color:var(--text-primary);font-size:14px">
                <option value="">Select state</option>
              </select>
            </div>
          </div>
          
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;margin-bottom:20px">
            <div>
              <label style="display:block;margin-bottom:8px;font-size:14px;color:var(--text-secondary)">Period Start</label>
              <input type="date" id="analysis-period-start" style="width:100%;padding:12px;border-radius:var(--radius);background:var(--bg-primary);border:1px solid var(--border);color:var(--text-primary);font-size:14px">
            </div>
            <div>
              <label style="display:block;margin-bottom:8px;font-size:14px;color:var(--text-secondary)">Period End</label>
              <input type="date" id="analysis-period-end" style="width:100%;padding:12px;border-radius:var(--radius);background:var(--bg-primary);border:1px solid var(--border);color:var(--text-primary);font-size:14px">
            </div>
          </div>
          
          <div style="margin-bottom:24px">
            <label style="display:block;margin-bottom:8px;font-size:14px;color:var(--text-secondary)">Symptoms</label>
            <textarea id="analysis-symptoms" rows="4" placeholder="Describe your symptoms..." style="width:100%;padding:12px;border-radius:var(--radius);background:var(--bg-primary);border:1px solid var(--border);color:var(--text-primary);font-size:14px;resize:vertical;font-family:inherit"></textarea>
          </div>
          
          <div style="display:flex;gap:12px">
            <button class="btn btn-primary" onclick="Analysis.runAnalysis()">Run Analysis</button>
            <button class="btn btn-secondary" onclick="Analysis.loadDemo()">Load Demo</button>
          </div>
        </div>
      </div>
    `;
  },
  
  async init() {
    const states = await this.loadStates();
    const select = document.getElementById('analysis-state');
    if (select && states.length) {
      select.innerHTML = '<option value="">Select state</option>' + states.map(s => `<option value="${s}">${s}</option>`).join('');
    }
  },
  
  loadDemo() {
    document.getElementById('analysis-age').value = '25';
    document.getElementById('analysis-state').value = 'Maharashtra';
    document.getElementById('analysis-symptoms').value = 'Irregular periods, weight gain, excessive hair growth, acne, mood swings';
  },
  
  async runAnalysis() {
    const data = {
      age: document.getElementById('analysis-age').value,
      state: document.getElementById('analysis-state').value,
      period_start: document.getElementById('analysis-period-start').value,
      period_end: document.getElementById('analysis-period-end').value,
      symptoms: document.getElementById('analysis-symptoms').value,
    };
    
    if (!data.state || !data.symptoms) {
      alert('Please fill in required fields');
      return;
    }
    
    try {
      const res = await fetch('/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      const result = await res.json();
      Results.setData(result);
      window.location.hash = '#results';
    } catch (e) {
      alert('Analysis failed: ' + e.message);
    }
  }
};
```

- [ ] **Step 2: Update App.render() to call Analysis.init() after render**

```javascript
// After lucide.createIcons(), add:
if (route === '#analysis') setTimeout(() => Analysis.init(), 0);
```

- [ ] **Step 3: Add Results object placeholder**

```javascript
const Results = {
  data: null,
  setData(d) { this.data = d; },
  render() { return '<div>Results</div>'; }
};
```

- [ ] **Step 4: Test analysis page**

Verify form renders with all fields and dropdown populates with states.

- [ ] **Step 5: Commit**

```bash
git add app.js && git commit -m "feat: add health analysis input page"
```

---

## Task 5: Analysis Results Page

**Files:**
- Modify: `app.js` - Update Results object

- [ ] **Step 1: Add Results.render() with risk gauge**

```javascript
const Results = {
  data: null,
  setData(d) { this.data = d; },
  
  render() {
    if (!this.data) return '<div class="container"><p>No results. Run analysis first.</p></div>';
    
    const { top_risk, india_context, aqi, community_data, recommended_actions, lab_tests, government_schemes, analysis_summary } = this.data;
    const riskPercent = top_risk ? Math.round(top_risk.confidence) : 0;
    const riskLabel = top_risk ? `${top_risk.condition} – ${riskPercent > 60 ? 'High' : riskPercent > 40 ? 'Medium' : 'Low'} Risk` : 'No significant risk';
    
    return `
      <div class="container" style="padding: 40px 40px">
        <h1 style="font-size:32px;font-weight:600;margin-bottom:8px">Health Analysis Results</h1>
        <p style="color:var(--text-secondary);margin-bottom:32px">${analysis_summary}</p>
        
        <div style="display:flex;justify-content:center;margin-bottom:40px">
          <div style="text-align:center">
            <svg width="180" height="180" viewBox="0 0 180 180">
              <circle cx="90" cy="90" r="80" fill="none" stroke="var(--border)" stroke-width="12"/>
              <circle cx="90" cy="90" r="80" fill="none" stroke="var(--accent-red)" stroke-width="12" stroke-linecap="round" stroke-dasharray="${riskPercent * 5.024} 502.4" transform="rotate(-90 90 90)" style="transition:stroke-dasharray 1s ease"/>
            </svg>
            <div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);margin-top:-20px">
              <span style="font-size:36px;font-weight:700">${riskPercent}%</span>
            </div>
          </div>
        </div>
        <p style="text-align:center;font-size:18px;font-weight:600;color:var(--accent-red);margin-bottom:40px">${riskLabel}</p>
        
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:20px;margin-bottom:32px">
          <div class="card">
            <h3 style="font-size:16px;font-weight:600;margin-bottom:12px">India Context</h3>
            <ul style="color:var(--text-secondary);font-size:14px;list-style:disc;padding-left:20px">
              <li>Iron deficiency: ${india_context.iron_tips || 'Consume leafy greens, legumes'}</li>
              <li>Vitamin D: ${india_context.vitamin_d_tips || 'Sun exposure, fortified foods'}</li>
              <li>General: ${india_context.general_tips || 'Balanced diet, regular exercise'}</li>
            </ul>
          </div>
          <div class="card">
            <h3 style="font-size:16px;font-weight:600;margin-bottom:12px">Air Quality (${aqi.city})</h3>
            <div style="display:flex;align-items:center;gap:12px">
              <span style="font-size:24px;font-weight:700;color:${aqi.aqi < 50 ? 'var(--accent-green)' : aqi.aqi < 100 ? 'var(--warning)' : 'var(--accent-red)'}">${aqi.aqi}</span>
              <span style="color:var(--text-secondary);font-size:14px">AQI - ${aqi.status}</span>
            </div>
          </div>
          <div class="card">
            <h3 style="font-size:16px;font-weight:600;margin-bottom:12px">Community Data</h3>
            <p style="color:var(--text-secondary);font-size:14px;margin-bottom:8px">Prevalence in ${community_data.state}</p>
            <div style="background:var(--bg-primary);height:24px;border-radius:12px;overflow:hidden">
              <div style="width:${community_data.prevalence}%;height:100%;background:var(--accent-red)"></div>
            </div>
            <p style="font-size:12px;color:var(--text-secondary);margin-top:4px">${community_data.prevalence}% of women</p>
          </div>
          <div class="card">
            <h3 style="font-size:16px;font-weight:600;margin-bottom:12px">Research Gap</h3>
            <p style="color:var(--text-secondary);font-size:14px">Limited studies on ${top_risk?.condition || 'this condition'} in Indian women. More clinical trials needed.</p>
          </div>
        </div>
        
        ${lab_tests ? `
        <div class="card" style="margin-bottom:20px">
          <h3 style="font-size:16px;font-weight:600;margin-bottom:12px">Lab Test Recommendations</h3>
          <ul style="color:var(--text-secondary);font-size:14px;list-style:disc;padding-left:20px">
            <li>${lab_tests.recommended_test || 'Full hormone panel'}</li>
            <li>${lab_tests.alt_test || 'Ultrasound'}</li>
          </ul>
        </div>
        ` : ''}
        
        ${government_schemes?.length ? `
        <div class="card" style="margin-bottom:20px">
          <h3 style="font-size:16px;font-weight:600;margin-bottom:12px">Government Schemes</h3>
          <ul style="color:var(--text-secondary);font-size:14px;list-style:disc;padding-left:20px">
            ${government_schemes.map(s => `<li>${s}</li>`).join('')}
          </ul>
        </div>
        ` : ''}
        
        <div class="card" style="margin-bottom:20px">
          <h3 style="font-size:16px;font-weight:600;margin-bottom:12px">Recommended Actions</h3>
          <ul style="color:var(--text-primary);font-size:14px">
            ${recommended_actions.map(a => `<li style="margin-bottom:8px;display:flex;align-items:center;gap:8px"><i data-lucide="check-circle" style="color:var(--accent-green);width:16px;height:16px"></i>${a}</li>`).join('')}
          </ul>
        </div>
        
        <div style="background:rgba(245,158,11,0.1);border:1px solid var(--warning);border-radius:var(--radius);padding:16px;margin-top:32px">
          <p style="color:var(--warning);font-size:14px"><strong>Disclaimer:</strong> This is not a medical diagnosis. Please consult a healthcare professional for proper evaluation.</p>
        </div>
      </div>
    `;
  }
};
```

- [ ] **Step 2: Test results page with demo data**

- [ ] **Step 3: Commit**

```bash
git add app.js && git commit -m "feat: add analysis results page with risk gauge"
```

---

## Task 6: Calendar Page

**Files:**
- Modify: `app.js` - Add Calendar object

- [ ] **Step 1: Add Calendar.render()**

```javascript
const Calendar = {
  currentDate: new Date(),
  periods: [],
  
  async loadPeriods() {
    try {
      const res = await fetch('/periods');
      return await res.json();
    } catch { return []; }
  },
  
  render() {
    const year = this.currentDate.getFullYear();
    const month = this.currentDate.getMonth();
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const monthName = this.currentDate.toLocaleString('default', { month: 'long' });
    
    const days = [];
    for (let i = 0; i < firstDay; i++) days.push(null);
    for (let i = 1; i <= daysInMonth; i++) days.push(i);
    
    const periodDays = this.periods.flatMap(p => {
      const start = new Date(p.start_date);
      const end = new Date(p.end_date);
      const days = [];
      for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        if (d.getMonth() === month && d.getFullYear() === year) days.push(d.getDate());
      }
      return days;
    });
    
    return `
      <div class="container" style="padding: 40px 40px">
        <h1 style="font-size:32px;font-weight:600;margin-bottom:8px">Calendar</h1>
        <p style="color:var(--text-secondary);margin-bottom:32px">Track your menstrual cycle</p>
        
        <div class="card" style="margin-bottom:32px">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px">
            <button class="btn btn-secondary" style="padding:8px 12px" onclick="Calendar.prevMonth()">
              <i data-lucide="chevron-left" style="width:16px;height:16px"></i>
            </button>
            <h2 style="font-size:20px;font-weight:600">${monthName} ${year}</h2>
            <button class="btn btn-secondary" style="padding:8px 12px" onclick="Calendar.nextMonth()">
              <i data-lucide="chevron-right" style="width:16px;height:16px"></i>
            </button>
          </div>
          
          <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px;text-align:center;margin-bottom:8px">
            ${['Sun','Mon','Tue','Wed','Thu','Fri','Sat'].map(d => `<div style="font-size:12px;color:var(--text-secondary);padding:8px">${d}</div>`).join('')}
          </div>
          <div style="display:grid;grid-template-columns:repeat(7,1fr);gap:4px">
            ${days.map(day => {
              if (!day) return '<div></div>';
              const isPeriod = periodDays.includes(day);
              const isToday = day === new Date().getDate() && month === new Date().getMonth() && year === new Date().getFullYear();
              return `<div style="aspect-ratio:1;display:flex;align-items:center;justify-content:center;border-radius:8px;font-size:14px;${isPeriod ? 'background:rgba(255,107,107,0.2);color:var(--accent-red)' : isToday ? 'border:1px solid var(--accent-red)' : 'color:var(--text-primary)'}">${day}</div>`;
            }).join('')}
          </div>
        </div>
        
        <div class="card">
          <h3 style="font-size:18px;font-weight:600;margin-bottom:16px">Recent Periods</h3>
          ${this.periods.length ? this.periods.slice(0,5).map(p => `
            <div style="display:flex;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--border)">
              <span>${p.start_date} - ${p.end_date}</span>
              <span style="color:var(--text-secondary)">${p.flow_level || 'Medium'}</span>
            </div>
          `).join('') : '<p style="color:var(--text-secondary)">No periods logged yet</p>'}
          
          <button class="btn btn-primary" style="width:100%;margin-top:16px" onclick="App.openPeriodModal()">
            <i data-lucide="plus" style="width:16px;height:16px;margin-right:8px"></i>
            Add Period
          </button>
        </div>
      </div>
    `;
  },
  
  prevMonth() {
    this.currentDate.setMonth(this.currentDate.getMonth() - 1);
    this.refresh();
  },
  
  nextMonth() {
    this.currentDate.setMonth(this.currentDate.getMonth() + 1);
    this.refresh();
  },
  
  async refresh() {
    this.periods = await this.loadPeriods();
    window.location.hash = '#calendar';
  },
  
  async init() {
    this.periods = await this.loadPeriods();
  }
};
```

- [ ] **Step 2: Test calendar page**

- [ ] **Step 3: Commit**

```bash
git add app.js && git commit -m "feat: add calendar page with period tracking"
```

---

## Task 7: Log Period Modal

**Files:**
- Modify: `app.js` - Add modal functions to App

- [ ] **Step 1: Add modal styles**

```css
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: fadeIn 0.2s ease;
}
.modal-content {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 32px;
  width: 100%;
  max-width: 480px;
  box-shadow: var(--shadow-elevated);
  animation: scaleIn 0.2s ease;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes scaleIn { from { transform: scale(0.95); opacity: 0; } to { transform: scale(1); opacity: 1; } }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
.modal-title { font-size: 20px; font-weight: 600; }
.modal-close { background: none; border: none; color: var(--text-secondary); cursor: pointer; }
```

- [ ] **Step 2: Add App.openPeriodModal() and closePeriodModal()**

```javascript
openPeriodModal() {
  document.body.insertAdjacentHTML('beforeend', `
    <div id="period-modal" class="modal-overlay" onclick="if(event.target===this)App.closePeriodModal()">
      <div class="modal-content">
        <div class="modal-header">
          <h2 class="modal-title">Log Period</h2>
          <button class="modal-close" onclick="App.closePeriodModal()">
            <i data-lucide="x" style="width:20px;height:20px"></i>
          </button>
        </div>
        <div style="margin-bottom:20px">
          <label style="display:block;margin-bottom:8px;font-size:14px;color:var(--text-secondary)">Start Date</label>
          <input type="date" id="period-start" style="width:100%;padding:12px;border-radius:var(--radius);background:var(--bg-primary);border:1px solid var(--border);color:var(--text-primary);font-size:14px">
        </div>
        <div style="margin-bottom:20px">
          <label style="display:block;margin-bottom:8px;font-size:14px;color:var(--text-secondary)">End Date</label>
          <input type="date" id="period-end" style="width:100%;padding:12px;border-radius:var(--radius);background:var(--bg-primary);border:1px solid var(--border);color:var(--text-primary);font-size:14px">
        </div>
        <div style="margin-bottom:20px">
          <label style="display:block;margin-bottom:8px;font-size:14px;color:var(--text-secondary)">Flow Level</label>
          <select id="period-flow" style="width:100%;padding:12px;border-radius:var(--radius);background:var(--bg-primary);border:1px solid var(--border);color:var(--text-primary);font-size:14px">
            <option value="Light">Light</option>
            <option value="Medium" selected>Medium</option>
            <option value="Heavy">Heavy</option>
          </select>
        </div>
        <div style="margin-bottom:24px">
          <label style="display:block;margin-bottom:8px;font-size:14px;color:var(--text-secondary)">Symptoms (optional)</label>
          <textarea id="period-symptoms" rows="3" style="width:100%;padding:12px;border-radius:var(--radius);background:var(--bg-primary);border:1px solid var(--border);color:var(--text-primary);font-size:14px;resize:vertical;font-family:inherit"></textarea>
        </div>
        <div style="display:flex;gap:12px">
          <button class="btn btn-secondary" style="flex:1" onclick="App.closePeriodModal()">Cancel</button>
          <button class="btn btn-primary" style="flex:1" onclick="App.savePeriod()">Save</button>
        </div>
      </div>
    </div>
  `);
  if (window.lucide) window.lucide.createIcons();
},

closePeriodModal() {
  document.getElementById('period-modal')?.remove();
},

async savePeriod() {
  const data = {
    start_date: document.getElementById('period-start').value,
    end_date: document.getElementById('period-end').value,
    flow_level: document.getElementById('period-flow').value,
    symptoms: document.getElementById('period-symptoms').value,
  };
  
  if (!data.start_date || !data.end_date) {
    alert('Please fill in start and end dates');
    return;
  }
  
  try {
    await fetch('/periods', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    this.closePeriodModal();
    window.location.hash = '#calendar';
  } catch (e) {
    alert('Failed to save: ' + e.message);
  }
},
```

- [ ] **Step 3: Test modal open/close and save**

- [ ] **Step 4: Commit**

```bash
git add app.js && git commit -m "feat: add log period modal"
```

---

## Task 8: API Integration & Auth

**Files:**
- Modify: `app.js` - Add auth handling

- [ ] **Step 1: Add auth functions**

```javascript
const Auth = {
  token: localStorage.getItem('token'),
  
  async login(email, password) {
    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
    if (!res.ok) throw new Error('Login failed');
    const data = await res.json();
    this.token = data.access_token;
    localStorage.setItem('token', data.access_token);
  },
  
  logout() {
    this.token = null;
    localStorage.removeItem('token');
    window.location.hash = '#login';
  },
  
  async getMe() {
    if (!this.token) return null;
    const res = await fetch('/auth/me', {
      headers: { 'Authorization': `Bearer ${this.token}` },
    });
    if (!res.ok) return null;
    return await res.json();
  }
};
```

- [ ] **Step 2: Update fetch calls to include auth header**

Add to Analysis.runAnalysis, Calendar.loadPeriods, App.savePeriod:
```javascript
headers: { ..., 'Authorization': `Bearer ${Auth.token}` }
```

- [ ] **Step 3: Add logout to App**

```javascript
logout() {
  Auth.logout();
}
```

- [ ] **Step 4: Test with backend running**

Verify all API calls work with auth.

- [ ] **Step 5: Commit**

```bash
git add app.js && git commit -m "feat: add API authentication"
```

---

## Task 9: Polish & Responsive

**Files:**
- Modify: `index.html` - Add responsive CSS

- [ ] **Step 1: Add responsive styles**

```css
@media (max-width: 768px) {
  .container { padding: 0 20px !important; }
  .navbar .container { padding: 0 20px !important; }
  .nav-center { display: none !important; }
  .card { padding: 16px !important; }
  h1 { font-size: 24px !important; }
  .feature-cards { grid-template-columns: 1fr !important; }
  .insights-grid { grid-template-columns: 1fr !important; }
}
```

- [ ] **Step 2: Add hover effects to cards**

```css
.card:hover { transform: translateY(-2px); box-shadow: var(--shadow-elevated); }
```

- [ ] **Step 3: Final testing**

Verify all pages work, responsive design, no console errors.

- [ ] **Step 4: Commit**

```bash
git add index.html app.js && git commit -m "feat: add responsive styles and polish"
```

---

## Verification

- [ ] All 5 pages render correctly
- [ ] Navigation between pages works
- [ ] API calls succeed with backend
- [ ] Modal opens/closes properly
- [ ] Calendar shows period days
- [ ] Risk gauge animates
- [ ] Mobile responsive
- [ ] No console errors