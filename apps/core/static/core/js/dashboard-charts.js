(function () {
    "use strict";

    // === Theme detection ===
    var isDark = document.documentElement.classList.contains("dark");
    var gridColor = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)";
    var textColor = isDark ? "#9ca3af" : "#6b7280";

    // === JSON data reader ===
    function readJsonScript(id, fallback) {
        var el = document.getElementById(id);
        if (!el) return fallback;
        try {
            var parsed = JSON.parse(el.textContent);
            return typeof parsed === "string" ? JSON.parse(parsed) : parsed;
        } catch (_) {
            return fallback;
        }
    }

    // === Load all data ===
    var chartLabels = readJsonScript("chart-labels-data", []);
    var chartIncome = readJsonScript("chart-income-data", []);
    var chartExpense = readJsonScript("chart-expense-data", []);
    var expenseLabels = readJsonScript("expense-categories-labels-data", []);
    var expenseData = readJsonScript("expense-categories-data", []);
    var incomeLabels = readJsonScript("income-categories-labels-data", []);
    var incomeData = readJsonScript("income-categories-data", []);
    var topExpensesData = readJsonScript("top-expenses-data", []);

    // === Shared chart options ===
    var doughnutColors = [
        "#10b981", "#3b82f6", "#f59e0b", "#a855f7", "#ef4444",
        "#06b6d4", "#84cc16", "#f97316", "#ec4899", "#6366f1",
    ];

    function lineScaleOptions() {
        return {
            x: { grid: { color: gridColor }, ticks: { color: textColor } },
            y: {
                grid: { color: gridColor },
                ticks: {
                    color: textColor,
                    callback: function (v) {
                        return v >= 1000 ? "R$" + (v / 1000).toFixed(0) + "k" : "R$" + v;
                    },
                },
                beginAtZero: true,
            },
        };
    }

    function legendBottom() {
        return {
            position: "bottom",
            labels: { color: textColor, usePointStyle: true, pointStyle: "circle", padding: 16 },
        };
    }

    // === Chart creators ===

    function createEvolutionLine(canvasId) {
        var ctx = document.getElementById(canvasId);
        if (!ctx || chartLabels.length === 0) return null;
        return new Chart(ctx, {
            type: "line",
            data: {
                labels: chartLabels,
                datasets: [
                    {
                        label: "Receitas",
                        data: chartIncome,
                        borderColor: "#10b981",
                        backgroundColor: "rgba(16,185,129,0.1)",
                        tension: 0.3,
                        pointRadius: 5,
                        pointBackgroundColor: "#10b981",
                        fill: false,
                    },
                    {
                        label: "Despesas",
                        data: chartExpense,
                        borderColor: "#ef4444",
                        backgroundColor: "rgba(239,68,68,0.1)",
                        tension: 0.3,
                        pointRadius: 5,
                        pointBackgroundColor: "#ef4444",
                        fill: false,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: legendBottom() },
                scales: lineScaleOptions(),
            },
        });
    }

    function createEvolutionBar(canvasId) {
        var ctx = document.getElementById(canvasId);
        if (!ctx || chartLabels.length === 0) return null;
        return new Chart(ctx, {
            type: "bar",
            data: {
                labels: chartLabels,
                datasets: [
                    {
                        label: "Receitas",
                        data: chartIncome,
                        backgroundColor: "rgba(16,185,129,0.8)",
                        borderColor: "#10b981",
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                    {
                        label: "Despesas",
                        data: chartExpense,
                        backgroundColor: "rgba(239,68,68,0.8)",
                        borderColor: "#ef4444",
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: legendBottom() },
                scales: lineScaleOptions(),
            },
        });
    }

    function createDoughnut(canvasId, labels, data) {
        var ctx = document.getElementById(canvasId);
        if (!ctx || data.length === 0) return null;
        return new Chart(ctx, {
            type: "doughnut",
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: doughnutColors.slice(0, labels.length),
                    borderWidth: 2,
                    borderColor: isDark ? "#1f2937" : "#ffffff",
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "65%",
                plugins: { legend: legendBottom() },
            },
        });
    }

    function createBalanceArea(canvasId) {
        var ctx = document.getElementById(canvasId);
        if (!ctx || chartLabels.length === 0) return null;

        var balanceData = [];
        var running = 0;
        for (var i = 0; i < chartLabels.length; i++) {
            running += (chartIncome[i] || 0) - (chartExpense[i] || 0);
            balanceData.push(running);
        }

        return new Chart(ctx, {
            type: "line",
            data: {
                labels: chartLabels,
                datasets: [{
                    label: "Saldo Acumulado",
                    data: balanceData,
                    borderColor: "#3b82f6",
                    backgroundColor: "rgba(59,130,246,0.15)",
                    tension: 0.3,
                    pointRadius: 5,
                    pointBackgroundColor: "#3b82f6",
                    fill: true,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: legendBottom() },
                scales: lineScaleOptions(),
            },
        });
    }

    function createCategoryHBar(canvasId) {
        var ctx = document.getElementById(canvasId);
        if (!ctx) return null;

        var allLabels = [];
        var seen = {};
        expenseLabels.concat(incomeLabels).forEach(function (l) {
            if (!seen[l]) { seen[l] = true; allLabels.push(l); }
        });
        if (allLabels.length === 0) return null;

        var incomeMap = {};
        incomeLabels.forEach(function (label, i) { incomeMap[label] = incomeData[i] || 0; });
        var expenseMap = {};
        expenseLabels.forEach(function (label, i) { expenseMap[label] = expenseData[i] || 0; });

        var incomeValues = allLabels.map(function (l) { return incomeMap[l] || 0; });
        var expenseValues = allLabels.map(function (l) { return expenseMap[l] || 0; });

        return new Chart(ctx, {
            type: "bar",
            data: {
                labels: allLabels,
                datasets: [
                    {
                        label: "Receitas",
                        data: incomeValues,
                        backgroundColor: "rgba(16,185,129,0.8)",
                        borderColor: "#10b981",
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                    {
                        label: "Despesas",
                        data: expenseValues,
                        backgroundColor: "rgba(239,68,68,0.8)",
                        borderColor: "#ef4444",
                        borderWidth: 1,
                        borderRadius: 4,
                    },
                ],
            },
            options: {
                indexAxis: "y",
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: legendBottom() },
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            callback: function (v) {
                                return v >= 1000 ? "R$" + (v / 1000).toFixed(0) + "k" : "R$" + v;
                            },
                        },
                        beginAtZero: true,
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: { color: textColor },
                    },
                },
            },
        });
    }

    function renderTopExpenses() {
        var container = document.getElementById("top-expenses-container");
        if (!container) return;
        if (topExpensesData.length === 0) {
            container.innerHTML = '<p class="py-8 text-center text-sm text-gray-500 dark:text-gray-400">Nenhuma despesa encontrada no período.</p>';
            return;
        }
        var html = "";
        var rankColors = ["text-amber-500", "text-gray-400", "text-amber-700", "text-gray-500", "text-gray-500"];
        topExpensesData.forEach(function (item, index) {
            html += '<div class="flex items-center justify-between py-3.5">' +
                '<div class="flex items-center gap-3">' +
                '<span class="text-lg font-bold ' + (rankColors[index] || "text-gray-500") + ' dark:opacity-80 w-6 text-center">' + (index + 1) + '</span>' +
                '<div>' +
                '<p class="text-sm font-semibold text-gray-900 dark:text-gray-100">' + escapeHtml(item.description) + '</p>' +
                '<p class="text-xs text-gray-500 dark:text-gray-400">' + escapeHtml(item.category_name) + ' \u00b7 ' + formatDate(item.date) + '</p>' +
                '</div></div>' +
                '<span class="text-sm font-semibold text-red-600 dark:text-red-400">R$ ' + formatNumber(item.amount) + '</span>' +
                '</div>';
        });
        container.innerHTML = html;
    }

    // === Utility functions ===
    function escapeHtml(str) {
        var div = document.createElement("div");
        div.appendChild(document.createTextNode(str || ""));
        return div.innerHTML;
    }

    function formatNumber(num) {
        return Number(num).toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }

    function formatDate(isoDate) {
        if (!isoDate) return "";
        var parts = isoDate.split("-");
        if (parts.length === 3) return parts[2] + "/" + parts[1] + "/" + parts[0];
        return isoDate;
    }

    // === Chart Registry ===
    var DEFAULTS = {
        "evolution-line": true,
        "evolution-bar": false,
        "expense-doughnut": true,
        "income-doughnut": true,
        "balance-area": false,
        "category-hbar": false,
        "top-expenses": false,
    };

    var chartInstances = {};

    var chartCreators = {
        "evolution-line": function () { return createEvolutionLine("evolutionLineChart"); },
        "evolution-bar": function () { return createEvolutionBar("evolutionBarChart"); },
        "expense-doughnut": function () { return createDoughnut("expenseDoughnutChart", expenseLabels, expenseData); },
        "income-doughnut": function () { return createDoughnut("incomeDoughnutChart", incomeLabels, incomeData); },
        "balance-area": function () { return createBalanceArea("balanceAreaChart"); },
        "category-hbar": function () { return createCategoryHBar("categoryHBarChart"); },
        "top-expenses": function () { renderTopExpenses(); return null; },
    };

    // === localStorage ===
    var STORAGE_KEY = "dashboard_chart_prefs";

    function loadPrefs() {
        try {
            var saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
            if (saved && typeof saved === "object") {
                var result = {};
                for (var key in DEFAULTS) {
                    if (DEFAULTS.hasOwnProperty(key)) {
                        result[key] = saved.hasOwnProperty(key) ? saved[key] : DEFAULTS[key];
                    }
                }
                return result;
            }
        } catch (_) {}
        return JSON.parse(JSON.stringify(DEFAULTS));
    }

    function savePrefs(prefs) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(prefs));
        } catch (_) {}
    }

    // === Show/Hide chart sections ===
    function showSection(chartId) {
        var section = document.querySelector('[data-chart-section="' + chartId + '"]');
        if (!section) return;
        section.classList.remove("chart-hidden");

        if (!chartInstances[chartId]) {
            requestAnimationFrame(function () {
                chartInstances[chartId] = chartCreators[chartId]();
            });
        }
    }

    function hideSection(chartId) {
        var section = document.querySelector('[data-chart-section="' + chartId + '"]');
        if (!section) return;
        section.classList.add("chart-hidden");

        if (chartInstances[chartId]) {
            chartInstances[chartId].destroy();
            chartInstances[chartId] = null;
        }
    }

    // === Settings popup ===
    function initSettingsPopup() {
        var btn = document.getElementById("chart-settings-btn");
        var popup = document.getElementById("chart-settings-popup");
        var closeBtn = document.getElementById("chart-settings-close");
        if (!btn || !popup) return;

        function togglePopup() {
            if (popup.classList.contains("hidden")) {
                popup.classList.remove("hidden", "popup-animate-out");
                popup.classList.add("popup-animate-in");
            } else {
                popup.classList.remove("popup-animate-in");
                popup.classList.add("popup-animate-out");
                popup.addEventListener("animationend", function handler() {
                    popup.removeEventListener("animationend", handler);
                    popup.classList.add("hidden");
                    popup.classList.remove("popup-animate-out");
                }, { once: true });
            }
        }

        btn.addEventListener("click", togglePopup);
        if (closeBtn) closeBtn.addEventListener("click", togglePopup);

        document.addEventListener("click", function (e) {
            if (!popup.classList.contains("hidden") && !popup.contains(e.target) && !btn.contains(e.target)) {
                togglePopup();
            }
        });
    }

    // === Initialize ===
    function init() {
        var prefs = loadPrefs();

        var checkboxes = document.querySelectorAll("[data-chart-toggle]");
        checkboxes.forEach(function (cb) {
            var chartId = cb.getAttribute("data-chart-toggle");
            var isOn = prefs[chartId] !== undefined ? prefs[chartId] : DEFAULTS[chartId];
            cb.checked = isOn;

            if (isOn) {
                showSection(chartId);
            } else {
                hideSection(chartId);
            }

            cb.addEventListener("change", function () {
                prefs[chartId] = cb.checked;
                savePrefs(prefs);
                if (cb.checked) {
                    showSection(chartId);
                } else {
                    hideSection(chartId);
                }
            });
        });

        initSettingsPopup();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
