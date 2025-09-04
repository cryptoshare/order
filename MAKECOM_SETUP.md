# make.com Webhook Setup Guide

## Quick Setup for Bybit Trading Bot

### 1. Webhook Endpoint
Your trading bot webhook endpoint will be:
```
http://your-server-ip:8080/
```

### 2. Webhook Configuration in make.com

1. **Add HTTP Request Module**
   - Method: `POST`
   - URL: `http://your-server-ip:8080/`
   - Headers: `Content-Type: application/json`

2. **Data Format**
   Send the trade decision in this exact JSON structure:

```json
{
  "intent": "trade_decision",
  "reply_markdown": "Your trade analysis here...",
  "trade": {
    "action": "open_limit",
    "reason": "Trade reasoning...",
    "confidence": 0.6,
    "symbol": "HYPE/USDT",
    "side": "long",
    "risk": {
      "risk_per_trade_pct": 0.4,
      "atr": 0.2532,
      "atr_mult": 2.0,
      "rr_target": 2.0,
      "cooldown_min": 30
    },
    "limit_plan": {
      "cancel_if": {
        "condition": "Cancel if conditions...",
        "timeout_min": 120
      },
      "orders": [
        {
          "price": 44.64,
          "size_pct": 100
        }
      ],
      "stop_loss": 44.1336,
      "take_profits": [
        {
          "price": 45.1464,
          "size_pct": 30
        },
        {
          "price": 45.5516,
          "size_pct": 40
        },
        {
          "price": 45.9064,
          "size_pct": 30
        }
      ]
    }
  }
}
```

### 3. Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `intent` | string | Must be "trade_decision" | "trade_decision" |
| `trade.symbol` | string | Trading pair | "HYPE/USDT" |
| `trade.side` | string | Trade direction | "long" or "short" |
| `trade.risk.risk_per_trade_pct` | number | Risk per trade % | 0.4 |
| `trade.limit_plan.orders[0].price` | number | Entry price | 44.64 |
| `trade.limit_plan.stop_loss` | number | Stop loss price | 44.1336 |
| `trade.limit_plan.take_profits` | array | Take profit levels | See example above |

### 4. Testing the Webhook

1. **Start your bot**:
   ```bash
   ./start_bot.sh
   ```

2. **Test with curl**:
   ```bash
   curl -X POST http://localhost:8080/ \
     -H "Content-Type: application/json" \
     -d @sample_trade.json
   ```

3. **Check logs**:
   - `webhook.log` - Webhook server activity
   - `trading.log` - Trade execution details

### 5. Health Check

Test if your bot is running:
```bash
curl http://localhost:8080/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1234567890,
  "service": "Bybit Trading Bot Webhook"
}
```

### 6. Error Handling

The bot will return appropriate HTTP status codes:
- `200` - Trade decision accepted
- `400` - Invalid data format
- `500` - Internal server error

### 7. Security Notes

- ⚠️ **Never expose your webhook publicly without authentication**
- 🔒 **Use HTTPS in production**
- 🚫 **Don't share your server IP publicly**
- 📊 **Monitor all incoming webhooks**

### 8. Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection refused | Check if bot is running on port 8080 |
| Invalid JSON | Verify JSON format matches example |
| Symbol not found | Check if trading pair exists on Bybit |
| Insufficient balance | Ensure USDT balance in Bybit account |

### 9. Production Deployment

For production use:
1. Use a VPS or cloud server
2. Set up HTTPS with SSL certificate
3. Add authentication (API keys, IP whitelist)
4. Use a reverse proxy (nginx)
5. Set up monitoring and alerts
6. Regular backup of configuration and logs
