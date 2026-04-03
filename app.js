const Dashboard = {
    render() {
        return 'Loading...';
    }
};

const App = {
    init() {
        this.render();
    },

    render() {
        const app = document.getElementById('app');
        app.innerHTML = Dashboard.render();
    }
};

document.addEventListener('DOMContentLoaded', () => App.init());
