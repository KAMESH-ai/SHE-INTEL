const Dashboard = {
    render() {
        return `
            <div style="padding: 40px;">
                <h1 style="font-size: 32px; font-weight: 600; margin-bottom: 8px;">Welcome, Demo User</h1>
                <p style="color: var(--text-secondary); margin-bottom: 32px;">Your health dashboard at a glance</p>
                
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin-bottom: 32px;">
                    <div class="card" style="cursor: pointer; transition: all 0.2s;" onclick="window.location.hash='#calendar'">
                        <i data-lucide="calendar" style="width:32px;height:32px;color:var(--accent-red);margin-bottom:12px"></i>
                        <h3 style="font-size:18px;font-weight:600;margin-bottom:4px;">Calendar</h3>
                        <p style="color:var(--text-secondary);font-size:14px;">View your cycles</p>
                    </div>
                    <div class="card" style="cursor: pointer; transition: all 0.2s;" onclick="window.location.hash='#analysis'">
                        <i data-lucide="activity" style="width:32px;height:32px;color:var(--accent-red);margin-bottom:12px"></i>
                        <h3 style="font-size:18px;font-weight:600;margin-bottom:4px;">Health Analysis</h3>
                        <p style="color:var(--text-secondary);font-size:14px;">Run AI analysis</p>
                    </div>
                    <div class="card" style="cursor: pointer; transition: all 0.2s;" onclick="window.location.hash='#calendar'">
                        <i data-lucide="heart" style="width:32px;height:32px;color:var(--accent-red);margin-bottom:12px"></i>
                        <h3 style="font-size:18px;font-weight:600;margin-bottom:4px;">Log Period</h3>
                        <p style="color:var(--text-secondary);font-size:14px;">Track your period</p>
                    </div>
                </div>
                
                <div class="card" style="max-width: 300px;">
                    <h3 style="font-size:14px;color:var(--text-secondary);margin-bottom:8px;">Periods Logged</h3>
                    <div style="font-size: 36px; font-weight: 700; color: var(--accent-green); margin-bottom: 8px;">12</div>
                    <p style="font-size:14px;color:var(--text-secondary);">Total tracked cycles</p>
                </div>
            </div>
        `;
    }
};

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
            <div style="padding: 40px;">
                <h1 style="font-size: 32px; font-weight: 600; margin-bottom: 8px;">Health Analysis</h1>
                <p style="color: var(--text-secondary); margin-bottom: 32px;">Enter your symptoms for AI-powered health insights</p>
                
                <div class="card" style="max-width: 600px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                        <div>
                            <label style="display: block; margin-bottom: 8px; font-size: 14px; color: var(--text-secondary);">Age</label>
                            <select id="analysis-age" style="width: 100%; padding: 12px; border-radius: var(--radius); background: var(--bg-primary); border: 1px solid var(--border); color: var(--text-primary); font-size: 14px;">
                                <option value="">Select age</option>
                                ${[...Array(38)].map((_, i) => `<option value="${i + 18}">${i + 18}</option>`).join('')}
                            </select>
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 8px; font-size: 14px; color: var(--text-secondary);">State</label>
                            <select id="analysis-state" style="width: 100%; padding: 12px; border-radius: var(--radius); background: var(--bg-primary); border: 1px solid var(--border); color: var(--text-primary); font-size: 14px;">
                                <option value="">Select state</option>
                            </select>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
                        <div>
                            <label style="display: block; margin-bottom: 8px; font-size: 14px; color: var(--text-secondary);">Period Start</label>
                            <input type="date" id="analysis-period-start" style="width: 100%; padding: 12px; border-radius: var(--radius); background: var(--bg-primary); border: 1px solid var(--border); color: var(--text-primary); font-size: 14px;">
                        </div>
                        <div>
                            <label style="display: block; margin-bottom: 8px; font-size: 14px; color: var(--text-secondary);">Period End</label>
                            <input type="date" id="analysis-period-end" style="width: 100%; padding: 12px; border-radius: var(--radius); background: var(--bg-primary); border: 1px solid var(--border); color: var(--text-primary); font-size: 14px;">
                        </div>
                    </div>
                    
                    <div style="margin-bottom: 24px;">
                        <label style="display: block; margin-bottom: 8px; font-size: 14px; color: var(--text-secondary);">Symptoms</label>
                        <textarea id="analysis-symptoms" rows="4" placeholder="Describe your symptoms..." style="width: 100%; padding: 12px; border-radius: var(--radius); background: var(--bg-primary); border: 1px solid var(--border); color: var(--text-primary); font-size: 14px; resize: vertical; font-family: inherit;"></textarea>
                    </div>
                    
                    <div style="display: flex; gap: 12px;">
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

