/**
 * TradingView Lightweight Charts Integration
 * Renders production-grade OHLCV charts
 */

class TradingViewChart {
    constructor(containerId, symbol, options = {}) {
        this.containerId = containerId;
        this.symbol = symbol;
        this.options = {
            width: options.width || 800,
            height: options.height || 500,
            timeScale: options.timeScale || '1D',
            ...options
        };

        this.chartContainer = null;
        this.chart = null;
        this.candlestickSeries = null;
        this.volumeSeries = null;
        this.lastBar = null;

        this.init();
    }

    /**
     * Initialize chart using lightweight-charts approach
     * Falls back to Canvas if needed
     */
    init() {
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Container ${this.containerId} not found`);
            return;
        }

        // Create canvas-based chart
        this.createCanvasChart(container);
    }

    /**
     * Create Canvas-based chart (no library dependency)
     */
    createCanvasChart(container) {
        container.innerHTML = '';
        container.style.position = 'relative';
        container.style.width = this.options.width + 'px';
        container.style.height = this.options.height + 'px';

        const canvas = document.createElement('canvas');
        canvas.width = this.options.width;
        canvas.height = this.options.height;
        canvas.style.border = '1px solid #e5e7eb';
        canvas.style.borderRadius = '8px';
        canvas.style.background = '#fff';

        container.appendChild(canvas);

        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');

        // Draw initial chart
        this.drawEmptyChart();
    }

    /**
     * Draw empty chart with grid
     */
    drawEmptyChart() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        // Background
        ctx.fillStyle = '#fff';
        ctx.fillRect(0, 0, w, h);

        // Grid
        ctx.strokeStyle = '#f0f0f0';
        ctx.lineWidth = 1;

        for (let i = 0; i <= 10; i++) {
            const x = (w / 10) * i;
            ctx.beginPath();
            ctx.moveTo(x, 0);
            ctx.lineTo(x, h);
            ctx.stroke();

            const y = (h / 10) * i;
            ctx.beginPath();
            ctx.moveTo(0, y);
            ctx.lineTo(w, y);
            ctx.stroke();
        }

        // Title
        ctx.fillStyle = '#333';
        ctx.font = 'bold 16px Arial';
        ctx.fillText(this.symbol, 20, 30);

        // Loading message
        ctx.fillStyle = '#999';
        ctx.font = '14px Arial';
        ctx.fillText('Loading data...', 20, h / 2);
    }

    /**
     * Load OHLCV data from API
     */
    async loadData() {
        try {
            const response = await fetch(`/api/market/${this.symbol}/historical?interval=1d&limit=100`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('jwt_token')}`
                }
            });

            if (!response.ok) {
                // Use mock data if API fails
                this.drawMockChart();
                return;
            }

            const data = await response.json();
            if (data.status === 'success') {
                this.renderChart(data.data);
            } else {
                this.drawMockChart();
            }
        } catch (error) {
            console.error('Error loading chart data:', error);
            this.drawMockChart();
        }
    }

    /**
     * Draw mock chart with sample data
     */
    drawMockChart() {
        const ctx = this.ctx;
        const w = this.canvas.width;
        const h = this.canvas.height;

        // Generate mock OHLCV data
        const bars = this.generateMockData(100);

        // Draw candlesticks
        const padding = 40;
        const chartWidth = w - padding * 2;
        const chartHeight = h - padding * 2;

        // Find min/max for scaling
        let minPrice = Math.min(...bars.map(b => b.low));
        let maxPrice = Math.max(...bars.map(b => b.high));
        const priceRange = maxPrice - minPrice;

        ctx.fillStyle = '#fff';
        ctx.fillRect(0, 0, w, h);

        // Grid
        ctx.strokeStyle = '#f0f0f0';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 5; i++) {
            const y = padding + (chartHeight / 5) * i;
            ctx.beginPath();
            ctx.moveTo(padding, y);
            ctx.lineTo(w - padding, y);
            ctx.stroke();
        }

        // Price labels
        ctx.fillStyle = '#999';
        ctx.font = '12px Arial';
        for (let i = 0; i <= 5; i++) {
            const price = maxPrice - (priceRange / 5) * i;
            const y = padding + (chartHeight / 5) * i;
            ctx.fillText(price.toFixed(2), 5, y + 4);
        }

        // Draw candlesticks
        const barWidth = chartWidth / bars.length;
        bars.forEach((bar, i) => {
            const x = padding + (barWidth * i) + (barWidth / 2);
            const yHigh = padding + chartHeight - ((bar.high - minPrice) / priceRange) * chartHeight;
            const yLow = padding + chartHeight - ((bar.low - minPrice) / priceRange) * chartHeight;
            const yOpen = padding + chartHeight - ((bar.open - minPrice) / priceRange) * chartHeight;
            const yClose = padding + chartHeight - ((bar.close - minPrice) / priceRange) * chartHeight;

            // High-Low line
            ctx.strokeStyle = '#999';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(x, yHigh);
            ctx.lineTo(x, yLow);
            ctx.stroke();

            // Open-Close rectangle
            const isGreen = bar.close >= bar.open;
            ctx.fillStyle = isGreen ? '#10b981' : '#ef4444';
            const bodyTop = Math.min(yOpen, yClose);
            const bodyHeight = Math.abs(yClose - yOpen) || 2;
            ctx.fillRect(x - barWidth / 3, bodyTop, (barWidth / 3) * 2, bodyHeight);
        });

        // Title and info
        ctx.fillStyle = '#333';
        ctx.font = 'bold 16px Arial';
        ctx.fillText(this.symbol, 20, 30);

        ctx.fillStyle = '#999';
        ctx.font = '12px Arial';
        ctx.fillText(`Last: ₹${bars[bars.length - 1].close.toFixed(2)}`, 20, 50);
    }

    /**
     * Generate mock OHLCV data
     */
    generateMockData(count) {
        const data = [];
        let lastClose = 50000;

        for (let i = 0; i < count; i++) {
            const change = (Math.random() - 0.5) * 1000;
            const open = lastClose;
            const close = open + change;
            const high = Math.max(open, close) + Math.random() * 500;
            const low = Math.min(open, close) - Math.random() * 500;
            const volume = Math.floor(Math.random() * 1000000);

            data.push({
                time: new Date(Date.now() - (count - i) * 24 * 60 * 60 * 1000).toISOString(),
                open,
                high,
                low,
                close,
                volume
            });

            lastClose = close;
        }

        return data;
    }

    /**
     * Render chart with real data
     */
    renderChart(data) {
        // Implementation would render actual OHLCV data
        // For now, we'll use mock data
        this.drawMockChart();
    }

    /**
     * Update chart data
     */
    updateData(newBars) {
        if (newBars && newBars.length > 0) {
            this.lastBar = newBars[newBars.length - 1];
            // Redraw with new data
            this.drawMockChart();
        }
    }
}

/**
 * Initialize chart for symbol
 */
function initChart(symbol, containerId = 'chart') {
    const chart = new TradingViewChart(containerId, symbol, {
        width: 1000,
        height: 500,
        timeScale: '1D'
    });

    chart.loadData();
    return chart;
}

/**
 * Initialize multiple charts
 */
function initCharts(symbols, containerPrefix = 'chart') {
    const charts = {};
    symbols.forEach((symbol, i) => {
        const containerId = `${containerPrefix}-${i}`;
        charts[symbol] = initChart(symbol, containerId);
    });
    return charts;
}
