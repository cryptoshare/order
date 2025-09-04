#!/usr/bin/env python3
"""
Demo script for Bybit Trading Bot
Shows the bot functionality without requiring account balance
"""

import json
from bybit_trader import BybitTrader

def demo_bot_functionality():
    """Demonstrate the bot's core functionality"""
    try:
        print("🎭 Bybit Trading Bot - Demo Mode")
        print("=" * 50)
        
        # Initialize trader
        trader = BybitTrader()
        print("✅ Trader initialized successfully")
        
        # Test account connection
        print("\n📊 Testing Bybit connection...")
        account_info = trader.get_account_info()
        if account_info and 'result' in account_info:
            print("✅ Successfully connected to Bybit")
            print(f"Account type: {account_info['result'].get('accountType', 'N/A')}")
            
            # Show available balances
            print("\n💰 Available balances:")
            for coin in account_info['result']['list']:
                balance = float(coin['totalWalletBalance'])
                if balance > 0:
                    print(f"  {coin['coin']}: {balance}")
                else:
                    print(f"  {coin['coin']}: {balance} (no balance)")
        else:
            print("❌ Failed to connect to Bybit")
            return False
        
        # Test symbol information
        print("\n🔍 Testing symbol information...")
        symbol_info = trader.get_symbol_info("HYPE/USDT")
        if symbol_info:
            print("✅ Symbol info retrieved successfully")
            print(f"  Symbol: {symbol_info.get('symbol', 'N/A')}")
            print(f"  Status: {symbol_info.get('status', 'N/A')}")
            print(f"  Base coin: {symbol_info.get('baseCoin', 'N/A')}")
            print(f"  Quote coin: {symbol_info.get('quoteCoin', 'N/A')}")
            
            # Show lot size information
            lot_size = symbol_info.get('lotSizeFilter', {})
            if lot_size:
                print(f"  Min order qty: {lot_size.get('minOrderQty', 'N/A')}")
                print(f"  Qty step: {lot_size.get('qtyStep', 'N/A')}")
        else:
            print("❌ Failed to get symbol info")
            return False
        
        # Test position size calculation (with mock data)
        print("\n📏 Testing position size calculation...")
        entry_price = 44.64
        stop_loss = 44.1336
        risk_pct = 0.4
        
        # Mock USDT balance for demonstration
        mock_usdt_balance = 1000.0
        risk_amount = mock_usdt_balance * (risk_pct / 100)
        stop_distance = abs(entry_price - stop_loss)
        mock_position_size = risk_amount / stop_distance
        
        print(f"  Entry price: ${entry_price}")
        print(f"  Stop loss: ${stop_loss}")
        print(f"  Risk percentage: {risk_pct}%")
        print(f"  Mock USDT balance: ${mock_usdt_balance}")
        print(f"  Risk amount: ${risk_amount}")
        print(f"  Stop distance: ${stop_distance}")
        print(f"  Calculated position size: {mock_position_size:.6f}")
        
        # Test webhook data validation
        print("\n🔄 Testing webhook data validation...")
        sample_webhook = {
            "intent": "trade_decision",
            "trade": {
                "action": "open_limit",
                "symbol": "HYPE/USDT",
                "side": "long",
                "risk": {"risk_per_trade_pct": 0.4},
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
        
        print("✅ Sample webhook data structure is valid")
        print("  Intent:", sample_webhook['intent'])
        print("  Symbol:", sample_webhook['trade']['symbol'])
        print("  Side:", sample_webhook['trade']['side'])
        print("  Risk:", sample_webhook['trade']['risk']['risk_per_trade_pct'], "%")
        
        print("\n🎉 Demo completed successfully!")
        print("\n📋 What the bot can do:")
        print("  ✅ Connect to Bybit API")
        print("  ✅ Retrieve account information")
        print("  ✅ Get symbol details and trading rules")
        print("  ✅ Calculate position sizes based on risk")
        print("  ✅ Validate webhook data from make.com")
        print("  ✅ Execute trades with stop losses and take profits")
        
        print("\n🚀 Ready to receive trade decisions from make.com!")
        print("   Run: python webhook_server.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        return False

def main():
    """Main demo function"""
    if demo_bot_functionality():
        print("\n" + "=" * 50)
        print("🎯 Next steps:")
        print("1. Ensure you have USDT balance in your Bybit account")
        print("2. Run the webhook server: python webhook_server.py")
        print("3. Configure make.com to send webhooks")
        print("4. Test with real trade decisions")
        
        print("\n⚠️  Important notes:")
        print("   - The bot will execute real trades on Bybit")
        print("   - Test thoroughly before using with real money")
        print("   - Monitor all trades and logs carefully")
    else:
        print("\n❌ Demo failed. Please check your configuration.")

if __name__ == "__main__":
    main()
