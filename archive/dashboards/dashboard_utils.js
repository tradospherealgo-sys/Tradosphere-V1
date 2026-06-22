/**
 * Dashboard Utilities
 * Helper functions and utilities for dashboard integration with Tradosphere API
 *
 * Usage:
 * <script src="api_client.js"></script>
 * <script src="dashboard_utils.js"></script>
 *
 * Then:
 * const dashboard = new DashboardManager();
 * await dashboard.initialize();
 */

class DashboardManager {
  constructor(apiBaseURL = 'http://localhost:8000') {
    this.api = new TradosphereAPI(apiBaseURL);
    this.user = null;
    this.isInitialized = false;
    this.eventListeners = {};
  }

  // ==================== INITIALIZATION ====================

  /**
   * Initialize dashboard - load user data and setup
   */
  async initialize() {
    try {
      // Check if user is authenticated
      if (!this.api.isAuthenticated()) {
        this.redirectToLogin();
        return false;
      }

      // Load user data
      await this.loadUserData();
      this.isInitialized = true;
      this.emit('initialized');
      return true;
    } catch (error) {
      console.error('Dashboard initialization failed:', error);
      this.redirectToLogin();
      return false;
    }
  }

  /**
   * Load all user data
   */
  async loadUserData() {
    try {
      this.user = await this.api.getMe();
      return this.user;
    } catch (error) {
      console.error('Failed to load user data:', error);
      throw error;
    }
  }

  /**
   * Refresh all dashboard data
   */
  async refreshDashboard() {
    try {
      this.api.clearCache(); // Clear cached data
      await this.loadUserData();
      this.emit('refreshed');
      return true;
    } catch (error) {
      console.error('Failed to refresh dashboard:', error);
      return false;
    }
  }

  // ==================== AUTHENTICATION ====================

  /**
   * Handle login
   */
  async handleLogin(email, password) {
    try {
      const response = await this.api.login(email, password);
      if (response.access_token) {
        await this.loadUserData();
        this.emit('logged-in');
        return true;
      }
      return false;
    } catch (error) {
      console.error('Login failed:', error);
      this.emit('login-error', error.message);
      return false;
    }
  }

  /**
   * Handle logout
   */
  handleLogout() {
    this.api.logout();
    this.user = null;
    this.isInitialized = false;
    this.redirectToLogin();
  }

  /**
   * Redirect to login page
   */
  redirectToLogin() {
    const loginURL = `${this.api.baseURL}/test/login`;
    window.location.href = loginURL;
  }

  // ==================== DATA LOADING ====================

  /**
   * Load dashboard overview
   */
  async loadDashboardOverview() {
    try {
      const data = await this.api.getDashboardOverview();
      this.emit('overview-loaded', data);
      return data;
    } catch (error) {
      console.error('Failed to load dashboard overview:', error);
      this.emit('error', { section: 'overview', error: error.message });
      return null;
    }
  }

  /**
   * Load live market data
   */
  async loadLiveMarketData() {
    try {
      const data = await this.api.getLiveMarketData();
      this.emit('market-data-loaded', data);
      return data;
    } catch (error) {
      console.error('Failed to load market data:', error);
      this.emit('error', { section: 'market-data', error: error.message });
      return null;
    }
  }

  /**
   * Load open trades
   */
  async loadOpenTrades() {
    try {
      const trades = await this.api.getOpenTrades();
      this.emit('trades-loaded', trades);
      return trades;
    } catch (error) {
      console.error('Failed to load trades:', error);
      this.emit('error', { section: 'trades', error: error.message });
      return [];
    }
  }

  /**
   * Load trading stats
   */
  async loadTradingStats() {
    try {
      const stats = await this.api.getTradingStats();
      this.emit('stats-loaded', stats);
      return stats;
    } catch (error) {
      console.error('Failed to load stats:', error);
      return null;
    }
  }

  /**
   * Load signals
   */
  async loadSignals(limit = 20) {
    try {
      const signals = await this.api.getSignals(limit);
      this.emit('signals-loaded', signals);
      return signals;
    } catch (error) {
      console.error('Failed to load signals:', error);
      this.emit('error', { section: 'signals', error: error.message });
      return [];
    }
  }

  /**
   * Load technical analysis
   */
  async loadTechnicalAnalysis(symbol) {
    try {
      const analysis = await this.api.getTechnicalAnalysis(symbol);
      this.emit('technical-analysis-loaded', analysis);
      return analysis;
    } catch (error) {
      console.error(`Failed to load technical analysis for ${symbol}:`, error);
      return null;
    }
  }

  /**
   * Load options analysis
   */
  async loadOptionsAnalysis(symbol) {
    try {
      const analysis = await this.api.getOptionsAnalysis(symbol);
      this.emit('options-analysis-loaded', analysis);
      return analysis;
    } catch (error) {
      console.error(`Failed to load options analysis for ${symbol}:`, error);
      return null;
    }
  }

  /**
   * Load AI insights
   */
  async loadAIInsights(symbol) {
    try {
      const insights = await this.api.getAIInsights(symbol);
      this.emit('ai-insights-loaded', insights);
      return insights;
    } catch (error) {
      console.error(`Failed to load AI insights for ${symbol}:`, error);
      return null;
    }
  }

