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
                app.innerHTML += '<div class="container"><div class="card"><h2>Health Analysis</h2><p>Run ML-powered health analysis</p></div></div>';
                break;
            case '#results':
                app.innerHTML += '<div class="container"><div class="card"><h2>Results</h2><p>View your analysis results</p></div></div>';
                break;
            case '#calendar':
                app.innerHTML += '<div class="container"><div class="card"><h2>Calendar</h2><p>View & manage period history</p></div></div>';
                break;
            default:
                app.innerHTML += '<div class="container"><div class="card"><h2>Dashboard</h2><p>Welcome to SHE-INTEL</p></div></div>';
        }

        if (window.lucide) window.lucide.createIcons();
    },

    logout() {
        localStorage.removeItem('token');
        window.location.hash = '#login';
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
