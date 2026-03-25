(function () {
    const toasts = document.querySelectorAll("[data-toast]");

    function dismissToast(toast) {
        if (!toast || toast.dataset.toastDismissed === "true") {
            return;
        }

        toast.dataset.toastDismissed = "true";
        toast.classList.add("pointer-events-none", "opacity-0");
        window.setTimeout(function () {
            toast.remove();
        }, 220);
    }

    function startToast(toast) {
        const progress = toast.querySelector("[data-toast-progress]");
        const duration = Number(toast.dataset.toastDuration || 5000);

        let startedAt = Date.now();
        let remaining = duration;
        let timeoutId = null;

        function animate(widthDuration) {
            if (!progress) {
                return;
            }

            progress.style.transition = "none";
            progress.style.width = "100%";

            window.requestAnimationFrame(function () {
                progress.style.transition = "width " + widthDuration + "ms linear";
                progress.style.width = "0%";
            });
        }

        function run() {
            startedAt = Date.now();
            animate(remaining);
            timeoutId = window.setTimeout(function () {
                dismissToast(toast);
            }, remaining);
        }

        function pause() {
            if (timeoutId) {
                window.clearTimeout(timeoutId);
                timeoutId = null;
            }

            const elapsed = Date.now() - startedAt;
            remaining = Math.max(0, remaining - elapsed);

            if (progress) {
                const computedWidth = window.getComputedStyle(progress).width;
                progress.style.transition = "none";
                progress.style.width = computedWidth;
            }
        }

        function resume() {
            if (remaining <= 0) {
                dismissToast(toast);
                return;
            }

            run();
        }

        toast.addEventListener("mouseenter", pause);
        toast.addEventListener("mouseleave", resume);

        const close = toast.querySelector("[data-toast-close]");
        if (close) {
            close.addEventListener("click", function () {
                dismissToast(toast);
            });
        }

        run();
    }

    toasts.forEach(startToast);
})();
