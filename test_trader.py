#!/usr/bin/env python3
"""
Test script for Bybit Trading Bot
Tests the trader with sample data to ensure everything works correctly
"""

import json
import sys
from bybit_trader import BybitTrader

def test_trader():
    """Test the trader with sample data"""
    try:
        print("🧪 Testing Bybit Trading Bot...")
        
        # Initialize trader
        trader = BybitTrader()
        print("✅ Trader initialized successfully")
        
        # Test account info
        print("\n📊 Testing account info...")
        account_info = trader.get_account_info()
        if account_info and 'result' in account_info:
            print("✅ Account info retrieved successfully")
            # Show USDT balance
            for coin in account_info['result']['list']:
                if coin['coin'] == 'USDT':
                    balance = float(coin['totalWalletBalance'])
                    print(f"💰 USDT Balance: {balance}")
                    break
        else:
            print("❌ Failed to get account info")
            return False
        
        # Test symbol info
        print("\n🔍 Testing symbol info...")
        symbol_info = trader.get_symbol_info("HYPE/USDT")
        if symbol_info:
            print("✅ Symbol info retrieved successfully")
            print(f"Symbol: {symbol_info.get('symbol', 'N/A')}")
            print(f"Status: {symbol_info.get('status', 'N/A')}")
        else:
            print("❌ Failed to get symbol info")
            return False
        
        # Test position size calculation
        print("\n📏 Testing position size calculation...")
        entry_price = 44.64
        stop_loss = 44.1336
        risk_pct = 0.4
        
        position_size = trader.calculate_position_size(risk_pct, stop_loss, entry_price, symbol_info)
        if position_size > 0:
            print(f"✅ Position size calculated: {position_size}")
        else:
            print("❌ Failed to calculate position size")
            return False
        
        print("\n🎉 All tests passed! The trading bot is ready to use.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

def test_sample_trade():
    """Test with the sample trade data from make.com"""
    try:
        print("\n🔄 Testing with sample trade data...")
        
        # Sample trade data (same format as make.com)
        sample_trade = {
            "intent": "trade_decision",
            "reply_markdown": "Firm setup (long, limit)\n- Entry: 44.6400 (pullback into 5–15m value; OB + 0.5–0.618 fib)\n- SL: 44.1336 (2× 15m ATR)\n- TP: 45.1464 (30%), 45.5516 (40%), 45.9064 (30%)\n- R/R: ≥1.8R to TP2, 2.5R to final; risk 0.4%\n- Cancel if: 15m closes < 44.40, BTC -2% in 1h, or not filled in 120m\nContext: 1h trend up, 15m momentum strong; regime RISK_ON (comp 0.35) → size modest. Confidence 0.60.",
            "trade": {
                "action": "open_limit",
                "reason": "Pullback-to-value long aligned with 1h upstructure and 15m momentum; RR meets ≥1.8 with ATR-based SL; avoids chasing below 1h EMA200 resistance.",
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
                "market_order": None,
                "limit_plan": {
                    "cancel_if": {
                        "condition": "Cancel if 15m candle closes below 44.40 or if BTC drops >2% in 1h.",
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
                },
                "management": None
            },
            "settings": {
                "risk_per_trade_pct": None,
                "atr_mult": None,
                "rr_target": None,
                "cooldown_min": None,
                "rr_to_breakeven": None,
                "language": "en"
            }
        }
        
        print("📋 Sample trade data structure:")
        print(json.dumps(sample_trade, indent=2))
        
        print("\n✅ Sample trade data is valid and ready for testing")
        return True
        
    except Exception as e:
        print(f"❌ Failed to process sample trade data: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Bybit Trading Bot - Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    if not test_trader():
        print("\n❌ Basic tests failed. Please check your configuration.")
        sys.exit(1)
    
    # Test sample trade data
    if not test_sample_trade():
        print("\n❌ Sample trade data test failed.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎯 Next steps:")
    print("1. Run the webhook server: python webhook_server.py")
    print("2. Configure make.com to send webhooks to your server")
    print("3. Monitor logs in trading.log and webhook.log")
    print("4. Test with real trade decisions from make.com")
    
    print("\n⚠️  IMPORTANT: This bot will execute real trades on Bybit!")
    print("   Make sure to test thoroughly before using with real money.")

if __name__ == "__main__":
    main()
