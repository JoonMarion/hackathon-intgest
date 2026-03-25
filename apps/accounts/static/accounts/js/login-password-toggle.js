document.addEventListener("DOMContentLoaded", function () {
    const passwordInput = document.getElementById("id_password");
    const toggleButton = document.getElementById("toggle-password-visibility");

    if (!passwordInput || !toggleButton) {
        return;
    }

    toggleButton.classList.remove("hidden");
    toggleButton.addEventListener("click", function () {
        const showingPassword = passwordInput.type === "text";
        passwordInput.type = showingPassword ? "password" : "text";
        toggleButton.textContent = showingPassword ? "Mostrar" : "Ocultar";
        toggleButton.setAttribute("aria-pressed", showingPassword ? "false" : "true");
        toggleButton.setAttribute("aria-label", showingPassword ? "Mostrar senha" : "Ocultar senha");
    });
});
