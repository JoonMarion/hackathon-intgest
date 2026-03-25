(() => {
    const closeMenu = (menu) => {
        const toggle = menu.querySelector("[data-user-menu-toggle]");
        const panel = menu.querySelector("[data-user-menu-panel]");

        if (!toggle || !panel) {
            return;
        }

        panel.classList.add("hidden");
        toggle.setAttribute("aria-expanded", "false");
    };

    const openMenu = (menu) => {
        const toggle = menu.querySelector("[data-user-menu-toggle]");
        const panel = menu.querySelector("[data-user-menu-panel]");

        if (!toggle || !panel) {
            return;
        }

        panel.classList.remove("hidden");
        toggle.setAttribute("aria-expanded", "true");
    };

    if (window.__userMenuGlobalListenersBound !== true) {
        document.addEventListener("click", (event) => {
            const menus = document.querySelectorAll("[data-user-menu]");

            menus.forEach((menu) => {
                if (!menu.contains(event.target)) {
                    closeMenu(menu);
                }
            });
        });

        document.addEventListener("keydown", (event) => {
            if (event.key !== "Escape") {
                return;
            }

            const menus = document.querySelectorAll("[data-user-menu]");

            menus.forEach((menu) => {
                const toggle = menu.querySelector("[data-user-menu-toggle]");
                const panel = menu.querySelector("[data-user-menu-panel]");

                if (!toggle || !panel || panel.classList.contains("hidden")) {
                    return;
                }

                closeMenu(menu);
                toggle.focus();
            });
        });

        window.__userMenuGlobalListenersBound = true;
    }

    const menus = document.querySelectorAll("[data-user-menu]");

    menus.forEach((menu) => {
        if (menu.dataset.bound === "true") {
            return;
        }

        menu.dataset.bound = "true";

        const toggle = menu.querySelector("[data-user-menu-toggle]");
        const panel = menu.querySelector("[data-user-menu-panel]");

        if (!toggle || !panel) {
            return;
        }

        toggle.addEventListener("click", (event) => {
            event.stopPropagation();

            if (panel.classList.contains("hidden")) {
                openMenu(menu);
                return;
            }

            closeMenu(menu);
        });
    });
})();
