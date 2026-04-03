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
                app.innerHTML += '<div class="container"><div class="card"><h2>Dashboard</h2><p>Welcome to SHE-INTEL</p></div></div>';
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
