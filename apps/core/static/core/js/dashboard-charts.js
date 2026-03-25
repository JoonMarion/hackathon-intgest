(function () {
    const isDark = document.documentElement.classList.contains("dark");
    const gridColor = isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.06)";
    const textColor = isDark ? "#9ca3af" : "#6b7280";

    const readJsonScript = function (id, fallback) {
        const element = document.getElementById(id);
        if (!element) {
            return fallback;
        }

        try {
            const firstParse = JSON.parse(element.textContent);
            if (typeof firstParse === "string") {
                try {
                    return JSON.parse(firstParse);
                } catch (_error) {
                    return firstParse;
                }
            }
            return firstParse;
        } catch (_error) {
            return fallback;
        }
    };

    const chartLabels = readJsonScript("chart-labels-data", []);
    const chartIncome = readJsonScript("chart-income-data", []);
    const chartExpense = readJsonScript("chart-expense-data", []);
    const expenseLabels = readJsonScript("expense-categories-labels-data", []);
    const expenseData = readJsonScript("expense-categories-data", []);
    const incomeLabels = readJsonScript("income-categories-labels-data", []);
    const incomeData = readJsonScript("income-categories-data", []);

    const evolutionCtx = document.getElementById("evolutionChart");
    if (evolutionCtx) {
        new Chart(evolutionCtx, {
            type: "line",
            data: {
                labels: chartLabels,
                datasets: [
                    {
                        label: "Receitas",
                        data: chartIncome,
                        borderColor: "#10b981",
                        backgroundColor: "rgba(16, 185, 129, 0.1)",
                        tension: 0.3,
                        pointRadius: 5,
                        pointBackgroundColor: "#10b981",
                        fill: false,
                    },
                    {
                        label: "Despesas",
                        data: chartExpense,
                        borderColor: "#ef4444",
                        backgroundColor: "rgba(239, 68, 68, 0.1)",
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
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: textColor, usePointStyle: true, pointStyle: "circle" },
                    },
                },
                scales: {
                    x: {
                        grid: { color: gridColor },
                        ticks: { color: textColor },
                    },
                    y: {
                        grid: { color: gridColor },
                        ticks: {
                            color: textColor,
                            callback: function (value) {
                                return "R$" + (value / 1000).toFixed(0) + "k";
                            },
                        },
                        beginAtZero: true,
                    },
                },
            },
        });
    }

    const doughnutColors = [
        "#10b981", "#3b82f6", "#f59e0b", "#a855f7", "#ef4444",
        "#06b6d4", "#84cc16", "#f97316", "#ec4899", "#6366f1",
    ];

    const expenseCtx = document.getElementById("expenseDoughnutChart");
    if (expenseCtx && expenseData.length > 0) {
        new Chart(expenseCtx, {
            type: "doughnut",
            data: {
                labels: expenseLabels,
                datasets: [{
                    data: expenseData,
                    backgroundColor: doughnutColors.slice(0, expenseLabels.length),
                    borderWidth: 2,
                    borderColor: isDark ? "#1f2937" : "#ffffff",
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "65%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: textColor, usePointStyle: true, pointStyle: "circle", padding: 16 },
                    },
                },
            },
        });
    }

    const incomeCtx = document.getElementById("incomeDoughnutChart");
    if (incomeCtx && incomeData.length > 0) {
        new Chart(incomeCtx, {
            type: "doughnut",
            data: {
                labels: incomeLabels,
                datasets: [{
                    data: incomeData,
                    backgroundColor: doughnutColors.slice(0, incomeLabels.length),
                    borderWidth: 2,
                    borderColor: isDark ? "#1f2937" : "#ffffff",
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "65%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: { color: textColor, usePointStyle: true, pointStyle: "circle", padding: 16 },
                    },
                },
            },
        });
    }
})();