  // ==================== TRADING OPERATIONS ====================

  /**
   * Create trade from form
   */
  async createTrade(formData) {
    try {
      const trade = await this.api.createTrade(
        formData.symbol,
        formData.direction,
        parseFloat(formData.entryPrice),
        parseFloat(formData.targetPrice),
        parseFloat(formData.stopLoss),
        parseInt(formData.quantity || 1)
      );
      this.emit('trade-created', trade);
      return trade;
    } catch (error) {
      console.error('Failed to create trade:', error);
      this.emit('error', { section: 'trade-creation', error: error.message });
      throw error;
    }
  }

  /**
   * Close trade
   */
  async closeTrade(tradeId, exitPrice) {
    try {
      const result = await this.api.closeTrade(tradeId, parseFloat(exitPrice));
      this.emit('trade-closed', result);
      return result;
    } catch (error) {
      console.error('Failed to close trade:', error);
      throw error;
    }
  }

  /**
   * Approve trade
   */
  async approveTrade(tradeId) {
    try {
      const result = await this.api.approveTrade(tradeId);
      this.emit('trade-approved', result);
      return result;
    } catch (error) {
      console.error('Failed to approve trade:', error);
      throw error;
    }
  }

  /**
   * Reject trade
   */
  async rejectTrade(tradeId, reason = '') {
    try {
      const result = await this.api.rejectTrade(tradeId, reason);
      this.emit('trade-rejected', result);
      return result;
    } catch (error) {
      console.error('Failed to reject trade:', error);
      throw error;
    }
  }

  // ==================== EVENT SYSTEM ====================

  /**
   * Register event listener
   */
  on(eventName, callback) {
    if (!this.eventListeners[eventName]) {
      this.eventListeners[eventName] = [];
    }
    this.eventListeners[eventName].push(callback);
  }

  /**
   * Unregister event listener
   */
  off(eventName, callback) {
    if (this.eventListeners[eventName]) {
      this.eventListeners[eventName] = this.eventListeners[eventName]
        .filter(cb => cb !== callback);
    }
  }

  /**
   * Emit event
   */
  emit(eventName, data = null) {
    console.log(`📢 Event: ${eventName}`, data);
    if (this.eventListeners[eventName]) {
      this.eventListeners[eventName].forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`Error in event listener for ${eventName}:`, error);
        }
      });
    }
  }

  // ==================== UI HELPERS ====================

  /**
   * Show loading spinner
   */
  showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = '<div class="spinner">Loading...</div>';
    }
  }

  /**
   * Show error message
   */
  showError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = `<div class="error">${message}</div>`;
    }
  }

  /**
   * Format currency value
   */
  formatCurrency(value) {
    return TradosphereAPI.formatCurrency(value);
  }

  /**
   * Format percentage value
   */
  formatPercentage(value, decimals = 2) {
    return TradosphereAPI.formatPercentage(value, decimals);
  }

  /**
   * Format date value
   */
  formatDate(date) {
    return TradosphereAPI.formatDate(date);
  }

  /**
   * Format datetime value
   */
  formatDateTime(date) {
    return TradosphereAPI.formatDateTime(date);
  }

  // ==================== REAL-TIME UPDATES ====================

  /**
   * Subscribe to price updates
   */
  subscribeToPrices(symbols, callback) {
    try {
      const ws = this.api.openPriceStream(symbols, (error, data) => {
        if (error) {
          console.error('WebSocket error:', error);
          callback(error, null);
        } else {
          callback(null, data);
        }
      });
      return ws;
    } catch (error) {
      console.error('Failed to subscribe to prices:', error);
      return null;
    }
  }

  /**
   * Unsubscribe from price updates
   */
  unsubscribeFromPrices(ws) {
    if (ws && ws.close) {
      ws.close();
    }
  }
}

// ==================== PAGE INITIALIZATION HELPER ====================

/**
 * Quick initialization for dashboard pages
 * Usage: await initializeDashboard();
 */
async function initializeDashboard(apiBaseURL = 'http://localhost:8000') {
  const dashboard = new DashboardManager(apiBaseURL);

  // Setup error handling
  dashboard.on('error', (error) => {
    console.error('Dashboard error:', error);
    // You can add UI error notification here
  });

  // Initialize
  const success = await dashboard.initialize();

  if (!success) {
    console.error('Failed to initialize dashboard');
    return null;
  }

  return dashboard;
}

/**
 * Login helper
 */
async function handleDashboardLogin(email, password, apiBaseURL = 'http://localhost:8000') {
  const api = new TradosphereAPI(apiBaseURL);
  return api.login(email, password);
}

/**
 * Logout helper
 */
function handleDashboardLogout(apiBaseURL = 'http://localhost:8000') {
  const api = new TradosphereAPI(apiBaseURL);
  api.logout();
  window.location.href = `${apiBaseURL}/test/login`;
}

// Export for Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    DashboardManager,
    initializeDashboard,
    handleDashboardLogin,
    handleDashboardLogout
  };
}
