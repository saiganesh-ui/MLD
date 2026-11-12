let currentPage = 1;

document.addEventListener('DOMContentLoaded', function() {
    loadTransactions(1);

    const filterBtn = document.getElementById('btn-apply-filters');
    if (filterBtn) {
        filterBtn.addEventListener('click', function() {
            loadTransactions(1);
        });
    }

    // Instant search on enter
    const searchInput = document.getElementById('filter-search');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                loadTransactions(1);
            }
        });
    }
});

function loadTransactions(page) {
    currentPage = page;
    const search = document.getElementById('filter-search').value;
    const risk = document.getElementById('filter-risk').value;
    const country = document.getElementById('filter-country').value;
    const suspicious = document.getElementById('filter-suspicious').checked;

    const url = `/api/transactions?page=${page}&search=${encodeURIComponent(search)}&risk_level=${risk}&country=${encodeURIComponent(country)}&suspicious=${suspicious}`;

    fetch(url)
        .then(res => res.json())
        .then(data => {
            renderTable(data.transactions);
            renderPagination(data.current_page, data.pages);
        })
        .catch(err => console.error("Error loading transactions:", err));
}

function renderTable(transactions) {
    const tbody = document.getElementById('tbl-transactions');
    tbody.innerHTML = '';

    if (transactions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="9" class="text-center text-muted py-5"><i class="fa-solid fa-inbox fs-3 mb-2 d-block"></i>No transactions match the specified parameters.</td></tr>';
        return;
    }

    transactions.forEach(t => {
        let badgeClass = 'badge-low';
        if (t.risk_level === 'Medium') badgeClass = 'badge-medium';
        if (t.risk_level === 'High') badgeClass = 'badge-high';

        const suspBadge = t.suspicious 
            ? '<span class="glass-badge badge-high"><i class="fa-solid fa-triangle-exclamation"></i> SUSPICIOUS</span>' 
            : '<span class="glass-badge badge-low"><i class="fa-solid fa-shield-check"></i> NORMAL</span>';

        const row = `
            <tr>
                <td><code>${t.transaction_id}</code></td>
                <td><span class="text-secondary font-monospace">${t.sender_account}</span></td>
                <td><span class="text-secondary font-monospace">${t.receiver_account}</span></td>
                <td class="fw-bold font-monospace text-white fs-6">$${t.amount.toLocaleString(undefined, {minimumFractionDigits: 2})} <small class="text-muted" style="font-size: 0.7rem;">${t.currency}</small></td>
                <td><span class="glass-badge badge-blue">${t.transaction_type}</span></td>
                <td><small class="text-secondary">${t.sender_country} <i class="fa-solid fa-arrow-right-long text-cyan-accent mx-1" style="color: var(--cyan-accent);"></i> ${t.receiver_country}</small></td>
                <td><span class="glass-badge ${badgeClass}">${t.risk_score} (${t.risk_level})</span></td>
                <td>${suspBadge}</td>
                <td>
                    <a href="/transactions/${t.transaction_id}" class="btn-glass-primary btn-sm py-1 px-3 text-decoration-none" style="font-size: 0.78rem;">
                        <i class="fa-solid fa-magnifying-glass-chart me-1"></i> Investigate
                    </a>
                </td>
            </tr>
        `;
        tbody.innerHTML += row;
    });
}

function renderPagination(current, total) {
    document.getElementById('page-info').innerText = `Page ${current} of ${total}`;
    const container = document.getElementById('pagination-controls');
    container.innerHTML = '';

    if (total <= 1) return;

    for (let i = 1; i <= Math.min(total, 10); i++) {
        const active = i === current ? 'btn-glass-primary' : 'btn-glass-secondary';
        const li = `<li class="page-item"><button class="btn btn-sm ${active} py-1 px-2 font-monospace" style="font-size: 0.8rem;" onclick="loadTransactions(${i}); return false;">${i}</button></li>`;
        container.innerHTML += li;
    }
}
