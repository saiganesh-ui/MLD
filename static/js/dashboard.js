document.addEventListener('DOMContentLoaded', function() {
    loadDashboardStats();

    const refreshBtn = document.getElementById('btn-refresh');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function() {
            refreshBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin me-1"></i> Syncing...';
            loadDashboardStats(() => {
                refreshBtn.innerHTML = '<i class="fa-solid fa-arrows-rotate me-1"></i> Refresh Telemetry';
            });
        });
    }
});

let chartInstances = {};

// Global Chart.js defaults for Glassmorphism Cyber Theme
Chart.defaults.color = '#94A3B8';
Chart.defaults.font.family = "'Plus Jakarta Sans', system-ui, sans-serif";
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(11, 18, 32, 0.9)';
Chart.defaults.plugins.tooltip.borderColor = 'rgba(148, 163, 184, 0.25)';
Chart.defaults.plugins.tooltip.borderWidth = 1;
Chart.defaults.plugins.tooltip.padding = 12;
Chart.defaults.plugins.tooltip.cornerRadius = 10;
Chart.defaults.plugins.tooltip.titleFont = { weight: 'bold', size: 12 };
Chart.defaults.plugins.tooltip.bodyFont = { size: 12 };

function loadDashboardStats(callback) {
    fetch('/api/dashboard/stats')
        .then(response => response.json())
        .then(data => {
            // Update Stat Cards with animated counting feel
            document.getElementById('stat-customers').innerText = data.total_customers.toLocaleString();
            document.getElementById('stat-accounts').innerText = data.total_accounts.toLocaleString();
            document.getElementById('stat-transactions').innerText = data.total_transactions.toLocaleString();
            document.getElementById('stat-suspicious').innerText = data.suspicious_transactions.toLocaleString();
            document.getElementById('stat-alerts').innerText = data.open_alerts.toLocaleString();
            document.getElementById('stat-high-risk-cust').innerText = data.high_risk_customers.toLocaleString();
            document.getElementById('stat-avg-score').innerText = data.average_risk_score + ' / 100';

            // Chart 1: Timeline
            renderTimelineChart(data);

            // Chart 2: Suspicious vs Normal
            renderSuspiciousPieChart(data.total_transactions, data.suspicious_transactions);

            // Chart 3: Risk Distribution
            renderRiskDistChart(data.risk_distribution);

            // Chart 4: Alert Severity
            renderAlertSeverityChart(data.alert_severity);

            // Chart 5: Transaction Types
            renderTxTypesChart(data.transaction_types);

            // Chart 6: Country Activity
            renderCountryChart(data.country_activity);

            // Chart 7: Top Risky Customers Table
            renderTopCustomersTable(data.top_risky_customers);

            if (callback) callback();
        })
        .catch(err => {
            console.error("Failed to load dashboard stats:", err);
            if (callback) callback();
        });
}

function renderTimelineChart(data) {
    const ctx = document.getElementById('chart-timeline').getContext('2d');
    if (chartInstances.timeline) chartInstances.timeline.destroy();

    // Create neon gradient fills
    const blueGradient = ctx.createLinearGradient(0, 0, 0, 300);
    blueGradient.addColorStop(0, 'rgba(59, 130, 246, 0.35)');
    blueGradient.addColorStop(1, 'rgba(59, 130, 246, 0.0)');

    const amberGradient = ctx.createLinearGradient(0, 0, 0, 300);
    amberGradient.addColorStop(0, 'rgba(251, 191, 36, 0.35)');
    amberGradient.addColorStop(1, 'rgba(251, 191, 36, 0.0)');

    chartInstances.timeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Current'],
            datasets: [
                {
                    label: 'Clean Transactions',
                    data: [120, 240, 480, 800, 1400, 2600, Math.max(0, data.total_transactions - data.suspicious_transactions)],
                    borderColor: '#3B82F6',
                    backgroundColor: blueGradient,
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    pointBackgroundColor: '#22D3EE',
                    pointBorderColor: '#070B14',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                },
                {
                    label: 'Flagged Suspicious Activity',
                    data: [12, 28, 48, 85, 140, 220, data.suspicious_transactions],
                    borderColor: '#FB5268',
                    backgroundColor: amberGradient,
                    fill: true,
                    tension: 0.35,
                    borderWidth: 2.5,
                    pointBackgroundColor: '#FB5268',
                    pointBorderColor: '#070B14',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { color: '#F8FAFC', usePointStyle: true, boxWidth: 8, font: { weight: 600 } }
                }
            },
            scales: {
                x: {
                    ticks: { color: '#94A3B8' },
                    grid: { color: 'rgba(148, 163, 184, 0.08)' }
                },
                y: {
                    ticks: { color: '#94A3B8' },
                    grid: { color: 'rgba(148, 163, 184, 0.08)' }
                }
            }
        }
    });
}

