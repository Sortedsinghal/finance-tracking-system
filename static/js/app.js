/**
 * Main Dashboard Application
 */
const App = {
    currentView: 'dashboard',
    transactionPage: 1,
    transactionPageSize: 15,
    editingId: null,

    async init() {
        if (!Auth.requireAuth()) return;
        this.setupUserInfo();
        this.setupNavigation();
        this.setupRoleBasedUI();
        this.setupEventListeners();
        this.navigate('dashboard');
    },

    // ═══════════════════════════════════════════════════
    // SETUP
    // ═══════════════════════════════════════════════════

    setupUserInfo() {
        const user = Auth.getUser();
        if (!user) return;
        const el = (id) => document.getElementById(id);
        if (el('user-avatar')) el('user-avatar').textContent = user.full_name.charAt(0).toUpperCase();
        if (el('user-name')) el('user-name').textContent = user.full_name;
        if (el('user-role')) el('user-role').textContent = user.role;
        el('logout-btn')?.addEventListener('click', () => Auth.logout());
    },

    setupNavigation() {
        document.querySelectorAll('.nav-link[data-view]').forEach(item => {
            item.addEventListener('click', () => this.navigate(item.dataset.view));
        });
    },

    setupRoleBasedUI() {
        document.querySelectorAll('[data-role]').forEach(el => {
            if (!Auth.hasRole(el.dataset.role)) el.style.display = 'none';
        });
    },

    setupEventListeners() {
        document.getElementById('transaction-form')?.addEventListener('submit', e => {
            e.preventDefault();
            this.saveTransaction();
        });

        document.getElementById('txn-type')?.addEventListener('change', e => {
            this.updateCategoryOptions(e.target.value);
        });

        ['filter-type', 'filter-category', 'filter-date-from', 'filter-date-to'].forEach(id => {
            document.getElementById(id)?.addEventListener('change', () => {
                this.transactionPage = 1;
                this.loadTransactions();
            });
        });

        document.getElementById('filter-search')?.addEventListener('input',
            debounce(() => { this.transactionPage = 1; this.loadTransactions(); }, 400)
        );

        document.getElementById('export-csv')?.addEventListener('click', () => this.exportData('csv'));
        document.getElementById('export-json')?.addEventListener('click', () => this.exportData('json'));

        document.getElementById('mobile-toggle')?.addEventListener('click', () => {
            document.querySelector('.sidebar')?.classList.toggle('open');
        });
    },

    // ═══════════════════════════════════════════════════
    // NAVIGATION
    // ═══════════════════════════════════════════════════

    navigate(view) {
        this.currentView = view;
        document.querySelectorAll('.nav-link').forEach(i => i.classList.remove('active'));
        document.querySelector(`.nav-link[data-view="${view}"]`)?.classList.add('active');
        document.querySelectorAll('.view').forEach(s => s.classList.remove('active'));
        document.getElementById(`view-${view}`)?.classList.add('active');

        const titles = { dashboard: 'Dashboard', transactions: 'Transactions', analytics: 'Analytics', users: 'Users' };
        document.getElementById('page-title').textContent = titles[view] || 'Dashboard';
        this.loadViewData(view);
        document.querySelector('.sidebar')?.classList.remove('open');
    },

    async loadViewData(view) {
        switch (view) {
            case 'dashboard': await this.loadDashboard(); break;
            case 'transactions': await this.loadTransactions(); break;
            case 'analytics': await this.loadAnalytics(); break;
            case 'users': await this.loadUsers(); break;
        }
    },

    // ═══════════════════════════════════════════════════
    // DASHBOARD
    // ═══════════════════════════════════════════════════

    async loadDashboard() {
        try {
            const data = await API.get('/analytics/dashboard');
            this.renderSummaryCards(data.summary);
            Charts.destroy();
            Charts.renderMonthlyTrend('monthly-chart', data.monthly_trends.trends);
            Charts.renderCategoryBreakdown('category-chart', data.category_breakdown.expense_categories);
            this.renderRecentActivity(data.recent_activity.transactions);
        } catch (err) {
            showToast(err.message, 'error');
        }
    },

    renderSummaryCards(s) {
        animateCounter('stat-income', s.total_income, '$');
        animateCounter('stat-expenses', s.total_expenses, '$');
        animateCounter('stat-balance', s.balance, '$');
        animateCounter('stat-count', s.transaction_count, '', 0);
        document.getElementById('stat-income-sub').textContent = `${s.income_count} transactions`;
        document.getElementById('stat-expenses-sub').textContent = `${s.expense_count} transactions`;
        document.getElementById('stat-balance-sub').textContent = s.balance >= 0 ? 'Surplus' : 'Deficit';
        document.getElementById('stat-count-sub').textContent = 'Total records';
    },

    renderRecentActivity(txns) {
        const tbody = document.getElementById('recent-tbody');
        if (!tbody) return;
        if (!txns.length) {
            tbody.innerHTML = '<tr><td colspan="5"><div class="empty"><h3>No activity yet</h3></div></td></tr>';
            return;
        }
        tbody.innerHTML = txns.map(t => `
            <tr>
                <td class="cell-date">${fmtDate(t.date)}</td>
                <td><span class="tag tag-${t.type}">${t.type}</span></td>
                <td>${t.category}</td>
                <td><span class="amount ${t.type === 'income' ? 'positive' : 'negative'}">${t.type === 'income' ? '+' : '-'}$${t.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span></td>
                <td class="cell-desc">${t.description || '—'}</td>
            </tr>
        `).join('');
    },

    // ═══════════════════════════════════════════════════
    // TRANSACTIONS
    // ═══════════════════════════════════════════════════

    async loadTransactions() {
        try {
            const p = new URLSearchParams();
            p.set('page', this.transactionPage);
            p.set('page_size', this.transactionPageSize);
            const val = id => document.getElementById(id)?.value;
            if (val('filter-type')) p.set('type', val('filter-type'));
            if (val('filter-category')) p.set('category', val('filter-category'));
            if (val('filter-date-from')) p.set('date_from', val('filter-date-from'));
            if (val('filter-date-to')) p.set('date_to', val('filter-date-to'));
            if (val('filter-search')) p.set('search', val('filter-search'));

            const data = await API.get(`/transactions?${p.toString()}`);
            this.renderTransactionsTable(data);
            this.renderPagination(data);
        } catch (err) {
            showToast(err.message, 'error');
        }
    },

    renderTransactionsTable(data) {
        const tbody = document.getElementById('transactions-tbody');
        if (!tbody) return;
        if (!data.transactions.length) {
            tbody.innerHTML = '<tr><td colspan="7"><div class="empty"><h3>No transactions found</h3><p>Adjust your filters or add a new record.</p></div></td></tr>';
            return;
        }
        const isAdmin = Auth.hasRole('admin');
        tbody.innerHTML = data.transactions.map(t => `
            <tr>
                <td class="cell-date">${fmtDate(t.date)}</td>
                <td><span class="tag tag-${t.type}">${t.type}</span></td>
                <td>${t.category}</td>
                <td><span class="amount ${t.type === 'income' ? 'positive' : 'negative'}">${t.type === 'income' ? '+' : '-'}$${t.amount.toLocaleString('en-US', { minimumFractionDigits: 2 })}</span></td>
                <td class="cell-desc">${t.description || '—'}</td>
                <td class="cell-date">${fmtDate(t.created_at)}</td>
                ${isAdmin ? `<td><div class="cell-actions">
                    <button class="icon-btn" onclick="App.editTransaction(${t.id})" title="Edit">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 3a2.85 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z"/><path d="m15 5 4 4"/></svg>
                    </button>
                    <button class="icon-btn danger" onclick="App.deleteTransaction(${t.id})" title="Delete">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/></svg>
                    </button>
                </div></td>` : ''}
            </tr>
        `).join('');
    },

    renderPagination(data) {
        const info = document.getElementById('pagination-info');
        const controls = document.getElementById('pagination-controls');
        if (!info || !controls) return;

        const start = (data.page - 1) * data.page_size + 1;
        const end = Math.min(data.page * data.page_size, data.total);
        info.textContent = data.total > 0 ? `${start}–${end} of ${data.total}` : 'No records';

        let html = `<button class="pager-btn" onclick="App.goToPage(${data.page - 1})" ${data.page <= 1 ? 'disabled' : ''}>Prev</button>`;
        for (let p = 1; p <= data.total_pages && p <= 5; p++) {
            html += `<button class="pager-btn ${p === data.page ? 'active' : ''}" onclick="App.goToPage(${p})">${p}</button>`;
        }
        if (data.total_pages > 5) {
            html += `<span class="text-muted" style="padding:0 4px">…</span>`;
            html += `<button class="pager-btn ${data.total_pages === data.page ? 'active' : ''}" onclick="App.goToPage(${data.total_pages})">${data.total_pages}</button>`;
        }
        html += `<button class="pager-btn" onclick="App.goToPage(${data.page + 1})" ${data.page >= data.total_pages ? 'disabled' : ''}>Next</button>`;
        controls.innerHTML = html;
    },

    goToPage(page) { if (page < 1) return; this.transactionPage = page; this.loadTransactions(); },

    openCreateModal() {
        this.editingId = null;
        document.getElementById('modal-title').textContent = 'New Transaction';
        document.getElementById('transaction-form').reset();
        this.updateCategoryOptions('income');
        document.getElementById('txn-date').value = new Date().toISOString().split('T')[0];
        this.openModal('transaction-modal');
    },

    async editTransaction(id) {
        try {
            const txn = await API.get(`/transactions/${id}`);
            this.editingId = id;
            document.getElementById('modal-title').textContent = 'Edit Transaction';
            document.getElementById('txn-type').value = txn.type;
            this.updateCategoryOptions(txn.type);
            document.getElementById('txn-category').value = txn.category;
            document.getElementById('txn-amount').value = txn.amount;
            document.getElementById('txn-date').value = txn.date;
            document.getElementById('txn-description').value = txn.description || '';
            this.openModal('transaction-modal');
        } catch (err) { showToast(err.message, 'error'); }
    },

    async saveTransaction() {
        const data = {
            type: document.getElementById('txn-type').value,
            category: document.getElementById('txn-category').value,
            amount: parseFloat(document.getElementById('txn-amount').value),
            date: document.getElementById('txn-date').value,
            description: document.getElementById('txn-description').value || null,
        };
        try {
            if (this.editingId) {
                await API.put(`/transactions/${this.editingId}`, data);
                showToast('Transaction updated', 'success');
            } else {
                await API.post('/transactions', data);
                showToast('Transaction created', 'success');
            }
            this.closeModal('transaction-modal');
            this.loadTransactions();
        } catch (err) { showToast(err.message, 'error'); }
    },

    async deleteTransaction(id) {
        if (!confirm('Delete this transaction?')) return;
        try {
            await API.del(`/transactions/${id}`);
            showToast('Transaction deleted', 'success');
            this.loadTransactions();
        } catch (err) { showToast(err.message, 'error'); }
    },

    updateCategoryOptions(type) {
        const sel = document.getElementById('txn-category');
        if (!sel) return;
        const inc = ['Salary', 'Freelance', 'Investment', 'Business', 'Rental', 'Refund', 'Other Income'];
        const exp = ['Rent', 'Groceries', 'Utilities', 'Transport', 'Healthcare', 'Entertainment', 'Education', 'Shopping', 'Dining', 'Insurance', 'Subscriptions', 'Other Expense'];
        sel.innerHTML = (type === 'income' ? inc : exp).map(c => `<option value="${c}">${c}</option>`).join('');
    },

    async exportData(format) {
        try {
            const p = new URLSearchParams({ format });
            const val = id => document.getElementById(id)?.value;
            if (val('filter-type')) p.set('type', val('filter-type'));
            if (val('filter-category')) p.set('category', val('filter-category'));

            const res = await API.download(`/transactions/export?${p.toString()}`);
            let blob, filename;
            if (format === 'csv') { blob = await res.blob(); filename = 'transactions.csv'; }
            else { const d = await res.json(); blob = new Blob([JSON.stringify(d, null, 2)], { type: 'application/json' }); filename = 'transactions.json'; }

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url; a.download = filename; a.click();
            URL.revokeObjectURL(url);
            showToast(`Exported as ${format.toUpperCase()}`, 'success');
        } catch (err) { showToast(err.message, 'error'); }
    },

    // ═══════════════════════════════════════════════════
    // ANALYTICS
    // ═══════════════════════════════════════════════════

    async loadAnalytics() {
        try {
            const [summary, categories, monthly] = await Promise.all([
                API.get('/analytics/summary'),
                API.get('/analytics/categories').catch(() => null),
                API.get('/analytics/monthly').catch(() => null),
            ]);
            this.renderAnalyticsSummary(summary);
            if (categories) this.renderCategoryLists(categories);
            if (monthly) { Charts.destroy(); Charts.renderMonthlyTrend('analytics-monthly-chart', monthly.trends); }
        } catch (err) { showToast(err.message, 'error'); }
    },

    renderAnalyticsSummary(s) {
        const el = document.getElementById('analytics-summary');
        if (!el) return;
        el.innerHTML = `
            <div class="stats-row" style="grid-template-columns:repeat(3,1fr);margin-bottom:16px;">
                <div class="stat-card">
                    <div class="stat-header"><span class="stat-label">Total Income</span><div class="stat-icon green"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 5 5 12"/></svg></div></div>
                    <div class="stat-value">$${s.total_income.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
                    <div class="stat-sub">${s.income_count} transactions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-header"><span class="stat-label">Total Expenses</span><div class="stat-icon red"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="5 12 12 19 19 12"/></svg></div></div>
                    <div class="stat-value">$${s.total_expenses.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
                    <div class="stat-sub">${s.expense_count} transactions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-header"><span class="stat-label">Net Balance</span><div class="stat-icon blue"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg></div></div>
                    <div class="stat-value">$${s.balance.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
                    <div class="stat-sub">${s.balance >= 0 ? 'Surplus' : 'Deficit'}</div>
                </div>
            </div>`;
    },

    renderCategoryLists(data) {
        this.renderCategoryList('income-categories-list', data.income_categories);
        this.renderCategoryList('expense-categories-list', data.expense_categories);
    },

    renderCategoryList(containerId, items) {
        const el = document.getElementById(containerId);
        if (!el) return;
        if (!items.length) { el.innerHTML = '<p class="text-muted" style="padding:16px;text-align:center">No data</p>'; return; }
        el.innerHTML = items.map((item, i) => `
            <div class="cat-item">
                <div class="cat-dot" style="background:${Charts.colors[i % Charts.colors.length]}"></div>
                <div class="cat-info">
                    <div class="cat-name">${item.category}</div>
                    <div class="cat-bar"><div class="cat-bar-fill" style="width:${item.percentage}%;background:${Charts.colors[i % Charts.colors.length]}"></div></div>
                </div>
                <div class="cat-value">
                    <div class="cat-amount">$${item.total.toLocaleString('en-US', { minimumFractionDigits: 2 })}</div>
                    <div class="cat-pct">${item.percentage}%</div>
                </div>
            </div>
        `).join('');
    },

    // ═══════════════════════════════════════════════════
    // USERS
    // ═══════════════════════════════════════════════════

    async loadUsers() {
        try {
            const data = await API.get('/users');
            this.renderUsersTable(data.users);
        } catch {
            const el = document.getElementById('users-tbody');
            if (el) el.innerHTML = '<tr><td colspan="6"><div class="empty"><h3>Access denied</h3><p>Admin role required</p></div></td></tr>';
        }
    },

    renderUsersTable(users) {
        const tbody = document.getElementById('users-tbody');
        if (!tbody) return;
        tbody.innerHTML = users.map(u => `
            <tr>
                <td class="text-muted">${u.id}</td>
                <td style="font-weight:500">${u.username}</td>
                <td>${u.full_name}</td>
                <td class="text-muted">${u.email}</td>
                <td><span class="tag tag-${u.role}">${u.role}</span></td>
                <td><div class="status"><span class="status-dot ${u.is_active ? 'active' : 'inactive'}"></span>${u.is_active ? 'Active' : 'Inactive'}</div></td>
            </tr>
        `).join('');
    },

    // ═══════════════════════════════════════════════════
    // MODAL
    // ═══════════════════════════════════════════════════

    openModal(id) { document.getElementById(id)?.classList.add('active'); },
    closeModal(id) { document.getElementById(id)?.classList.remove('active'); },
};


// ═══════════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════════

function fmtDate(str) {
    if (!str) return '—';
    const d = new Date(str);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

function animateCounter(id, target, prefix = '', decimals = 2) {
    const el = document.getElementById(id);
    if (!el) return;
    const dur = 800;
    const start = performance.now();
    function tick(now) {
        const p = Math.min((now - start) / dur, 1);
        const eased = 1 - Math.pow(1 - p, 3);
        const v = target * eased;
        el.textContent = decimals === 0
            ? `${prefix}${Math.round(v).toLocaleString()}`
            : `${prefix}${v.toLocaleString('en-US', { minimumFractionDigits: decimals, maximumFractionDigits: decimals })}`;
        if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
}

function debounce(fn, ms) {
    let t;
    return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); };
}

function showToast(msg, type = 'info') {
    const c = document.getElementById('toast-container') || (() => {
        const el = document.createElement('div');
        el.id = 'toast-container';
        el.className = 'toast-container';
        document.body.appendChild(el);
        return el;
    })();
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = msg;
    c.appendChild(toast);
    setTimeout(() => { toast.style.opacity = '0'; setTimeout(() => toast.remove(), 200); }, 3500);
}

document.addEventListener('DOMContentLoaded', () => App.init());
