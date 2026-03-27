(() => {
    const currentState = window.__pfDashboardChartsState;
    if (currentState && typeof currentState.cleanup === 'function') {
        currentState.cleanup();
    }

    const STORAGE_KEY = 'dashboard_chart_prefs';
    const DEFAULTS = {
        'evolution-line': true,
        'evolution-bar': false,
        'expense-doughnut': true,
        'income-doughnut': true,
        'balance-area': true,
        'category-hbar': false,
        'top-expenses': true,
    };

    const state = {
        chartInstances: {},
        listeners: [],
        prefs: null,
        popupOpen: false,
    };
    window.__pfDashboardChartsState = state;

    function addManagedListener(target, eventName, handler, options) {
        if (!target) {
            return;
        }
        target.addEventListener(eventName, handler, options);
        state.listeners.push(() => target.removeEventListener(eventName, handler, options));
    }

    function cleanup() {
        Object.values(state.chartInstances).forEach((instance) => {
            if (instance && typeof instance.destroy === 'function') {
                instance.destroy();
            }
        });
        state.chartInstances = {};
        state.listeners.forEach((removeListener) => removeListener());
        state.listeners = [];
        state.popupOpen = false;
    }

    state.cleanup = cleanup;

    function readJsonScript(id, fallback) {
        const element = document.getElementById(id);
        if (!element) {
            return fallback;
        }
        try {
            const parsed = JSON.parse(element.textContent);
            return typeof parsed === 'string' ? JSON.parse(parsed) : parsed;
        } catch (error) {
            return fallback;
        }
    }

    function cssVar(name, fallback) {
        const value = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
        return value || fallback;
    }

    function getThemeTokens() {
        const isDark = document.documentElement.classList.contains('dark');
        return {
            isDark,
            text: cssVar('--pf-text-muted', isDark ? '#94a2c3' : '#6f7892'),
            title: cssVar('--pf-text', isDark ? '#edf3ff' : '#182033'),
            brand: cssVar('--pf-brand', isDark ? '#79a2ff' : '#2f6bff'),
            brandStrong: cssVar('--pf-brand-strong', isDark ? '#9db9ff' : '#1f4fd1'),
            brandSoft: cssVar('--pf-brand-soft', isDark ? 'rgba(121,162,255,0.18)' : '#dce8ff'),
            mintStrong: cssVar('--pf-mint-strong', isDark ? '#63d0a0' : '#2e9e72'),
            mintSoft: cssVar('--pf-mint-soft', isDark ? 'rgba(61,182,132,0.18)' : '#dff5eb'),
            roseStrong: cssVar('--pf-rose-strong', isDark ? '#ff92ad' : '#df6a87'),
            roseSoft: cssVar('--pf-rose-soft', isDark ? 'rgba(223,106,135,0.18)' : '#ffe4ea'),
            amberStrong: cssVar('--pf-amber-strong', isDark ? '#f1c86c' : '#be8b25'),
            amberSoft: cssVar('--pf-amber-soft', isDark ? 'rgba(190,139,37,0.18)' : '#f6edd5'),
            lilacSoft: cssVar('--pf-lilac-soft', isDark ? 'rgba(176,164,255,0.18)' : '#e8e8ff'),
            surfaceStrong: cssVar('--pf-surface-strong', isDark ? '#16233d' : '#ffffff'),
            grid: isDark ? 'rgba(148, 162, 195, 0.16)' : 'rgba(95, 121, 173, 0.16)',
            font: cssVar('--pf-font-sans', 'sans-serif'),
        };
    }

    function formatCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2,
        }).format(Number(value || 0));
    }

    function formatAxisCurrency(value) {
        return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            maximumFractionDigits: value >= 1000 ? 0 : 2,
        }).format(Number(value || 0));
    }

    function formatDate(isoDate) {
        if (!isoDate) {
            return '';
        }
        const [year, month, day] = isoDate.split('-');
        if (!day) {
            return isoDate;
        }
        return `${day}/${month}/${year}`;
    }

    function buildCommonScaleOptions(tokens) {
        return {
            x: {
                grid: { color: tokens.grid },
                border: { display: false },
                ticks: {
                    color: tokens.text,
                    font: { family: tokens.font, size: 12, weight: '600' },
                },
            },
            y: {
                beginAtZero: true,
                grid: { color: tokens.grid },
                border: { display: false },
                ticks: {
                    color: tokens.text,
                    font: { family: tokens.font, size: 12, weight: '600' },
                    callback(value) {
                        return formatAxisCurrency(value);
                    },
                },
            },
        };
    }

    function buildLegend(tokens) {
        return {
            position: 'bottom',
            labels: {
                color: tokens.text,
                usePointStyle: true,
                pointStyle: 'circle',
                padding: 18,
                boxWidth: 10,
                boxHeight: 10,
                font: { family: tokens.font, size: 12, weight: '700' },
            },
        };
    }

    function buildTooltip(tokens) {
        return {
            backgroundColor: tokens.surfaceStrong,
            titleColor: tokens.title,
            bodyColor: tokens.title,
            borderColor: tokens.grid,
            borderWidth: 1,
            cornerRadius: 14,
            padding: 12,
            bodyFont: { family: tokens.font, size: 12, weight: '600' },
            titleFont: { family: tokens.font, size: 12, weight: '700' },
            callbacks: {
                label(context) {
                    const label = context.dataset && context.dataset.label ? `${context.dataset.label}: ` : '';
                    const rawValue = typeof context.raw === 'number' ? context.raw : Number(context.raw || 0);
                    return `${label}${formatCurrency(rawValue)}`;
                },
            },
        };
    }

    const chartLabels = readJsonScript('chart-labels-data', []);
    const chartIncome = readJsonScript('chart-income-data', []);
    const chartExpense = readJsonScript('chart-expense-data', []);
    const expenseLabels = readJsonScript('expense-categories-labels-data', []);
    const expenseData = readJsonScript('expense-categories-data', []);
    const incomeLabels = readJsonScript('income-categories-labels-data', []);
    const incomeData = readJsonScript('income-categories-data', []);
    const topExpensesData = readJsonScript('top-expenses-data', []);

    function createEvolutionLine(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            return null;
        }
        const tokens = getThemeTokens();
        return new Chart(canvas, {
            type: 'line',
            data: {
                labels: chartLabels,
                datasets: [
                    {
                        label: 'Receitas',
                        data: chartIncome,
                        borderColor: tokens.mintStrong,
                        backgroundColor: tokens.mintSoft,
                        pointBackgroundColor: tokens.mintStrong,
                        pointBorderColor: tokens.surfaceStrong,
                        pointRadius: 4,
                        pointHoverRadius: 5,
                        tension: 0.34,
                        fill: false,
                        borderWidth: 3,
                    },
                    {
                        label: 'Despesas',
                        data: chartExpense,
                        borderColor: tokens.roseStrong,
                        backgroundColor: tokens.roseSoft,
                        pointBackgroundColor: tokens.roseStrong,
                        pointBorderColor: tokens.surfaceStrong,
                        pointRadius: 4,
                        pointHoverRadius: 5,
                        tension: 0.34,
                        fill: false,
                        borderWidth: 3,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'index' },
                plugins: {
                    legend: buildLegend(tokens),
                    tooltip: buildTooltip(tokens),
                },
                scales: buildCommonScaleOptions(tokens),
            },
        });
    }

    function createEvolutionBar(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            return null;
        }
        const tokens = getThemeTokens();
        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels: chartLabels,
                datasets: [
                    {
                        label: 'Receitas',
                        data: chartIncome,
                        backgroundColor: tokens.mintSoft,
                        borderColor: tokens.mintStrong,
                        borderWidth: 1,
                        borderRadius: 12,
                    },
                    {
                        label: 'Despesas',
                        data: chartExpense,
                        backgroundColor: tokens.roseSoft,
                        borderColor: tokens.roseStrong,
                        borderWidth: 1,
                        borderRadius: 12,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: buildLegend(tokens),
                    tooltip: buildTooltip(tokens),
                },
                scales: buildCommonScaleOptions(tokens),
            },
        });
    }

    function createBalanceArea(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            return null;
        }
        const tokens = getThemeTokens();
        let runningBalance = 0;
        const balanceData = chartLabels.map((_, index) => {
            runningBalance += Number(chartIncome[index] || 0) - Number(chartExpense[index] || 0);
            return runningBalance;
        });

        return new Chart(canvas, {
            type: 'line',
            data: {
                labels: chartLabels,
                datasets: [
                    {
                        label: 'Saldo acumulado',
                        data: balanceData,
                        borderColor: tokens.brand,
                        backgroundColor: tokens.brandSoft,
                        pointBackgroundColor: tokens.brandStrong,
                        pointBorderColor: tokens.surfaceStrong,
                        pointRadius: 4,
                        tension: 0.32,
                        fill: true,
                        borderWidth: 3,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { intersect: false, mode: 'index' },
                plugins: {
                    legend: buildLegend(tokens),
                    tooltip: buildTooltip(tokens),
                },
                scales: buildCommonScaleOptions(tokens),
            },
        });
    }

    function createDoughnut(canvasId, labels, data) {
        const canvas = document.getElementById(canvasId);
        if (!canvas || data.length === 0) {
            return null;
        }
        const tokens = getThemeTokens();
        const palette = [
            tokens.brand,
            tokens.mintStrong,
            tokens.roseStrong,
            tokens.amberStrong,
            '#7a77ff',
            '#4ba7c9',
            '#83924b',
        ];
        return new Chart(canvas, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [
                    {
                        data,
                        backgroundColor: labels.map((_, index) => palette[index % palette.length]),
                        borderColor: tokens.surfaceStrong,
                        borderWidth: 4,
                        hoverOffset: 10,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '68%',
                plugins: {
                    legend: buildLegend(tokens),
                    tooltip: buildTooltip(tokens),
                },
            },
        });
    }

    function createCategoryHBar(canvasId) {
        const canvas = document.getElementById(canvasId);
        if (!canvas) {
            return null;
        }
        const tokens = getThemeTokens();
        const labels = [];
        const seen = new Set();
        [...expenseLabels, ...incomeLabels].forEach((label) => {
            if (!seen.has(label)) {
                seen.add(label);
                labels.push(label);
            }
        });
        if (labels.length === 0) {
            return null;
        }

        const incomeMap = Object.fromEntries(incomeLabels.map((label, index) => [label, incomeData[index] || 0]));
        const expenseMap = Object.fromEntries(expenseLabels.map((label, index) => [label, expenseData[index] || 0]));

        return new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Receitas',
                        data: labels.map((label) => incomeMap[label] || 0),
                        backgroundColor: tokens.mintSoft,
                        borderColor: tokens.mintStrong,
                        borderWidth: 1,
                        borderRadius: 12,
                    },
                    {
                        label: 'Despesas',
                        data: labels.map((label) => expenseMap[label] || 0),
                        backgroundColor: tokens.roseSoft,
                        borderColor: tokens.roseStrong,
                        borderWidth: 1,
                        borderRadius: 12,
                    },
                ],
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: buildLegend(tokens),
                    tooltip: buildTooltip(tokens),
                },
                scales: {
                    ...buildCommonScaleOptions(tokens),
                    x: {
                        ...buildCommonScaleOptions(tokens).y,
                    },
                    y: {
                        ...buildCommonScaleOptions(tokens).x,
                    },
                },
            },
        });
    }

    function renderTopExpenses() {
        const container = document.getElementById('top-expenses-container');
        if (!container) {
            return { destroy() {} };
        }
        if (topExpensesData.length === 0) {
            container.innerHTML = [
                '<div class="rounded-[1.4rem] border border-dashed border-[color:var(--pf-border)] px-4 py-10 text-center">',
                '<p class="text-sm font-semibold text-[color:var(--pf-text)]">Nenhuma despesa encontrada no período.</p>',
                '<p class="mt-2 text-sm pf-text-muted">Ajuste o filtro ou registre novas saídas para comparar aqui.</p>',
                '</div>',
            ].join('');
            return { destroy() { container.innerHTML = ''; } };
        }

        container.innerHTML = topExpensesData.map((item, index) => {
            const rankTone = index === 0 ? 'pf-pill-amber' : index === 1 ? 'pf-pill-brand' : 'pf-pill';
            return [
                '<div class="pf-top-expense-row">',
                '<div class="flex min-w-0 items-center gap-3">',
                `<span class="pf-rank-badge">${index + 1}</span>`,
                '<div class="min-w-0">',
                `<p class="truncate text-sm font-semibold text-[color:var(--pf-text)]">${escapeHtml(item.description)}</p>`,
                `<p class="mt-1 text-xs pf-text-muted">${escapeHtml(item.category_name)} · ${formatDate(item.date)}</p>`,
                '</div>',
                '</div>',
                '<div class="text-right">',
                `<p class="text-sm font-black text-[color:var(--pf-rose-strong)]">${formatCurrency(item.amount)}</p>`,
                `<span class="mt-2 inline-flex ${rankTone} pf-pill">ranking</span>`,
                '</div>',
                '</div>',
            ].join('');
        }).join('');

        return {
            destroy() {
                container.innerHTML = '';
            },
        };
    }

    function escapeHtml(value) {
        const div = document.createElement('div');
        div.textContent = value || '';
        return div.innerHTML;
    }

    const chartCreators = {
        'evolution-line': () => createEvolutionLine('evolutionLineChart'),
        'evolution-bar': () => createEvolutionBar('evolutionBarChart'),
        'expense-doughnut': () => createDoughnut('expenseDoughnutChart', expenseLabels, expenseData),
        'income-doughnut': () => createDoughnut('incomeDoughnutChart', incomeLabels, incomeData),
        'balance-area': () => createBalanceArea('balanceAreaChart'),
        'category-hbar': () => createCategoryHBar('categoryHBarChart'),
        'top-expenses': () => renderTopExpenses(),
    };

    function loadPrefs() {
        try {
            const saved = JSON.parse(localStorage.getItem(STORAGE_KEY));
            if (saved && typeof saved === 'object') {
                return Object.keys(DEFAULTS).reduce((result, key) => {
                    result[key] = Object.prototype.hasOwnProperty.call(saved, key) ? saved[key] : DEFAULTS[key];
                    return result;
                }, {});
            }
        } catch (error) {
            return { ...DEFAULTS };
        }
        return { ...DEFAULTS };
    }

    function savePrefs() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state.prefs));
        } catch (error) {
            return;
        }
    }

    function destroyChart(chartId) {
        const instance = state.chartInstances[chartId];
        if (instance && typeof instance.destroy === 'function') {
            instance.destroy();
        }
        state.chartInstances[chartId] = null;
    }

    function showSection(chartId) {
        const section = document.querySelector(`[data-chart-section="${chartId}"]`);
        if (!section) {
            return;
        }
        section.classList.remove('chart-hidden');
        if (!state.chartInstances[chartId]) {
            state.chartInstances[chartId] = chartCreators[chartId]();
        }
    }

    function hideSection(chartId) {
        const section = document.querySelector(`[data-chart-section="${chartId}"]`);
        if (!section) {
            return;
        }
        section.classList.add('chart-hidden');
        destroyChart(chartId);
    }

    function applyPrefs() {
        Object.keys(DEFAULTS).forEach((chartId) => {
            if (state.prefs[chartId]) {
                showSection(chartId);
            } else {
                hideSection(chartId);
            }
        });
    }

    function rerenderVisibleCharts() {
        Object.keys(state.chartInstances).forEach((chartId) => destroyChart(chartId));
        Object.keys(DEFAULTS).forEach((chartId) => {
            if (state.prefs[chartId]) {
                showSection(chartId);
            }
        });
    }

    function closePopup(popup, button, shouldReturnFocus) {
        if (!popup || popup.classList.contains('hidden')) {
            state.popupOpen = false;
            return;
        }
        popup.classList.remove('popup-animate-in');
        popup.classList.add('popup-animate-out');
        popup.setAttribute('aria-hidden', 'true');
        if (button) {
            button.setAttribute('aria-expanded', 'false');
        }
        const handleAnimationEnd = () => {
            popup.classList.add('hidden');
            popup.classList.remove('popup-animate-out');
            if (shouldReturnFocus && button) {
                button.focus();
            }
        };
        popup.addEventListener('animationend', handleAnimationEnd, { once: true });
        state.popupOpen = false;
    }

    function openPopup(popup, button) {
        if (!popup) {
            return;
        }
        popup.classList.remove('hidden', 'popup-animate-out');
        popup.classList.add('popup-animate-in');
        popup.setAttribute('aria-hidden', 'false');
        if (button) {
            button.setAttribute('aria-expanded', 'true');
        }
        state.popupOpen = true;
        requestAnimationFrame(() => {
            const firstFocusable = popup.querySelector('[data-chart-toggle], button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                firstFocusable.focus();
                return;
            }
            popup.focus();
        });
    }

    function initSettingsPopup() {
        const button = document.getElementById('chart-settings-btn');
        const popup = document.getElementById('chart-settings-popup');
        const closeButton = document.getElementById('chart-settings-close');
        if (!button || !popup) {
            return;
        }

        addManagedListener(button, 'click', () => {
            if (state.popupOpen) {
                closePopup(popup, button, false);
                return;
            }
            openPopup(popup, button);
        });
        addManagedListener(closeButton, 'click', () => closePopup(popup, button, true));
        addManagedListener(document, 'click', (event) => {
            if (!state.popupOpen) {
                return;
            }
            if (popup.contains(event.target) || button.contains(event.target)) {
                return;
            }
            closePopup(popup, button, false);
        });
        addManagedListener(document, 'keydown', (event) => {
            if (!state.popupOpen || event.key !== 'Escape') {
                return;
            }
            event.preventDefault();
            closePopup(popup, button, true);
        });
    }

    function initCheckboxes() {
        const checkboxes = document.querySelectorAll('[data-chart-toggle]');
        checkboxes.forEach((checkbox) => {
            const chartId = checkbox.getAttribute('data-chart-toggle');
            checkbox.checked = Boolean(state.prefs[chartId]);
            addManagedListener(checkbox, 'change', () => {
                state.prefs[chartId] = checkbox.checked;
                savePrefs();
                if (checkbox.checked) {
                    showSection(chartId);
                    return;
                }
                hideSection(chartId);
            });
        });
    }

    function init() {
        if (typeof Chart === 'undefined') {
            return;
        }

        const hasDashboard = document.getElementById('evolutionLineChart') || document.getElementById('top-expenses-container');
        if (!hasDashboard) {
            return;
        }

        Chart.defaults.font.family = getThemeTokens().font;
        Chart.defaults.color = getThemeTokens().text;

        state.prefs = loadPrefs();
        initCheckboxes();
        initSettingsPopup();
        applyPrefs();
        addManagedListener(document, 'pf:themechange', () => {
            Chart.defaults.font.family = getThemeTokens().font;
            Chart.defaults.color = getThemeTokens().text;
            rerenderVisibleCharts();
        });
    }

    if (document.readyState === 'loading') {
        addManagedListener(document, 'DOMContentLoaded', init, { once: true });
    } else {
        init();
    }
})();