function renderSuspiciousPieChart(total, suspicious) {
    const ctx = document.getElementById('chart-suspicious-pie').getContext('2d');
    if (chartInstances.suspiciousPie) chartInstances.suspiciousPie.destroy();

    const normal = Math.max(0, total - suspicious);
    chartInstances.suspiciousPie = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Normal Transactions', 'Potentially Suspicious'],
            datasets: [{
                data: [normal, suspicious],
                backgroundColor: ['#10B981', '#FB5268'],
                borderColor: '#070B14',
                borderWidth: 3,
                hoverOffset: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '72%',
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94A3B8', usePointStyle: true, padding: 14 }
                }
            }
        }
    });
}

function renderRiskDistChart(dist) {
    const ctx = document.getElementById('chart-risk-dist').getContext('2d');
    if (chartInstances.riskDist) chartInstances.riskDist.destroy();

    chartInstances.riskDist = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: ['Low Risk (0–30)', 'Medium Risk (31–70)', 'High Risk (71–100)'],
            datasets: [{
                data: [dist.low, dist.medium, dist.high],
                backgroundColor: ['#10B981', '#FBBF24', '#FB5268'],
                borderColor: '#070B14',
                borderWidth: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#94A3B8', usePointStyle: true, padding: 12 }
                }
            }
        }
    });
}

function renderAlertSeverityChart(severity) {
    const ctx = document.getElementById('chart-alert-severity').getContext('2d');
    if (chartInstances.severity) chartInstances.severity.destroy();

    chartInstances.severity = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['INFO', 'WARNING', 'HIGH', 'CRITICAL'],
            datasets: [{
                label: 'Alert Volume',
                data: [severity.INFO, severity.WARNING, severity.HIGH, severity.CRITICAL],
                backgroundColor: [
                    'rgba(59, 130, 246, 0.75)',
                    'rgba(251, 191, 36, 0.75)',
                    'rgba(251, 82, 104, 0.75)',
                    'rgba(153, 27, 27, 0.9)'
                ],
                borderColor: [
                    '#3B82F6',
                    '#FBBF24',
                    '#FB5268',
                    '#FB5268'
                ],
                borderWidth: 1.5,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#94A3B8' }, grid: { display: false } },
                y: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(148, 163, 184, 0.08)' } }
            }
        }
    });
}

function renderTxTypesChart(types) {
    const ctx = document.getElementById('chart-tx-types').getContext('2d');
    if (chartInstances.txTypes) chartInstances.txTypes.destroy();

    chartInstances.txTypes = new Chart(ctx, {
        type: 'polarArea',
        data: {
            labels: types.map(t => t.type),
            datasets: [{
                data: types.map(t => t.count),
                backgroundColor: [
                    'rgba(59, 130, 246, 0.65)',
                    'rgba(34, 211, 238, 0.65)',
                    'rgba(16, 185, 129, 0.65)',
                    'rgba(167, 139, 250, 0.65)',
                    'rgba(251, 191, 36, 0.65)'
                ],
                borderColor: '#070B14',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                r: {
                    grid: { color: 'rgba(148, 163, 184, 0.1)' },
                    ticks: { backdropColor: 'transparent', color: '#94A3B8' }
                }
            },
            plugins: {
                legend: { position: 'bottom', labels: { color: '#94A3B8', padding: 10 } }
            }
        }
    });
}

function renderCountryChart(countries) {
    const ctx = document.getElementById('chart-countries').getContext('2d');
    if (chartInstances.countries) chartInstances.countries.destroy();

    chartInstances.countries = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: countries.map(c => c.country),
            datasets: [{
                label: 'Evaluated Transfers',
                data: countries.map(c => c.count),
                backgroundColor: 'rgba(34, 211, 238, 0.7)',
                borderColor: '#22D3EE',
                borderWidth: 1,
                borderRadius: 6
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#94A3B8' }, grid: { color: 'rgba(148, 163, 184, 0.08)' } },
                y: { ticks: { color: '#F8FAFC' }, grid: { display: false } }
            }
        }
    });
}

function renderTopCustomersTable(customers) {
    const tbody = document.getElementById('tbl-top-customers');
    tbody.innerHTML = '';

    customers.forEach(c => {
        let badgeClass = 'badge-low';
        if (c.risk_level === 'Medium') badgeClass = 'badge-medium';
        if (c.risk_level === 'High') badgeClass = 'badge-high';

        const row = `
            <tr>
                <td><code>${c.customer_id}</code></td>
                <td class="fw-semibold text-white">${c.name}</td>
                <td class="text-secondary">${c.country}</td>
                <td><span class="glass-badge ${badgeClass}">${c.risk_score} (${c.risk_level})</span></td>
                <td>
                    <a href="/customers/${c.customer_id}" class="btn-glass-primary btn-sm py-1 px-2 text-decoration-none" style="font-size: 0.78rem;">
                        <i class="fa-solid fa-arrow-up-right-from-square me-1"></i> Dossier
                    </a>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}
