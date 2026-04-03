const App = {
    init() {
        this.renderNavbar();
        this.render();
        window.addEventListener('hashchange', () => this.render());
    },

    renderNavbar() {
        return '';
    },

    render() {
        const hash = window.location.hash || '#dashboard';
        const app = document.getElementById('app');
        
        switch (hash) {
            case '#dashboard':
                app.innerHTML = '<div class="card"><h2>Dashboard</h2><p>Welcome to SHE-INTEL</p></div>';
                break;
            case '#analysis':
                app.innerHTML = '<div class="card"><h2>Health Analysis</h2><p>Run ML-powered health analysis</p></div>';
                break;
            case '#results':
                app.innerHTML = '<div class="card"><h2>Results</h2><p>View your analysis results</p></div>';
                break;
            case '#calendar':
                app.innerHTML = '<div class="card"><h2>Calendar</h2><p>View & manage period history</p></div>';
                break;
            default:
                app.innerHTML = '<div class="card"><h2>Dashboard</h2><p>Welcome to SHE-INTEL</p></div>';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
