/**
 * Tradosphere Production Configuration
 * Frontend → Railway Backend
 */

// Production Railway Backend
window.API_BASE_URL = "https://tradosphere-v1-production.up.railway.app";

// Development fallback (optional)
if (
    window.location.hostname === "localhost" ||
    window.location.hostname === "127.0.0.1"
) {
    window.API_BASE_URL = "http://localhost:8000";
}

// Debug information
console.log("====================================");
console.log("🚀 TRADOSPHERE CONFIG LOADED");
console.log("🌐 API URL:", window.API_BASE_URL);
console.log("🌍 Host:", window.location.hostname);
console.log("====================================");
