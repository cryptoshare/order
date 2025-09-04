# Railway Deployment Guide

This guide will help you deploy your Bybit trading bot to Railway for use with make.com webhooks.

## Prerequisites

- GitHub account
- Railway account (free at [railway.app](https://railway.app))
- Bybit API credentials with trading permissions

## Step 1: GitHub Repository

✅ **Repository Ready**: Your code is already pushed to [https://github.com/cryptoshare/order.git](https://github.com/cryptoshare/order.git)

The repository contains:
- Complete Bybit trading bot with derivatives support
- Webhook server for make.com integration
- Railway deployment configuration
- Risk management and position sizing
- Comprehensive documentation

## Step 2: Deploy on Railway

1. **Go to Railway**: Visit [railway.app](https://railway.app)
2. **Sign up/Login**: Use your GitHub account
3. **Create New Project**: Click "New Project"
4. **Deploy from GitHub**: Select "Deploy from GitHub repo"
5. **Select Repository**: Choose your `cryptoshare/order` repository
6. **Deploy**: Railway will automatically detect it's a Python app

## Step 3: Configure Environment Variables

In your Railway project dashboard:

1. Go to **Variables** tab
2. Add these environment variables:

```
BYBIT_API_KEY=ESHG81heo7B1NpbTLl
BYBIT_SECRET_KEY=vjFApzU49rCNqXwx5L8EIk3Dn1X4YomP9dRu
BYBIT_TESTNET=false
WEBHOOK_HOST=0.0.0.0
```

**Important**: Replace the API credentials with your actual values!

## Step 4: Get Your Webhook URL

1. In Railway dashboard, go to **Settings** tab
2. Find your **Domain** (e.g., `https://bybit-trader-production.up.railway.app`)
3. Copy this URL - this is your webhook endpoint

## Step 5: Configure make.com

1. In your make.com scenario, add a **Webhook** module
2. Set the webhook URL to your Railway domain:
   ```
   https://your-app-name.railway.app/
   ```
3. Set method to **POST**
4. Configure the webhook to send trade decisions in the expected format

## Step 6: Test the Deployment

1. **Health Check**: Visit `https://your-app-name.railway.app/health`
2. **Test Webhook**: Send a test trade decision from make.com
3. **Monitor Logs**: Check Railway logs for any errors

## Expected Webhook Format

Your make.com webhook should send data in this format:

```json
{
  "intent": "trade_decision",
  "trade": {
    "action": "open_limit",
    "symbol": "HYPE/USDT",
    "side": "long",
    "risk": {
      "risk_per_trade_pct": 0.4
    },
    "limit_plan": {
      "orders": [{"price": 44.64, "size_pct": 100}],
      "stop_loss": 44.1336,
      "take_profits": [
        {"price": 45.1464, "size_pct": 30},
        {"price": 45.5516, "size_pct": 40},
        {"price": 45.9064, "size_pct": 30}
      ],
      "cancel_if": {"timeout_min": 120}
    }
  }
}
```

## Monitoring

- **Railway Logs**: Check the logs tab in Railway dashboard
- **Health Endpoint**: `https://your-app-name.railway.app/health`
- **Trading Logs**: The bot logs all trading activities

## Security Notes

- Keep your API keys secure
- Use private GitHub repository
- Monitor your Railway usage (free tier has limits)
- Test with small amounts first

## Troubleshooting

### Common Issues:

1. **Build Fails**: Check that all dependencies are in `requirements.txt`
2. **API Errors**: Verify your Bybit API credentials and permissions
3. **Webhook Not Working**: Check the URL format and make.com configuration
4. **Orders Not Placing**: Ensure minimum order value (5 USDT for derivatives)

### Support:

- Check Railway logs for detailed error messages
- Verify your Bybit API has trading permissions
- Test locally first with `python test_trader.py`

## Cost

- **Railway**: Free tier available (limited usage)
- **Bybit**: No additional costs for API usage
- **make.com**: Depends on your plan

Your trading bot is now ready for production use! 🚀
