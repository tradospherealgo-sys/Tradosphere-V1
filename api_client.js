/**
 * Tradosphere API Client
 * Unified API client for all dashboard communication with the Flask backend
 *
 * Usage in HTML:
 * <script src="api_client.js"></script>
 *
 * Then in your code:
 * const api = new TradosphereAPI('http://localhost:8000');
 * const user = await api.getProfile();
 */

class TradosphereAPI {
  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
    this.token = this.loadToken();
    this.cache = new Map();
    this.cacheExpiry = 60000; // 1 minute default cache
  }

  // ==================== AUTH METHODS ====================

  /**
   * Sign up a new user
   */
  async signup(email, password, firstName, lastName) {
    return this.post('/api/auth/signup', {
      email,
      password,
      first_name: firstName,
      last_name: lastName
    });
  }

  /**
   * Login user and store token
   */
  async login(email, password) {
    const response = await this.post('/api/auth/login', { email, password });
    if (response.access_token) {
      this.saveToken(response.access_token);
      this.token = response.access_token;
    }
    return response;
  }

  /**
   * Get current user info
   */
  async getMe() {
    return this.get('/api/auth/me');
  }

  /**
   * Logout (clear token)
   */
  logout() {
    this.clearToken();
    this.token = null;
  }

  // ==================== USER METHODS ====================

  /**
   * Get user profile
   */
  async getProfile() {
    return this.get('/api/user/profile');
  }

  /**
   * Get user dashboard overview
   */
  async getDashboardOverview() {
    return this.get('/api/user/dashboard-overview', { cache: true });
  }

  /**
   * Get user portfolio data
   */
  async getPortfolio() {
    return this.get('/api/user/portfolio');
  }

  /**
   * Update user profile
   */
  async updateProfile(data) {
    return this.post('/api/user/profile', data);
  }

  // ==================== MARKET DATA METHODS ====================

  /**
   * Get live market data (NIFTY, BANKNIFTY)
   */
  async getLiveMarketData() {
    return this.get('/api/market/live', { cache: true });
  }

  /**
   * Get symbol quote
   */
  async getQuote(symbol) {
    return this.get(`/api/market/quote/${symbol}`);
  }

  /**
   * Get market status
   */
  async getMarketStatus() {
    return this.get('/api/market/status', { cache: true });
  }

  /**
   * Get price history
   */
  async getPriceHistory(symbol, interval = '5min', limit = 100) {
    return this.get('/api/market/history', {
      params: { symbol, interval, limit },
      cache: true
    });
  }

  /**
   * Stream live prices (WebSocket)
   */
  openPriceStream(symbols, callback) {
    const wsURL = this.baseURL.replace('http', 'ws') + '/ws/prices';
    const ws = new WebSocket(wsURL);

    ws.onopen = () => {
      ws.send(JSON.stringify({ action: 'subscribe', symbols }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(null, data);
    };

    ws.onerror = (error) => {
      callback(error);
    };

    return ws;
  }

  // ==================== TRADING METHODS ====================

  /**
   * Get open trades
   */
  async getOpenTrades() {
    return this.get('/api/trading/open-trades');
  }

  /**
   * Get closed trades
   */
  async getClosedTrades(limit = 50) {
    return this.get('/api/trading/closed-trades', {
      params: { limit }
    });
  }

  /**
   * Get pending approval trades
   */
  async getPendingTrades() {
    return this.get('/api/trading/pending-approval');
  }

  /**
   * Get trading statistics
   */
  async getTradingStats() {
    return this.get('/api/trading/stats', { cache: true });
  }

  /**
   * Create a new trade
   */
  async createTrade(symbol, direction, entryPrice, targetPrice, stopLoss, quantity = 1) {
    return this.post('/api/trading/create-trade', {
      symbol,
      direction, // BUY_CALL, BUY_PUT, SELL_CALL, SELL_PUT
      entry_price: entryPrice,
      target_price: targetPrice,
      stop_loss: stopLoss,
      quantity
    });
  }

  /**
   * Approve a pending trade
   */
  async approveTrade(tradeId) {
    return this.post(`/api/trading/approve/${tradeId}`, {});
  }

  /**
   * Reject a pending trade
   */
  async rejectTrade(tradeId, reason = '') {
    return this.post(`/api/trading/reject/${tradeId}`, { reason });
  }

  /**
   * Close an open trade
   */
  async closeTrade(tradeId, exitPrice) {
    return this.post(`/api/trading/close/${tradeId}`, { exit_price: exitPrice });
  }

  /**
   * Update trade stop loss or target
   */
  async updateTrade(tradeId, targetPrice = null, stopLoss = null) {
    return this.post(`/api/trading/update/${tradeId}`, {
      target_price: targetPrice,
      stop_loss: stopLoss
    });
  }

  /**
   * Get trade details
   */
  async getTrade(tradeId) {
    return this.get(`/api/trading/trade/${tradeId}`);
  }

  // ==================== SIGNALS METHODS ====================

  /**
   * Get all signals
   */
  async getSignals(limit = 50) {
    return this.get('/api/signals', { params: { limit } });
  }

  /**
   * Generate a new signal
   */
  async generateSignal(symbol, entryPrice, targetPrice, stopLoss) {
    return this.post('/api/signals/generate', {
      symbol,
      entry: entryPrice,
      target: targetPrice,
      stoploss: stopLoss
    });
  }

  /**
   * Get signal by ID
   */
  async getSignal(signalId) {
    return this.get(`/api/signals/${signalId}`);
  }

  /**
   * Execute a signal as a trade
   */
  async executeSignal(signalId) {
    return this.post(`/api/signals/execute/${signalId}`, {});
  }

  /**
   * Generate signals for multiple symbols (System B unified endpoint)
   * Returns identical signals across dashboard, terminal, API
   */
  async generateSignalsBatch(symbols = ['NIFTY', 'BANKNIFTY', 'FINNIFTY']) {
    return this.post('/api/signals/batch-generate', {
      symbols
    });
  }

  /**
   * Get signal history for a specific symbol
   * Shows all generated signals for NIFTY, BANKNIFTY, or FINNIFTY
   */
  async getSignalHistory(symbol, limit = 20) {
    if (!['NIFTY', 'BANKNIFTY', 'FINNIFTY'].includes(symbol)) {
      throw new Error(`Invalid symbol: ${symbol}`);
    }
    return this.get(`/api/signals/history/${symbol}`, {
      params: { limit }
    });
  }

  /**
   * Get signal performance metrics
   * Win rate, accuracy, P&L tracking
   * Symbol is optional - if not provided, returns all symbols
   */
  async getSignalPerformance(symbol = null) {
    const params = {};
    if (symbol) params.symbol = symbol;
    return this.get('/api/signals/performance', { params });
  }

  /**
   * Validate signal consistency across systems
   * Ensures dashboard, terminal, API generate identical signals
   * Used to verify System B single source of truth
   */
  async validateSignalConsistency(symbol, externalSignal) {
    return this.post('/api/signals/validate-consistency', {
      symbol,
      signal: externalSignal
    });
  }

  // ==================== ANALYSIS METHODS ====================

  /**
   * Get technical analysis for symbol
   */
  async getTechnicalAnalysis(symbol) {
    return this.get('/api/analysis/technical', {
      params: { symbol },
      cache: true
    });
  }

  /**
   * Get options analysis for symbol
   */
  async getOptionsAnalysis(symbol) {
    return this.get('/api/analysis/options', {
      params: { symbol },
      cache: true
    });
  }

  /**
   * Get AI insights for symbol
   */
  async getAIInsights(symbol) {
    return this.get('/api/analysis/ai-insights', {
      params: { symbol },
      cache: true
    });
  }

  /**
   * Get market trends
   */
  async getMarketTrends() {
    return this.get('/api/analysis/trends', { cache: true });
  }

  /**
   * Get sentiment analysis
   */
  async getSentiment(symbol) {
    return this.get('/api/analysis/sentiment', {
      params: { symbol },
      cache: true
    });
  }

  // ==================== PAPER TRADING METHODS ====================

  /**
   * Get paper trading account
   */
  async getPaperTradingAccount() {
    return this.get('/api/paper-trading/account');
  }

  /**
   * Get paper trading history
   */
  async getPaperTradingHistory() {
    return this.get('/api/paper-trading/history');
  }

  /**
   * Execute paper trade
   */
  async executePaperTrade(symbol, direction, quantity, price) {
    return this.post('/api/paper-trading/execute', {
      symbol,
      direction,
      quantity,
      price
    });
  }

  /**
   * Reset paper trading account
   */
  async resetPaperTradingAccount(initialBalance = 100000) {
    return this.post('/api/paper-trading/reset', { initial_balance: initialBalance });
  }

  // ==================== HEALTH & STATUS METHODS ====================

  /**
   * Get system health status
   */
  async getHealth() {
    return this.get('/api/health');
  }

  /**
   * Get detailed system status
   */
  async getHealthDetailed() {
    return this.get('/api/health/detailed');
  }

  /**
   * Get system status
   */
  async getStatus() {
    return this.get('/api/status');
  }

  // ==================== SUBSCRIPTION METHODS ====================

  /**
   * Get user subscription
   */
  async getSubscription() {
    return this.get('/api/subscription');
  }

  /**
   * Get available plans
   */
  async getPlans() {
    return this.get('/api/plans', { cache: true });
  }

  /**
   * Create subscription
   */
  async createSubscription(planId, billingCycle = 'monthly') {
    return this.post('/api/subscription', {
      plan_id: planId,
      billing_cycle: billingCycle
    });
  }

  /**
   * Cancel subscription
   */
  async cancelSubscription() {
    return this.post('/api/subscription/cancel', {});
  }

  // ==================== WEBHOOK METHODS ====================

  /**
   * Verify webhook signature
   */
  verifyWebhookSignature(payload, signature, secret) {
    const crypto = require('crypto');
    const hash = crypto.createHmac('sha256', secret)
      .update(JSON.stringify(payload))
      .digest('hex');
    return hash === signature;
  }

  // ==================== INTERNAL HTTP METHODS ====================

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    const { params = {}, cache = false } = options;
    const cacheKey = endpoint + JSON.stringify(params);

    // Check cache
    if (cache && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheExpiry) {
        return cached.data;
      }
    }

    let url = `${this.baseURL}${endpoint}`;
    if (Object.keys(params).length > 0) {
      const queryString = new URLSearchParams(params).toString();
      url += `?${queryString}`;
    }

    const response = await fetch(url, {
      method: 'GET',
      headers: this.getHeaders()
    });

    const data = await this.handleResponse(response);

    // Cache result
    if (cache) {
      this.cache.set(cacheKey, {
        data,
        timestamp: Date.now()
      });
    }

    return data;
  }

  /**
   * POST request
   */
  async post(endpoint, body = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(body)
    });

    return this.handleResponse(response);
  }

  /**
   * PUT request
   */
  async put(endpoint, body = {}) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'PUT',
      headers: this.getHeaders(),
      body: JSON.stringify(body)
    });

    return this.handleResponse(response);
  }

  /**
   * DELETE request
   */
  async delete(endpoint) {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      method: 'DELETE',
      headers: this.getHeaders()
    });

    return this.handleResponse(response);
  }

  /**
   * Get request headers with authentication
   */
  getHeaders() {
    const headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  /**
   * Handle API response
   */
  async handleResponse(response) {
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      const error = new Error(data.message || `API error: ${response.statusText}`);
      error.status = response.status;
      error.data = data;
      throw error;
    }

    return data;
  }

  // ==================== TOKEN MANAGEMENT ====================

  /**
   * Save token to localStorage
   */
  saveToken(token) {
    localStorage.setItem('tradosphere_token', token);
  }

  /**
   * Load token from localStorage
   */
  loadToken() {
    return localStorage.getItem('tradosphere_token');
  }

  /**
   * Clear token from localStorage
   */
  clearToken() {
    localStorage.removeItem('tradosphere_token');
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated() {
    return !!this.token;
  }

  // ==================== UTILITY METHODS ====================

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * Format currency
   */
  static formatCurrency(value) {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR'
    }).format(value);
  }

  /**
   * Format percentage
   */
  static formatPercentage(value, decimals = 2) {
    return (parseFloat(value) || 0).toFixed(decimals) + '%';
  }

  /**
   * Format date
   */
  static formatDate(date) {
    return new Intl.DateTimeFormat('en-IN').format(new Date(date));
  }

  /**
   * Format datetime
   */
  static formatDateTime(date) {
    return new Intl.DateTimeFormat('en-IN', {
      dateStyle: 'short',
      timeStyle: 'short'
    }).format(new Date(date));
  }
}

// Export for use in Node.js
if (typeof module !== 'undefined' && module.exports) {
  module.exports = TradosphereAPI;
}
