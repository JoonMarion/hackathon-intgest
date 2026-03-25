(function () {
    const root = document.documentElement;
    const savedTheme = localStorage.getItem("theme");

    if (savedTheme === "dark") {
        root.classList.add("dark");
    }

    document.addEventListener("click", function (event) {
        const toggle = event.target.closest("[data-theme-toggle]");
        if (!toggle) {
            return;
        }

        const isDark = root.classList.toggle("dark");
        localStorage.setItem("theme", isDark ? "dark" : "light");
    });

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) {
            return parts.pop().split(";").shift();
        }
        return "";
    }

    document.body.addEventListener("htmx:configRequest", function (event) {
        event.detail.headers["X-CSRFToken"] = getCookie("csrftoken");
    });
})();
