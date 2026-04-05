/**
 * API Client — centralised HTTP methods with auth token handling.
 */
const API = {
    baseUrl: '/api',
    token: localStorage.getItem('token'),

    /** Set the JWT token for subsequent requests. */
    setToken(token) {
        this.token = token;
        localStorage.setItem('token', token);
    },

    /** Clear stored credentials. */
    clearToken() {
        this.token = null;
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },

    /** Build the common headers object. */
    _headers(json = true) {
        const h = {};
        if (json) h['Content-Type'] = 'application/json';
        if (this.token) h['Authorization'] = `Bearer ${this.token}`;
        return h;
    },

    /** Core fetch wrapper with error handling. */
    async _fetch(method, path, body = null, isJson = true) {
        const opts = { method, headers: this._headers(isJson) };
        if (body && isJson) opts.body = JSON.stringify(body);
        if (body && !isJson) opts.body = body;  // FormData

        const res = await fetch(`${this.baseUrl}${path}`, opts);

        if (res.status === 401) {
            this.clearToken();
            window.location.href = '/';
            return;
        }

        if (res.status === 204) return null;

        const data = await res.json().catch(() => null);
        if (!res.ok) {
            const msg = data?.detail || `Request failed (${res.status})`;
            throw new Error(msg);
        }
        return data;
    },

    // ── Convenience methods ────────────────────────────
    get(path)           { return this._fetch('GET', path); },
    post(path, body)    { return this._fetch('POST', path, body); },
    put(path, body)     { return this._fetch('PUT', path, body); },
    del(path)           { return this._fetch('DELETE', path); },

    /** Upload a file (multipart/form-data). */
    upload(path, formData) {
        return this._fetch('POST', path, formData, false);
    },

    /** Get CSV/JSON export as text. */
    async download(path) {
        const res = await fetch(`${this.baseUrl}${path}`, {
            headers: this._headers(false),
        });
        if (!res.ok) throw new Error('Export failed');
        return res;
    },
};
