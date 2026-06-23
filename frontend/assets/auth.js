/**
 * Authentication Utilities
 * Handles login, logout, and session management
 */

const AUTH = {
    /**
     * Initialize Google OAuth
     */
    initGoogleOAuth(clientId) {
        const script = document.createElement('script');
        script.src = 'https://accounts.google.com/gsi/client';
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);

        window.onGoogleLibraryLoad = function() {
            google.accounts.id.initialize({
                client_id: clientId,
                callback: AUTH.handleGoogleCallback
            });
        };
    },

    /**
     * Handle Google OAuth callback
     */
    async handleGoogleCallback(response) {
        try {
            const result = await API_CLIENT.auth.googleCallback(response.credential);

            if (result.status === 'success') {
                API_CLIENT.setToken(result.data.token, result.data.role);
                showToast('Login successful!', 'success');

                // Redirect based on role
                const redirectUrl = result.data.role === 'admin' ? '/admin/dashboard' : '/user/dashboard';
                setTimeout(() => {
                    window.location.href = redirectUrl;
                }, 500);
            } else {
                showToast(result.message || 'Login failed', 'error');
            }
        } catch (error) {
            console.error('OAuth error:', error);
            showToast('Login error occurred', 'error');
        }
    },

    /**
     * Render Google Sign-In button
     */
    renderGoogleButton(containerId) {
        if (typeof google !== 'undefined' && google.accounts) {
            google.accounts.id.renderButton(
                document.getElementById(containerId),
                {
                    theme: 'outline',
                    size: 'large',
                    width: '100%'
                }
            );
        }
    },

    /**
     * Email/password login
     */
    async login(email, password) {
        try {
            const result = await API_CLIENT.auth.login(email, password);

            if (result.status === 'success') {
                API_CLIENT.setToken(result.data.token, result.data.role);
                showToast('Login successful!', 'success');

                const redirectUrl = result.data.role === 'admin' ? '/admin/dashboard' : '/user/dashboard';
                setTimeout(() => {
                    window.location.href = redirectUrl;
                }, 500);
                return true;
            } else {
                showToast(result.message || 'Login failed', 'error');
                return false;
            }
        } catch (error) {
            console.error('Login error:', error);
            showToast('Login error occurred', 'error');
            return false;
        }
    },

    /**
     * Logout
     */
    async logout() {
        try {
            await API_CLIENT.auth.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            API_CLIENT.clearToken();
            window.location.href = '/login';
        }
    },

    /**
     * Check authentication and redirect if needed
     */
    checkAuth(allowRoles = ['user', 'admin']) {
        if (!API_CLIENT.isAuthenticated()) {
            window.location.href = '/login';
            return false;
        }

        const role = API_CLIENT.getUserRole();
        if (!allowRoles.includes(role)) {
            window.location.href = '/login';
            return false;
        }

        return true;
    },

    /**
     * Check admin access
     */
    checkAdmin() {
        if (!API_CLIENT.isAdmin()) {
            window.location.href = '/user/dashboard';
            return false;
        }
        return true;
    },

    /**
     * Verify token validity with server
     */
    async verifyToken() {
        try {
            const result = await API_CLIENT.get('/auth/verify');
            return result.status === 'success';
        } catch (error) {
            return false;
        }
    },

    /**
     * Refresh token
     */
    async refreshToken() {
        try {
            const result = await API_CLIENT.auth.refreshToken();
            if (result.status === 'success') {
                API_CLIENT.setToken(result.data.token, API_CLIENT.getUserRole());
                return true;
            }
            return false;
        } catch (error) {
            console.error('Token refresh error:', error);
            return false;
        }
    },

    /**
     * Validate email format
     */
    validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    },

    /**
     * Validate password strength
     */
    validatePassword(password) {
        // At least 8 characters, 1 uppercase, 1 lowercase, 1 number
        return password.length >= 8 &&
               /[A-Z]/.test(password) &&
               /[a-z]/.test(password) &&
               /[0-9]/.test(password);
    },

    /**
     * Get password strength meter
     */
    getPasswordStrength(password) {
        let strength = 0;

        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/[0-9]/.test(password)) strength++;
        if (/[^A-Za-z0-9]/.test(password)) strength++;

        return {
            score: strength,
            level: strength <= 1 ? 'weak' : strength <= 2 ? 'fair' : strength <= 3 ? 'good' : strength <= 4 ? 'strong' : 'very-strong',
            message: strength <= 1 ? 'Weak' : strength <= 2 ? 'Fair' : strength <= 3 ? 'Good' : strength <= 4 ? 'Strong' : 'Very Strong'
        };
    }
};

/**
 * Session timeout handler
 */
class SessionManager {
    constructor(timeoutMinutes = 30) {
        this.timeoutMinutes = timeoutMinutes;
        this.warningMinutes = 5;
        this.timeoutId = null;
        this.warningId = null;

        if (API_CLIENT.isAuthenticated()) {
            this.startSession();
        }
    }

    startSession() {
        this.resetTimeout();
        document.addEventListener('mousedown', () => this.resetTimeout());
        document.addEventListener('keydown', () => this.resetTimeout());
    }

    resetTimeout() {
        clearTimeout(this.timeoutId);
        clearTimeout(this.warningId);

        this.warningId = setTimeout(() => {
            this.showWarning();
        }, (this.timeoutMinutes - this.warningMinutes) * 60 * 1000);

        this.timeoutId = setTimeout(() => {
            this.logout();
        }, this.timeoutMinutes * 60 * 1000);
    }

    showWarning() {
        showToast(`Your session will expire in ${this.warningMinutes} minutes. Stay active to continue.`, 'warning', 10000);
    }

    logout() {
        AUTH.logout();
    }

    extendSession() {
        this.resetTimeout();
        showToast('Session extended', 'success');
    }
}

// Initialize session manager if authenticated
if (API_CLIENT.isAuthenticated()) {
    window.sessionManager = new SessionManager(30);
}
