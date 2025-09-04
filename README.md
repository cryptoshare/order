# Bybit Trading Bot

A Python-based trading bot that receives trade decisions from make.com and executes them on Bybit. The bot supports limit orders, stop losses, and multiple take profit levels with risk management.

<!-- Updated: Fixed stop-loss order type for derivatives trading -->

## Features

- 🔄 **Webhook Integration**: Receives trade decisions from make.com via HTTP webhooks
- 📊 **Risk Management**: Calculates position sizes based on risk percentage
- 🎯 **Advanced Order Types**: Supports limit orders, stop losses, and multiple take profits
- 📝 **Comprehensive Logging**: Detailed logs for all trading activities
- 🧪 **Testing Suite**: Built-in testing to verify setup and functionality
- 🔒 **Secure**: Uses environment variables for API credentials

## Prerequisites

- Python 3.8+
- Bybit account with API access
- make.com account for trade decision automation

## Installation

1. **Clone or download the project files**

2. **Activate the virtual environment** (always required):
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your Bybit API credentials**:
   - Edit `config.env` with your actual API keys
   - Set `BYBIT_TESTNET=true` for testing (recommended initially)

## Configuration

### Environment Variables (`config.env`)

```env
BYBIT_API_KEY=your_api_key_here
BYBIT_SECRET_KEY=your_secret_key_here
BYBIT_TESTNET=false  # Set to true for testing
WEBHOOK_HOST=0.0.0.0  # Optional: webhook server host
WEBHOOK_PORT=8080      # Optional: webhook server port
```

### make.com Webhook Format

The bot expects trade decisions in this JSON format:

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

## Usage

### 1. Test the Setup

Always activate the virtual environment first:
```bash
source venv/bin/activate
python test_trader.py
```

### 2. Run the Webhook Server (Local)

```bash
source venv/bin/activate
python webhook_server.py
```

The server will start on `http://0.0.0.0:8080` by default.

### 3. Deploy to Railway (Recommended)

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/bybit-trader.git
   git push -u origin main
   ```

2. **Deploy on Railway**:
   - Go to [Railway.app](https://railway.app)
   - Connect your GitHub account
   - Create a new project from your GitHub repository
   - Add environment variables in Railway dashboard:
     - `BYBIT_API_KEY`: Your Bybit API key
     - `BYBIT_SECRET_KEY`: Your Bybit secret key
     - `BYBIT_TESTNET`: `false` (or `true` for testing)
   - Deploy!

3. **Get your webhook URL**:
   - Railway will provide a URL like: `https://your-app-name.railway.app`
   - Use this URL in make.com

### 4. Configure make.com

In make.com, set up a webhook to send POST requests to:
```
https://your-app-name.railway.app/
```

### 4. Monitor Logs

The bot creates two log files:
- `trading.log` - Trading execution logs
- `webhook.log` - Webhook server logs

## File Structure

```
Bybit trader/
├── venv/                    # Virtual environment
├── config.env              # Configuration file
├── requirements.txt        # Python dependencies
├── bybit_trader.py        # Main trading logic
├── webhook_server.py      # Webhook server
├── test_trader.py         # Testing script
├── README.md              # This file
├── trading.log            # Trading logs (created at runtime)
└── webhook.log            # Webhook logs (created at runtime)
```

## How It Works

1. **Webhook Reception**: The server receives trade decisions from make.com
2. **Data Validation**: Validates the incoming trade data structure
3. **Position Sizing**: Calculates position size based on risk percentage and account balance
4. **Order Execution**: Places the main limit order, stop loss, and take profit orders
5. **Logging**: Records all activities for monitoring and debugging

## Risk Management

- **Position Sizing**: Automatically calculated based on risk percentage
- **Stop Loss**: Placed as a stop market order
- **Take Profits**: Multiple levels with percentage-based position sizing
- **Timeout**: Orders can be cancelled if not filled within specified time

## Testing

### Test the Trader
```bash
source venv/bin/activate
python test_trader.py
```

### Test with Sample Data
```bash
source venv/bin/activate
python bybit_trader.py
```

## Security Considerations

- ⚠️ **Never commit API keys to version control**
- 🔒 **Use environment variables for sensitive data**
- 🧪 **Test with testnet before using real funds**
- 📊 **Monitor all trades and logs carefully**

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure virtual environment is activated
2. **API Errors**: Verify API keys and permissions
3. **Symbol Errors**: Check if the trading pair exists on Bybit
4. **Balance Errors**: Ensure sufficient USDT balance

### Logs

Check the log files for detailed error information:
- `trading.log` - Trading execution issues
- `webhook.log` - Webhook server issues

## Support

For issues or questions:
1. Check the logs for error details
2. Verify your configuration
3. Test with the provided test scripts
4. Ensure your Bybit API has trading permissions

## Disclaimer

⚠️ **This bot executes real trades on Bybit. Use at your own risk.**

- Test thoroughly before using with real funds
- Monitor all trades carefully
- Understand the risks involved in automated trading
- The authors are not responsible for any financial losses

## License

This project is for educational and personal use. Please ensure compliance with Bybit's terms of service and local regulations.
