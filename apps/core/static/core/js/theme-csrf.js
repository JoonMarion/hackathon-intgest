(function () {
    const root = document.documentElement;
    const storedTheme = localStorage.getItem('theme');

    if (storedTheme === 'dark') {
        root.classList.add('dark');
    }

    function emitThemeChange() {
        const theme = root.classList.contains('dark') ? 'dark' : 'light';
        document.dispatchEvent(new CustomEvent('pf:themechange', { detail: { theme: theme } }));
    }

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(';').shift();
        }
        return '';
    }

    document.addEventListener('click', function (event) {
        const toggle = event.target.closest('[data-theme-toggle]');
        if (!toggle) {
            return;
        }

        const isDark = root.classList.toggle('dark');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
        emitThemeChange();
    });

    document.addEventListener('htmx:configRequest', function (event) {
        event.detail.headers['X-CSRFToken'] = getCookie('csrftoken');
    });
})();
