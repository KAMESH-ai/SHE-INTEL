const isLocalHost = ['localhost', '127.0.0.1'].includes(window.location.hostname);
const API_URL = window.SHE_INTEL_API_URL
  || localStorage.getItem('she_intel_api_url')
  || (isLocalHost ? 'http://localhost:8002' : window.location.origin);

// Toast notification system
function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const icons = { success: '✓', error: '✕', warning: '⚠' };
  toast.innerHTML = `
    <span style="font-size: 1.1rem;">${icons[type] || '•'}</span>
    <span>${escapeHtml(message)}</span>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

// Button loading state
function setButtonLoading(button, loading) {
  const btn = button.closest('button');
  if (!btn) return;

  if (loading) {
    btn.classList.add('loading');
    btn.disabled = true;
    const text = btn.querySelector('.btn-text');
    if (text) {
      btn.dataset.originalText = text.textContent;
      text.innerHTML = '<span class="btn-spinner"></span>';
    }
  } else {
    btn.classList.remove('loading');
    btn.disabled = false;
    const text = btn.querySelector('.btn-text');
    if (text && btn.dataset.originalText) {
      text.textContent = btn.dataset.originalText;
    }
  }
}

// Character counter setup
function setupCharCounters() {
  const counters = [
    { input: 'symptom-desc', counter: 'symptom-desc-counter', max: 2000 },
    { input: 'analyze-desc', counter: 'analyze-desc-counter', max: 2000 },
    { input: 'period-symptoms', counter: 'period-symptoms-counter', max: 1000 }
  ];

  counters.forEach(({ input, counter, max }) => {
    const inputEl = document.getElementById(input);
    const counterEl = document.getElementById(counter);
    if (inputEl && counterEl) {
      const update = () => {
        const len = inputEl.value.length;
        counterEl.textContent = `${len} / ${max}`;
        counterEl.className = 'char-counter';
        if (len > max * 0.9) counterEl.classList.add('warning');
        if (len >= max) counterEl.classList.add('error');
      };
      inputEl.addEventListener('input', update);
      update();
    }
  });
}

// Tab keyboard navigation
function setupTabNavigation() {
  document.querySelectorAll('.sidebar-item').forEach(item => {
    item.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        const tab = item.dataset.tab;
        if (tab) setTab(tab);
      }
    });
  });
}

let currentTab = 'overview';
let userData = null;

function escapeHtml(value) {
  return String(value ?? '')
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

// Theme toggle
function toggleTheme() {
  const html = document.documentElement;
  const btn = document.getElementById('theme-toggle');
  const currentTheme = html.getAttribute('data-theme');
  const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

  html.setAttribute('data-theme', newTheme);
  localStorage.setItem('theme', newTheme);
  btn.textContent = newTheme === 'dark' ? '☀️' : '🌙';
}

function loadTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  const btn = document.getElementById('theme-toggle');
  if (btn) btn.textContent = saved === 'dark' ? '☀️' : '🌙';
}

async function parseApiError(res, fallbackMessage) {
  try {
    const payload = await res.json();
    if (Array.isArray(payload?.detail)) {
      return payload.detail.map(item => item.msg).join(', ');
    }
    return payload?.detail || fallbackMessage;
  } catch (err) {
    return fallbackMessage;
  }
}

async function apiRequest(endpoint, options = {}, fallbackMessage = 'API error') {
  const headers = {
    ...(window.token ? { Authorization: `Bearer ${window.token}` } : {}),
    ...(options.headers || {})
  };

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers
  });

  if (!response.ok) {
    if (response.status === 401 && window.token) {
      logout();
      throw new Error('Session expired. Please sign in again.');
    }
    throw new Error(await parseApiError(response, fallbackMessage));
  }

  return response.json();
}

// Utils
function showPage(page) {
  document.querySelectorAll('.page').forEach(p => {
    p.classList.add('hidden');
    p.classList.remove('visible');
  });

  const target = document.getElementById(`${page}-page`);
  if (target) {
    target.classList.remove('hidden');
    // Trigger animation
    requestAnimationFrame(() => {
      target.classList.add('visible');
    });
  }
}

function setTab(tab) {
  currentTab = tab;
  document.querySelectorAll('.sidebar-item').forEach(item => {
    item.classList.toggle('active', item.dataset.tab === tab);
  });
  document.querySelectorAll('.tab-content').forEach(content => {
    content.classList.add('hidden');
  });
  document.getElementById(`tab-${tab}`).classList.remove('hidden');

  if (tab === 'overview') loadOverview();
  if (tab === 'periods') loadPeriods();
  if (tab === 'symptoms') loadSymptoms();
  if (tab === 'history') loadHistory();
}

function showError(elementId, message) {
  const el = document.getElementById(elementId);
  el.textContent = message;
  el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 4000);
}

function getToken() {
  return localStorage.getItem('token');
}

function setAuthHeader() {
  const token = getToken();
  if (token) {
    window.token = token;
  }
}

// Auth
async function login(email, password) {
  const data = await apiRequest('/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password })
  }, 'Login failed');
  localStorage.setItem('token', data.access_token);
  window.token = data.access_token;
  return data;
}

async function register(data) {
  return apiRequest('/auth/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }, 'Registration failed');
}

async function fetchUser() {
  return apiRequest('/auth/me', {}, 'Failed to fetch user');
}

function logout() {
  localStorage.removeItem('token');
  window.token = null;
  showPage('login');
}

// API Calls
async function apiGet(endpoint) {
  return apiRequest(endpoint, {}, 'Failed to load data');
}

async function apiPost(endpoint, data) {
  return apiRequest(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  }, 'Failed to submit data');
}

// Dashboard Functions
async function loadOverview() {
  // Show skeletons initially
  const cycleSkeleton = document.getElementById('cycle-skeleton');
  const cycleContent = document.getElementById('cycle-content');
  const symptomsSkeleton = document.getElementById('symptoms-skeleton');
  const symptomsContent = document.getElementById('symptoms-content');

  if (cycleSkeleton) cycleSkeleton.style.display = 'block';
  if (cycleContent) cycleContent.classList.add('hidden');
  if (symptomsSkeleton) symptomsSkeleton.style.display = 'block';
  if (symptomsContent) symptomsContent.classList.add('hidden');

  try {
    const [periodsRes, symptomsRes, calendarRes] = await Promise.all([
      apiGet('/periods/'),
      apiGet('/symptoms/'),
      apiGet('/periods/calendar')
    ]);

    // Hide skeletons, show content
    if (cycleSkeleton) cycleSkeleton.style.display = 'none';
    if (cycleContent) cycleContent.classList.remove('hidden');
    if (symptomsSkeleton) symptomsSkeleton.style.display = 'none';
    if (symptomsContent) symptomsContent.classList.remove('hidden');

    document.getElementById('symptom-count').textContent = symptomsRes.length;

    if (calendarRes.prediction) {
      document.getElementById('avg-cycle').textContent = calendarRes.prediction.avg_cycle_length;
      document.getElementById('next-period-box').classList.remove('hidden');
      const nextDate = new Date(calendarRes.prediction.next_period_estimate);
      document.getElementById('next-date').textContent = nextDate.toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short'
      });
    } else {
      document.getElementById('avg-cycle').textContent = '--';
    }

    renderCalendar(periodsRes);
  } catch (err) {
    console.error('Error loading overview:', err);
    // Still hide skeletons on error
    if (cycleSkeleton) cycleSkeleton.style.display = 'none';
    if (cycleContent) cycleContent.classList.remove('hidden');
    if (symptomsSkeleton) symptomsSkeleton.style.display = 'none';
    if (symptomsContent) symptomsContent.classList.remove('hidden');
  }
}

function renderCalendar(periods) {
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth();
  const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'];

  document.getElementById('current-month').textContent = `${monthNames[month]} ${year}`;

  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();

  let html = '<div class="calendar-day-header">Sun</div>';
  html += '<div class="calendar-day-header">Mon</div>';
  html += '<div class="calendar-day-header">Tue</div>';
  html += '<div class="calendar-day-header">Wed</div>';
  html += '<div class="calendar-day-header">Thu</div>';
  html += '<div class="calendar-day-header">Fri</div>';
  html += '<div class="calendar-day-header">Sat</div>';

  for (let i = 0; i < firstDay; i++) {
    html += '<div class="calendar-day empty"></div>';
  }

  for (let day = 1; day <= daysInMonth; day++) {
    const current = new Date(year, month, day);
    const isToday = day === today.getDate();
    const isPeriod = periods.some(p => {
      const start = new Date(p.start_date);
      const end = p.end_date ? new Date(p.end_date) : start;
      return current >= start && current <= end;
    });

    let classes = 'calendar-day';
    if (isPeriod) classes += ' period';
    if (isToday) classes += ' today';

    html += `<div class="${classes}">${day}</div>`;
  }

  document.getElementById('calendar').innerHTML = html;
}

async function loadPeriods() {
  try {
    const periods = await apiGet('/periods/');
    renderPeriodHistory(periods);
  } catch (err) {
    console.error('Error:', err);
  }
}

function renderPeriodHistory(periods) {
  if (!periods.length) {
    document.getElementById('period-history').innerHTML = '<div class="empty-state"><p>No periods logged</p></div>';
    return;
  }

  let html = '';
  periods.forEach(p => {
    const start = new Date(p.start_date).toLocaleDateString('en-IN');
    html += `
      <div class="history-item">
        <div class="history-item-header">
          <span class="history-risk">${start}</span>
          <span class="history-score">${p.flow_level || 'N/A'}</span>
        </div>
        ${p.symptoms ? `<p class="history-note">${escapeHtml(p.symptoms)}</p>` : ''}
      </div>
    `;
  });
  document.getElementById('period-history').innerHTML = html;
}

async function loadSymptoms() {
  try {
    const symptoms = await apiGet('/symptoms/');
    renderSymptomHistory(symptoms);
  } catch (err) {
    console.error('Error:', err);
  }
}

function renderSymptomHistory(symptoms) {
  if (!symptoms.length) {
    document.getElementById('symptom-history').innerHTML = '<div class="empty-state"><p>No symptoms logged</p></div>';
    return;
  }

  let html = '';
  symptoms.slice(0, 10).forEach(s => {
    const date = new Date(s.date).toLocaleDateString('en-IN');
    html += `
      <div class="history-item">
        <div class="history-risk" style="font-size:0.9rem">${escapeHtml(s.description.substring(0, 60))}${s.description.length > 60 ? '...' : ''}</div>
        <div style="display:flex;gap:0.75rem;margin-top:0.35rem;font-size:0.8rem;color:var(--text-secondary)">
          <span>⚡ ${s.fatigue_level}/10</span>
          <span>😴 ${s.sleep_quality}/10</span>
          <span>${escapeHtml(s.mood || '')}</span>
        </div>
        <div class="history-date">${date}</div>
      </div>
    `;
  });
  document.getElementById('symptom-history').innerHTML = html;
}

async function loadHistory() {
  try {
    const history = await apiGet('/analysis/history');
    renderAnalysisHistory(history);
  } catch (err) {
    console.error('Error:', err);
  }
}

function renderAnalysisHistory(history) {
  if (!history.length) {
    document.getElementById('history-list').innerHTML = '<div class="empty-state"><p>No analysis history</p></div>';
    return;
  }

  let html = '';
  history.forEach(h => {
    const date = new Date(h.date).toLocaleDateString('en-IN');
    html += `
      <div class="history-item">
        <div class="history-item-header">
          <span class="history-risk">${escapeHtml(h.risk_type.replace(/_/g, ' '))}</span>
          <span class="history-score">${Math.round(h.confidence_score * 100)}%</span>
        </div>
        <p class="history-note">${escapeHtml(h.baseline_deviation)}</p>
        <div class="history-date">${date}</div>
      </div>
    `;
  });
  document.getElementById('history-list').innerHTML = html;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
  // Initialize new features
  setupCharCounters();
  setupTabNavigation();
  loadTheme();

  const token = getToken();
  if (token) {
    window.token = token;
    fetchUser().then(user => {
      userData = user;
      document.getElementById('user-name').textContent = user.name;
      showPage('dashboard');
      loadOverview();
    }).catch(() => logout());
  } else {
    showPage('login');
  }
});

// Login Form
document.getElementById('login-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = e.target.querySelector('button');
  setButtonLoading(btn, true);

  try {
    await login(
      document.getElementById('login-email').value,
      document.getElementById('login-password').value
    );
    userData = await fetchUser();
    document.getElementById('user-name').textContent = userData.name;
    showPage('dashboard');
    loadOverview();
    showToast('Welcome back!', 'success');
  } catch (err) {
    showError('login-error', err.message);
    showToast(err.message, 'error');
  } finally {
    setButtonLoading(btn, false);
  }
});

// Register Form
document.getElementById('register-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = e.target.querySelector('button');
  setButtonLoading(btn, true);

  try {
    const data = {
      name: document.getElementById('reg-name').value,
      email: document.getElementById('reg-email').value,
      password: document.getElementById('reg-password').value,
      age: document.getElementById('reg-age').value ? parseInt(document.getElementById('reg-age').value) : null,
      state: document.getElementById('reg-state').value || null
    };
    await register(data);
    await login(data.email, data.password);
    userData = await fetchUser();
    document.getElementById('user-name').textContent = userData.name;
    showPage('dashboard');
    loadOverview();
    showToast('Account created! Welcome!', 'success');
  } catch (err) {
    showError('register-error', err.message);
    showToast(err.message, 'error');
  } finally {
    setButtonLoading(btn, false);
  }
});

// Period Form
document.getElementById('period-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = e.target.querySelector('button');
  const startDate = document.getElementById('period-start').value;
  const endDate = document.getElementById('period-end').value;

  // Validate
  if (endDate && new Date(endDate) < new Date(startDate)) {
    showToast('End date must be after start date', 'error');
    return;
  }

  setButtonLoading(btn, true);

  try {
    await apiPost('/periods/', {
      start_date: startDate,
      end_date: endDate || null,
      flow_level: document.getElementById('period-flow').value || null,
      symptoms: document.getElementById('period-symptoms').value || null
    });
    e.target.reset();
    loadPeriods();
    loadOverview();
    showToast('Period logged successfully!', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    setButtonLoading(btn, false);
  }
});

// Symptom Form
document.getElementById('symptom-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = e.target.querySelector('button');
  setButtonLoading(btn, true);

  try {
    await apiPost('/symptoms/', {
      description: document.getElementById('symptom-desc').value,
      fatigue_level: parseInt(document.getElementById('symptom-fatigue').value),
      sleep_quality: parseInt(document.getElementById('symptom-sleep').value),
      mood: document.getElementById('symptom-mood').value || null
    });
    e.target.reset();
    document.getElementById('symptom-fatigue').value = '5';
    document.getElementById('symptom-sleep').value = '5';
    document.getElementById('fatigue-val').textContent = '5';
    document.getElementById('sleep-val').textContent = '5';
    loadSymptoms();
    loadOverview();
    showToast('Symptoms logged!', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    setButtonLoading(btn, false);
  }
});

// Analyze Form
document.getElementById('analyze-form').addEventListener('submit', async (e) => {
  e.preventDefault();
  const btn = e.target.querySelector('button');
  const resultDiv = document.getElementById('analysis-result');

  setButtonLoading(btn, true);
  resultDiv.innerHTML = '<div class="loading-container"><div class="loader"></div><p>Analyzing...</p></div>';

  try {
    const data = {
      description: document.getElementById('analyze-desc').value,
      fatigue_level: parseInt(document.getElementById('analyze-fatigue').value),
      sleep_quality: parseInt(document.getElementById('analyze-sleep').value)
    };

    const result = await apiPost('/analysis/analyze', data);
    renderAnalysisResult(result);
    showToast('Analysis complete!', 'success');
  } catch (err) {
    resultDiv.innerHTML = `<div class="error-msg">${escapeHtml(err.message)}</div>`;
    showToast(err.message, 'error');
  } finally {
    setButtonLoading(btn, false);
  }
});

function renderAnalysisResult(result) {
  const percent = Math.round(result.confidence_score * 100);
  const riskClass = result.confidence_label === 'high' ? 'risk-high' : result.confidence_label === 'medium' ? 'risk-medium' : 'risk-low';
  const circumference = 2 * Math.PI * 65;
  const offset = circumference * (1 - result.confidence_score);

  const aqi = result.aqi_enrichment || {};
  const schemes = Array.isArray(result.government_schemes) ? result.government_schemes : [];
  const labEstimates = Array.isArray(result.lab_test_cost_estimates) ? result.lab_test_cost_estimates : [];
  const metrics = result.model_metrics || {};

  const safeRiskType = escapeHtml(result.risk_type.replace(/_/g, ' '));
  const safeConfidenceLabel = escapeHtml(result.confidence_label);
  const accuracy = Number.isFinite(metrics.accuracy) ? `${(metrics.accuracy * 100).toFixed(1)}%` : 'N/A';
  const macroF1 = Number.isFinite(metrics.macro_f1) ? `${(metrics.macro_f1 * 100).toFixed(1)}%` : 'N/A';

  let html = `
    <div class="result-card">
      <div class="risk-gauge">
        <svg viewBox="0 0 160 160">
          <circle cx="80" cy="80" r="65" class="ring ring-bg" />
          <circle cx="80" cy="80" r="65" class="ring ring-progress ${riskClass}" stroke-dasharray="${circumference}" stroke-dashoffset="${offset}" />
        </svg>
        <div class="ring-text">
          <div class="ring-value">${percent}%</div>
          <div class="ring-label">${safeConfidenceLabel} risk</div>
        </div>
      </div>
      <div class="risk-type">${safeRiskType}</div>
  `;

  if (result.baseline_deviation) {
    html += `
      <div class="context-section">
        <div class="context-title">📊 Your Baseline</div>
        <div class="context-text">${escapeHtml(result.baseline_deviation)}</div>
      </div>
    `;
  }

  if (result.india_context) {
    html += `
      <div class="context-section">
        <div class="context-title">🇮🇳 India Context</div>
        <div class="context-text">${escapeHtml(result.india_context)}</div>
      </div>
    `;
  }

  if (result.recommendations && result.recommendations.length) {
    html += `
      <div class="context-section">
        <div class="context-title">💊 Recommendations</div>
        <div class="context-text">
          ${result.recommendations.map(r => `• ${escapeHtml(r)}`).join('<br>')}
        </div>
      </div>
    `;
  }

  if (result.diet_recommendations && result.diet_recommendations.length) {
    html += `
      <div class="context-section">
        <div class="context-title">🥗 Diet</div>
        <div>${result.diet_recommendations.map(f => `<span class="tag tag-success">${escapeHtml(f)}</span>`).join('')}</div>
      </div>
    `;
  }

  if (aqi.city) {
    html += `
      <div class="context-section">
        <div class="context-title">🌫️ AQI Enrichment</div>
        <div class="context-text">
          <strong>${escapeHtml(aqi.city)}</strong>: ${aqi.aqi_value ?? 'N/A'} (${escapeHtml(aqi.aqi_category || 'unknown')})
          ${aqi.pm2_5 ? `<br>PM2.5: ${escapeHtml(aqi.pm2_5)}` : ''}
          ${aqi.advisory ? `<br>${escapeHtml(aqi.advisory)}` : ''}
        </div>
      </div>
    `;
  }

  if (schemes.length) {
    html += `
      <div class="context-section">
        <div class="context-title">🏥 Government Schemes</div>
        <div class="context-text">${schemes.map(s => `• ${escapeHtml(s)}`).join('<br>')}</div>
      </div>
    `;
  }

  if (labEstimates.length) {
    html += `
      <div class="context-section">
        <div class="context-title">🧪 Lab Cost Estimates</div>
        <div class="context-text">
          ${labEstimates.map(item => `• ${escapeHtml(item.test)}: Rs ${item.estimated_low_inr} - Rs ${item.estimated_high_inr} (${escapeHtml(item.city)})`).join('<br>')}
        </div>
      </div>
    `;
  }

  if (result.bias_awareness) {
    html += `
      <div class="context-section">
        <div class="context-title">⚖️ Bias Awareness</div>
        <div class="context-text">${escapeHtml(result.bias_awareness)}</div>
      </div>
    `;
  }

  if (Number.isFinite(metrics.accuracy) || Number.isFinite(metrics.macro_f1)) {
    html += `
      <div class="context-section">
        <div class="context-title">📈 Model Metrics</div>
        <div class="context-text">
          Accuracy: ${accuracy}
          <br>Macro F1: ${macroF1}
        </div>
      </div>
    `;
  }

  html += `<div class="disclaimer">⚠️ ${escapeHtml(result.medical_disclaimer)}</div>`;
  html += '</div>';

  document.getElementById('analysis-result').innerHTML = html;
}
