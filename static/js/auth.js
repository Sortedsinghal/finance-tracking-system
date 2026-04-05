/**
 * Auth state management — handles login, logout, and user info.
 */
const Auth = {
    /** Get the stored user object. */
    getUser() {
        const raw = localStorage.getItem('user');
        return raw ? JSON.parse(raw) : null;
    },

    /** Save user info after login. */
    setUser(user) {
        localStorage.setItem('user', JSON.stringify(user));
    },

    /** Check if a user is currently logged in. */
    isLoggedIn() {
        return !!localStorage.getItem('token');
    },

    /** Get the current user's role. */
    getRole() {
        const user = this.getUser();
        return user?.role || 'viewer';
    },

    /** Check if the current user has at least the given role. */
    hasRole(required) {
        const hierarchy = { viewer: 1, analyst: 2, admin: 3 };
        return (hierarchy[this.getRole()] || 0) >= (hierarchy[required] || 0);
    },

    /** Attempt to login with credentials. */
    async login(username, password) {
        const data = await API.post('/auth/login', { username, password });
        API.setToken(data.access_token);
        this.setUser({
            username: data.username,
            full_name: data.full_name,
            role: data.role,
        });
        return data;
    },

    /** Logout and redirect to login page. */
    logout() {
        API.clearToken();
        window.location.href = '/';
    },

    /** Redirect to login if not authenticated. */
    requireAuth() {
        if (!this.isLoggedIn()) {
            window.location.href = '/';
            return false;
        }
        return true;
    },
};
