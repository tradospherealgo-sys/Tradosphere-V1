# 🌐 TEST ANGEL ONE API VIA BROWSER CONSOLE

## Open Your Browser (Chrome, Gemini, etc.)

1. Press **F12** to open Developer Tools
2. Go to **Console** tab
3. Copy and paste the code below:

```javascript
const apiKey = "oQbQqRnb";
const apiSecret = "LOY3MAKP5U4B3LLQMXJP3XIFEM";
const clientCode = "A972731";

console.log("🔐 Testing Angel One API from Browser Console...");

const payload = {
  clientcode: clientCode,
  password: apiSecret,
  totp: "000000"
};

console.log("Sending request to: https://apiconnect.angelone.in/rest/secure/login");
console.log("Payload:", payload);

fetch("https://apiconnect.angelone.in/rest/secure/login", {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${apiKey}`,
    "Content-Type": "application/json"
  },
  body: JSON.stringify(payload)
})
.then(response => {
  console.log("✅ Response Status:", response.status);
  console.log("✅ Response Headers:", response.headers);
  return response.text();
})
.then(data => {
  console.log("📋 Response Data:", data);
  try {
    const json = JSON.parse(data);
    console.log("✅ JSON Parsed:", json);
  } catch(e) {
    console.log("❌ Not JSON - Raw HTML/Text response");
  }
})
.catch(error => {
  console.error("❌ Error:", error);
});
```

4. Press **Enter** and watch the console output

---

## 📋 WHAT TO CHECK

After running the test, check:

1. **✅ Is response status 200?** (or 401/403?)
2. **📋 Is response JSON or HTML?**
3. **💭 What does the response say?**

---

## 🔍 TROUBLESHOOTING

### If you get "Request Rejected" HTML:
- API credentials might not be active
- Check Angel One account - are these credentials REALLY valid?
- Try logging into Angel One dashboard with the same credentials
- Check if API access is enabled on the account

### If you get CORS error:
- Browser blocking request (API doesn't allow browser requests)
- Need to use backend server instead (which we're doing)

### If you get 401/403:
- Credentials are invalid
- Check Angel One API Keys page again

---

## 💡 NEXT STEP

**Based on the response you get, tell me:**
1. What is the exact response (copy-paste from console)
2. Is it JSON or HTML?
3. What error message?

Then we can fix the market_data.py accordingly!

