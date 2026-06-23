/**
 * Tradosphere API Client
 * Handles all API requests with token management and error handling
 */

const API_CLIENT = {
    baseURL: '/api',

    /**
     * Get JWT token from localStorage
     */
    getToken() {
        return localStorage.getItem('jwt_token');
    },

    /**
     * Get user role from localStorage
     */
    getUserRole() {
        return localStorage.getItem('user_role');
    },

    /**
     * Set authentication token
     */
    setToken(token, role = 'user') {
        localStorage.setItem('jwt_token', token);
        localStorage.setItem('user_role', role);
    },

    /**
     * Clear authentication token
     */
    clearToken() {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('user_role');
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated() {
        return !!this.getToken();
    },

    /**
     * Check if user is admin
     */
    isAdmin() {
        return this.getUserRole() === 'admin';
    },

    /**
     * Generic API request handler
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        };

        const token = this.getToken();
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            });

            // Handle 401 Unauthorized
            if (response.status === 401) {
                this.clearToken();
                window.location.href = '/login';
                return { status: 'error', message: 'Session expired' };
            }

            const data = await response.json();

            if (!response.ok) {
                console.error(`API Error: ${endpoint}`, data);
            }

            return data;
        } catch (error) {
            console.error(`Network Error: ${endpoint}`, error);
            return {
                status: 'error',
                message: 'Network error occurred',
                error: error.message
            };
        }
    },

    /**
     * GET request
     */
    get(endpoint, options = {}) {
        return this.request(endpoint, {
            method: 'GET',
            ...options
        });
    },

    /**
     * POST request
     */
    post(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
            ...options
        });
    },

    /**
     * PUT request
     */
    put(endpoint, data = {}, options = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
            ...options
        });
    },

    /**
     * DELETE request
     */
    delete(endpoint, options = {}) {
        return this.request(endpoint, {
            method: 'DELETE',
            ...options
        });
    },

    /**
     * Auth endpoints
     */
    auth: {
        login(email, password) {
            return API_CLIENT.post('/auth/login', { email, password });
        },

        googleCallback(code) {
            return API_CLIENT.post('/auth/google/callback', { code });
        },

        logout() {
            return API_CLIENT.post('/auth/logout');
        },

        refreshToken() {
            return API_CLIENT.post('/auth/refresh-token');
        }
    },

    /**
     * User endpoints
     */
    user: {
        getDashboard() {
            return API_CLIENT.get('/user/dashboard-overview');
        },

        getProfile() {
            return API_CLIENT.get('/user/profile');
        },

        updateProfile(data) {
            return API_CLIENT.put('/user/profile', data);
        },

        getSubscription() {
            return API_CLIENT.get('/user/subscription');
        },

        getBillingHistory() {
            return API_CLIENT.get('/user/billing-history');
        },

        getWatchlist() {
            return API_CLIENT.get('/user/watchlist');
        },

        addToWatchlist(symbol) {
            return API_CLIENT.post('/user/watchlist', { symbol });
        },

        removeFromWatchlist(symbol) {
            return API_CLIENT.delete(`/user/watchlist/${symbol}`);
        },

        getActivity() {
            return API_CLIENT.get('/user/activity');
        }
    },

    /**
     * Trading endpoints
     */
    trading: {
        createTrade(data) {
            return API_CLIENT.post('/trading/create-trade', data);
        },

        getOpenTrades() {
            return API_CLIENT.get('/trading/open-trades');
        },

        closeTrade(tradeId) {
            return API_CLIENT.post(`/trading/close-trade/${tradeId}`);
        },

        getTradeHistory() {
            return API_CLIENT.get('/trading/history');
        }
    },

    /**
     * Signal endpoints
     */
    signals: {
        generate(symbol = 'NIFTY') {
            return API_CLIENT.post('/signals/generate', { symbol });
        },

        getSignals() {
            return API_CLIENT.get('/signals');
        },

        getSignalById(signalId) {
            return API_CLIENT.get(`/signals/${signalId}`);
        },

        getSignalPerformance() {
            return API_CLIENT.get('/signals/performance');
        }
    },

    /**
     * Market endpoints
     */
    market: {
        getOverview() {
            return API_CLIENT.get('/market/overview');
        },

        getSymbolData(symbol) {
            return API_CLIENT.get(`/market/${symbol}`);
        },

        getOptionsChain(symbol) {
            return API_CLIENT.get(`/market/${symbol}/options-chain`);
        },

        getHistoricalData(symbol, interval = '1d') {
            return API_CLIENT.get(`/market/${symbol}/historical?interval=${interval}`);
        }
    },

    /**
     * Backtest endpoints
     */
    backtest: {
        runBacktest(data) {
            return API_CLIENT.post('/backtest/run', data);
        },

        getBacktestResults(testId) {
            return API_CLIENT.get(`/backtest/${testId}`);
        },

        listBacktests() {
            return API_CLIENT.get('/backtest/list');
        }
    },

    /**
     * Admin endpoints
     */
    admin: {
        getDashboard() {
            return API_CLIENT.get('/admin/dashboard');
        },

        getUsers(page = 1) {
            return API_CLIENT.get(`/admin/users?page=${page}`);
        },

        getUserDetail(userId) {
            return API_CLIENT.get(`/admin/users/${userId}`);
        },

        disableUser(userId) {
            return API_CLIENT.post(`/admin/users/${userId}/disable`);
        },

        enableUser(userId) {
            return API_CLIENT.post(`/admin/users/${userId}/enable`);
        },

        getSubscriptions() {
            return API_CLIENT.get('/admin/subscriptions');
        },

        getAnalytics(startDate, endDate) {
            return API_CLIENT.get(`/admin/analytics?start=${startDate}&end=${endDate}`);
        },

        getSignals() {
            return API_CLIENT.get('/admin/signals');
        }
    },

    /**
     * Health check endpoints
     */
    health: {
        check() {
            return API_CLIENT.get('/health');
        },

        detailed() {
            return API_CLIENT.get('/health/detailed');
        }
    }
};

/**
 * Utility function to show toast notifications
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 15px 20px;
        background: ${
            type === 'success' ? '#10b981' :
            type === 'error' ? '#ef4444' :
            type === 'warning' ? '#f59e0b' :
            '#3b82f6'
        };
        color: white;
        border-radius: 6px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

/**
 * Format currency value
 */
function formatCurrency(value, currency = 'INR') {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: currency
    }).format(value);
}

/**
 * Format percentage
 */
function formatPercent(value, decimals = 2) {
    return (value).toFixed(decimals) + '%';
}

/**
 * Format date
 */
function formatDate(date, locale = 'en-IN') {
    return new Date(date).toLocaleDateString(locale);
}

/**
 * Format date and time
 */
function formatDateTime(date, locale = 'en-IN') {
    return new Date(date).toLocaleString(locale);
}

/**
 * Redirect to login if not authenticated
 */
function requireAuth() {
    if (!API_CLIENT.isAuthenticated()) {
        window.location.href = '/login';
    }
}

/**
 * Redirect to login if not admin
 */
function requireAdmin() {
    if (!API_CLIENT.isAuthenticated() || !API_CLIENT.isAdmin()) {
        window.location.href = '/login';
    }
}

/**
 * Add animation styles
 */
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);
