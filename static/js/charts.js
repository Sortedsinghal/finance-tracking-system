/**
 * Chart rendering — enterprise palette
 */
const Charts = {
    monthlyChart: null,
    categoryChart: null,

    colors: [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#06b6d4', '#ec4899', '#f97316', '#14b8a6', '#6366f1',
        '#84cc16', '#e11d48',
    ],

    defaults() {
        Chart.defaults.font.family = "'Inter', system-ui, sans-serif";
        Chart.defaults.color = '#52525b';
    },

    destroy() {
        if (this.monthlyChart) { this.monthlyChart.destroy(); this.monthlyChart = null; }
        if (this.categoryChart) { this.categoryChart.destroy(); this.categoryChart = null; }
    },

    renderMonthlyTrend(canvasId, trends) {
        this.defaults();
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const labels = trends.map(t => {
            const [y, m] = t.month.split('-');
            return new Date(y, m - 1).toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
        });

        const gridColor = 'rgba(255,255,255,0.025)';

        this.monthlyChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels,
                datasets: [
                    {
                        label: 'Income',
                        data: trends.map(t => t.income),
                        backgroundColor: 'rgba(16, 185, 129, 0.65)',
                        borderColor: 'transparent',
                        borderRadius: 3,
                        barPercentage: 0.5,
                        categoryPercentage: 0.75,
                    },
                    {
                        label: 'Expenses',
                        data: trends.map(t => t.expenses),
                        backgroundColor: 'rgba(239, 68, 68, 0.65)',
                        borderColor: 'transparent',
                        borderRadius: 3,
                        barPercentage: 0.5,
                        categoryPercentage: 0.75,
                    },
                    {
                        label: 'Net',
                        data: trends.map(t => t.net),
                        type: 'line',
                        borderColor: '#3b82f6',
                        backgroundColor: 'transparent',
                        borderWidth: 2,
                        pointRadius: 3,
                        pointBackgroundColor: '#3b82f6',
                        pointBorderColor: '#111114',
                        pointBorderWidth: 2,
                        tension: 0.35,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: { mode: 'index', intersect: false },
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            color: '#71717a',
                            font: { size: 11, weight: '500' },
                            padding: 16,
                            usePointStyle: true,
                            pointStyleWidth: 8,
                        },
                    },
                    tooltip: {
                        backgroundColor: '#18181c',
                        titleColor: '#f4f4f5',
                        bodyColor: '#a1a1aa',
                        borderColor: '#28282f',
                        borderWidth: 1,
                        cornerRadius: 6,
                        padding: { top: 8, bottom: 8, left: 12, right: 12 },
                        titleFont: { size: 12, weight: '600' },
                        bodyFont: { family: "'JetBrains Mono', monospace", size: 11 },
                        callbacks: {
                            label: c => `  ${c.dataset.label}  $${c.parsed.y.toLocaleString('en-US', { minimumFractionDigits: 2 })}`,
                        },
                    },
                },
                scales: {
                    x: {
                        ticks: { color: '#52525b', font: { size: 11 } },
                        grid: { color: gridColor, drawBorder: false },
                        border: { display: false },
                    },
                    y: {
                        ticks: {
                            color: '#52525b',
                            font: { family: "'JetBrains Mono', monospace", size: 10 },
                            callback: v => v >= 1000 ? '$' + (v / 1000).toFixed(0) + 'k' : '$' + v,
                        },
                        grid: { color: gridColor, drawBorder: false },
                        border: { display: false },
                    },
                },
            },
        });
    },

    renderCategoryBreakdown(canvasId, categories) {
        this.defaults();
        const ctx = document.getElementById(canvasId);
        if (!ctx) return;

        const labels = categories.map(c => c.category);
        const data = categories.map(c => c.total);
        const bg = categories.map((_, i) => this.colors[i % this.colors.length]);

        this.categoryChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels,
                datasets: [{
                    data,
                    backgroundColor: bg,
                    borderColor: '#111114',
                    borderWidth: 2,
                    hoverOffset: 3,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '70%',
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#71717a',
                            font: { size: 10.5, weight: '450' },
                            padding: 10,
                            usePointStyle: true,
                            pointStyleWidth: 7,
                        },
                    },
                    tooltip: {
                        backgroundColor: '#18181c',
                        titleColor: '#f4f4f5',
                        bodyColor: '#a1a1aa',
                        borderColor: '#28282f',
                        borderWidth: 1,
                        cornerRadius: 6,
                        padding: { top: 8, bottom: 8, left: 12, right: 12 },
                        bodyFont: { family: "'JetBrains Mono', monospace", size: 11 },
                        callbacks: {
                            label: c => `  ${c.label}: $${c.parsed.toLocaleString('en-US', { minimumFractionDigits: 2 })} (${categories[c.dataIndex]?.percentage ?? 0}%)`,
                        },
                    },
                },
            },
        });
    },
};