const Results = {
    data: null,
    setData(d) { this.data = d; },
    
    render() {
        if (!this.data) return '<div style="padding:40px"><p>No results. Run analysis first.</p></div>';
        
        const { top_risk, india_context, aqi, community_data, recommended_actions, lab_tests, government_schemes, analysis_summary } = this.data;
        const riskPercent = top_risk ? Math.round(top_risk.confidence) : 0;
        const riskLabel = top_risk ? `${top_risk.condition} – ${riskPercent > 60 ? 'High' : riskPercent > 40 ? 'Medium' : 'Low'} Risk` : 'No significant risk';
        
        return `
            <div style="padding: 40px;">
                <h1 style="font-size: 32px; font-weight: 600; margin-bottom: 8px;">Health Analysis Results</h1>
                <p style="color: var(--text-secondary); margin-bottom: 32px;">${analysis_summary}</p>
                
                <div style="display: flex; justify-content: center; margin-bottom: 40px;">
                    <div style="position: relative; width: 180px; height: 180px;">
                        <svg width="180" height="180" viewBox="0 0 180 180">
                            <circle cx="90" cy="90" r="80" fill="none" stroke="var(--border)" stroke-width="12"/>
                            <circle cx="90" cy="90" r="80" fill="none" stroke="var(--accent-red)" stroke-width="12" stroke-linecap="round" stroke-dasharray="${riskPercent * 5.024} 502.4" transform="rotate(-90 90 90)" style="transition: stroke-dasharray 1s ease"/>
                        </svg>
                        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                            <span style="font-size: 36px; font-weight: 700;">${riskPercent}%</span>
                        </div>
                    </div>
                </div>
                <p style="text-align: center; font-size: 18px; font-weight: 600; color: var(--accent-red); margin-bottom: 40px;">${riskLabel}</p>
                
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 32px;">
                    <div class="card">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">India Context</h3>
                        <ul style="color: var(--text-secondary); font-size: 14px; list-style: disc; padding-left: 20px;">
                            <li>Iron deficiency: ${india_context.iron_tips || 'Consume leafy greens, legumes'}</li>
                            <li>Vitamin D: ${india_context.vitamin_d_tips || 'Sun exposure, fortified foods'}</li>
                            <li>General: ${india_context.general_tips || 'Balanced diet, regular exercise'}</li>
                        </ul>
                    </div>
                    <div class="card">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Air Quality (${aqi.city})</h3>
                        <div style="display: flex; align-items: center; gap: 12px;">
                            <span style="font-size: 24px; font-weight: 700; color: ${aqi.aqi < 50 ? 'var(--accent-green)' : aqi.aqi < 100 ? 'var(--warning)' : 'var(--accent-red)'}">${aqi.aqi}</span>
                            <span style="color: var(--text-secondary); font-size: 14px;">AQI - ${aqi.status}</span>
                        </div>
                    </div>
                    <div class="card">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Community Data</h3>
                        <p style="color: var(--text-secondary); font-size: 14px; margin-bottom: 8px;">Prevalence in ${community_data.state}</p>
                        <div style="background: var(--bg-primary); height: 24px; border-radius: 12px; overflow: hidden;">
                            <div style="width: ${community_data.prevalence}%; height: 100%; background: var(--accent-red);"></div>
                        </div>
                        <p style="font-size: 12px; color: var(--text-secondary); margin-top: 4px;">${community_data.prevalence}% of women</p>
                    </div>
                    <div class="card">
                        <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Research Gap</h3>
                        <p style="color: var(--text-secondary); font-size: 14px;">Limited studies on ${top_risk?.condition || 'this condition'} in Indian women. More clinical trials needed.</p>
                    </div>
                </div>
                
                ${lab_tests ? `
                <div class="card" style="margin-bottom: 20px;">
                    <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Lab Test Recommendations</h3>
                    <ul style="color: var(--text-secondary); font-size: 14px; list-style: disc; padding-left: 20px;">
                        <li>${lab_tests.recommended_test || 'Full hormone panel'}</li>
                        <li>${lab_tests.alt_test || 'Ultrasound'}</li>
                    </ul>
                </div>
                ` : ''}
                
                ${government_schemes?.length ? `
                <div class="card" style="margin-bottom: 20px;">
                    <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Government Schemes</h3>
                    <ul style="color: var(--text-secondary); font-size: 14px; list-style: disc; padding-left: 20px;">
                        ${government_schemes.map(s => `<li>${s}</li>`).join('')}
                    </ul>
                </div>
                ` : ''}
                
                <div class="card" style="margin-bottom: 20px;">
                    <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 12px;">Recommended Actions</h3>
                    <ul style="color: var(--text-primary); font-size: 14px;">
                        ${recommended_actions.map(a => `<li style="margin-bottom: 8px; display: flex; align-items: center; gap: 8px;"><i data-lucide="check-circle" style="color: var(--accent-green); width: 16px; height: 16px;"></i>${a}</li>`).join('')}
                    </ul>
                </div>
                
                <div style="background: rgba(245, 158, 11, 0.1); border: 1px solid var(--warning); border-radius: var(--radius); padding: 16px; margin-top: 32px;">
                    <p style="color: var(--warning); font-size: 14px;"><strong>Disclaimer:</strong> This is not a medical diagnosis. Please consult a healthcare professional for proper evaluation.</p>
                </div>
            </div>
        `;
    }
};

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
            <div style="padding: 40px;">
                <h1 style="font-size: 32px; font-weight: 600; margin-bottom: 8px;">Calendar</h1>
                <p style="color: var(--text-secondary); margin-bottom: 32px;">Track your menstrual cycle</p>
                
                <div class="card" style="margin-bottom: 32px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <button class="btn btn-secondary" style="padding: 8px 12px;" onclick="Calendar.prevMonth()">
                            <i data-lucide="chevron-left" style="width: 16px; height: 16px;"></i>
                        </button>
                        <h2 style="font-size: 20px; font-weight: 600;">${monthName} ${year}</h2>
                        <button class="btn btn-secondary" style="padding: 8px 12px;" onclick="Calendar.nextMonth()">
                            <i data-lucide="chevron-right" style="width: 16px; height: 16px;"></i>
                        </button>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px; text-align: center; margin-bottom: 8px;">
                        ${['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(d => `<div style="font-size: 12px; color: var(--text-secondary); padding: 8px;">${d}</div>`).join('')}
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px;">
                        ${days.map(day => {
                            if (!day) return '<div></div>';
                            const isPeriod = periodDays.includes(day);
                            const isToday = day === new Date().getDate() && month === new Date().getMonth() && year === new Date().getFullYear();
                            return `<div style="aspect-ratio: 1; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-size: 14px; ${isPeriod ? 'background: rgba(255, 107, 107, 0.2); color: var(--accent-red)' : isToday ? 'border: 1px solid var(--accent-red)' : 'color: var(--text-primary)'}">${day}</div>`;
                        }).join('')}
                    </div>
                </div>
                
                <div class="card">
                    <h3 style="font-size: 18px; font-weight: 600; margin-bottom: 16px;">Recent Periods</h3>
                    ${this.periods.length ? this.periods.slice(0, 5).map(p => `
                        <div style="display: flex; justify-content: space-between; padding: 12px 0; border-bottom: 1px solid var(--border);">
                            <span>${p.start_date} - ${p.end_date}</span>
                            <span style="color: var(--text-secondary);">${p.flow_level || 'Medium'}</span>
                        </div>
                    `).join('') : '<p style="color: var(--text-secondary);">No periods logged yet</p>'}
                    
                    <button class="btn btn-primary" style="width: 100%; margin-top: 16px;" onclick="App.openPeriodModal()">
                        <i data-lucide="plus" style="width: 16px; height: 16px; margin-right: 8px;"></i>
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

const App = {
    init() {
        this.render();
        window.addEventListener('hashchange', () => this.render());
    },

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
    },

    render() {
        const hash = window.location.hash || '#dashboard';
        const app = document.getElementById('app');
        
        app.innerHTML = this.renderNavbar();

        switch (hash) {
            case '#dashboard':
                app.innerHTML += Dashboard.render();
                break;
            case '#analysis':
                app.innerHTML += Analysis.render();
                setTimeout(() => Analysis.init(), 0);
                break;
            case '#results':
                app.innerHTML += Results.render();
                break;
            case '#calendar':
                app.innerHTML += Calendar.render();
                setTimeout(() => Calendar.init(), 0);
                break;
            default:
                app.innerHTML += '<div class="container"><div class="card"><h2>Dashboard</h2><p>Welcome to SHE-INTEL</p></div></div>';
        }

        if (window.lucide) window.lucide.createIcons();
    },

    logout() {
        localStorage.removeItem('token');
        window.location.hash = '#login';
    },
    
    openPeriodModal() {
        alert('Modal will be implemented in Task 7');
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
