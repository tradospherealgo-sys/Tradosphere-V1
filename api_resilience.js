/**
 * API Resilience Layer
 *
 * Provides error handling, retry logic, timeouts, and graceful degradation
 * for all frontend → backend API calls.
 *
 * Ensures dashboard never crashes due to API issues.
 */

class APIResilience {
  constructor(baseAPI) {
    this.baseAPI = baseAPI;
    this.maxRetries = 3;
    this.retryDelay = 1000; // ms
    this.timeout = 10000; // ms
    this.cache = new Map();
    this.cacheExpiry = 60000; // 1 minute
    this.healthCheckInterval = 30000; // 30 seconds
    this.lastHealthStatus = null;
    this.startHealthCheck();
  }

  /**
   * Standardized API response format
   */
  createResponse(status, data, error = null) {
    return {
      status: status, // 'success', 'error', 'degraded', 'offline'
      data: data || {},
      error: error || null,
      timestamp: new Date().toISOString(),
      cached: false
    };
  }

  /**
   * Execute API call with retry logic and timeout
   */
  async callWithRetry(method, path, body = null) {
    let lastError = null;

    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        const result = await this.callWithTimeout(method, path, body);
        return this.createResponse('success', result);
      } catch (error) {
        lastError = error;

        // Don't retry on auth errors or not found
        if (error.status === 401 || error.status === 404) {
          break;
        }

        // Wait before retrying
        if (attempt < this.maxRetries) {
          await new Promise(r => setTimeout(r, this.retryDelay));
        }
      }
    }

    return this.createResponse('error', null, {
      message: lastError?.message || 'API call failed after retries',
      status: lastError?.status || 503
    });
  }

  /**
   * Execute API call with timeout
   */
  async callWithTimeout(method, path, body) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeout);

    try {
      let response;

      if (method === 'GET') {
        response = await this.baseAPI.get(path);
      } else if (method === 'POST') {
        response = await fetch(`${this.baseAPI.baseURL}${path}`, {
          method: 'POST',
          headers: this.baseAPI.getHeaders(),
          body: JSON.stringify(body),
          signal: controller.signal
        });

        if (!response.ok) {
          const error = new Error(`HTTP ${response.status}`);
          error.status = response.status;
          throw error;
        }

        return response.json();
      }

      return response;
    } finally {
      clearTimeout(timeout);
    }
  }

  /**
   * Generate signal with fallback
   */
  async generateSignal(symbol) {
    const cacheKey = `signal_${symbol}`;

    // Check cache first
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.time < this.cacheExpiry) {
        const response = this.createResponse('success', cached.data);
        response.cached = true;
        return response;
      }
    }

    try {
      const signal = await this.baseAPI.generateSignal(symbol);

      // Cache successful response
      this.cache.set(cacheKey, {
        data: signal,
        time: Date.now()
      });

      return this.createResponse('success', signal);
    } catch (error) {
      // Return fallback signal structure
      return this.createResponse('degraded', this.getFallbackSignal(symbol), {
        message: 'Using fallback signal - backend unavailable',
        reason: error.message
      });
    }
  }

  /**
   * Get signal history with fallback
   */
  async getSignalHistory(symbol) {
    try {
      const history = await this.baseAPI.getSignalHistory(symbol);
      return this.createResponse('success', history);
    } catch (error) {
      return this.createResponse('degraded', [], {
        message: 'Signal history unavailable',
        reason: error.message
      });
    }
  }

  /**
   * Get performance metrics with fallback
   */
  async getPerformance(symbol = null) {
    try {
      const performance = await this.baseAPI.getSignalPerformance(symbol);
      return this.createResponse('success', performance);
    } catch (error) {
      return this.createResponse('degraded', this.getFallbackPerformance(), {
        message: 'Performance metrics unavailable',
        reason: error.message
      });
    }
  }

  /**
   * Get market data with fallback
   */
  async getMarketData() {
    try {
      const data = await this.baseAPI.getLiveMarketData();
      return this.createResponse('success', data);
    } catch (error) {
      return this.createResponse('degraded', this.getFallbackMarketData(), {
        message: 'Market data unavailable - using cached values',
        reason: error.message
      });
    }
  }

  /**
   * Fallback signal when backend is unavailable
   */
  getFallbackSignal(symbol) {
    return {
      symbol: symbol,
      direction: 'WAIT',
      confidence: 0,
      entry: null,
      target: null,
      stop_loss: null,
      setup: 'N/A',
      trend: 'UNKNOWN',
      quality_score: { tech: 0, options: 0, market: 0 },
      reasons: ['Market data unavailable - signal generation paused'],
      status: 'UNAVAILABLE'
    };
  }

  /**
   * Fallback performance metrics
   */
  getFallbackPerformance() {
    return {
      symbol: 'ALL',
      total_signals: 0,
      executed: 0,
      pending: 0,
      winning_trades: 0,
      losing_trades: 0,
      win_rate: 0,
      message: 'Performance metrics unavailable',
      status: 'UNAVAILABLE'
    };
  }

  /**
   * Fallback market data
   */
  getFallbackMarketData() {
    return {
      nifty: { symbol: 'NIFTY', ltp: null, change: null, status: 'unavailable' },
      banknifty: { symbol: 'BANKNIFTY', ltp: null, change: null, status: 'unavailable' },
      finnifty: { symbol: 'FINNIFTY', ltp: null, change: null, status: 'unavailable' },
      message: 'Market data unavailable - markets may be closed'
    };
  }

  /**
   * Check backend health
   */
  async getHealth() {
    try {
      const response = await fetch(`${this.baseAPI.baseURL}/api/health`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: AbortSignal.timeout(5000)
      });

      if (!response.ok) {
        return this.createResponse('error', null, {
          message: `Backend returned ${response.status}`,
          status: response.status
        });
      }

      const data = await response.json();
      return this.createResponse('success', data);
    } catch (error) {
      return this.createResponse('error', null, {
        message: 'Cannot reach backend',
        reason: error.message
      });
    }
  }

  /**
   * Periodic health check
   */
  startHealthCheck() {
    setInterval(async () => {
      const health = await this.getHealth();
      this.lastHealthStatus = health.status;

      // Could emit event here for UI to display backend status
      if (health.status === 'error') {
        console.warn('Backend health check failed:', health.error);
      }
    }, this.healthCheckInterval);
  }

  /**
   * Get last known health status
   */
  getLastHealthStatus() {
    return this.lastHealthStatus;
  }

  /**
   * Clear cache (manual refresh)
   */
  clearCache() {
    this.cache.clear();
  }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
  module.exports = APIResilience;
}
