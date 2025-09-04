#!/usr/bin/env python3
"""
Bybit Trading Bot
Receives trade decisions from make.com and executes them on Bybit
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from decimal import Decimal, ROUND_DOWN

import requests
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

# Load environment variables
load_dotenv('config.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BybitTrader:
    def __init__(self):
        """Initialize Bybit trader with API credentials"""
        self.api_key = os.getenv('BYBIT_API_KEY')
        self.secret_key = os.getenv('BYBIT_SECRET_KEY')
        self.testnet = os.getenv('BYBIT_TESTNET', 'false').lower() == 'true'
        
        if not self.api_key or not self.secret_key:
            raise ValueError("BYBIT_API_KEY and BYBIT_SECRET_KEY must be set in config.env")
        
        # Initialize Bybit client
        self.session = HTTP(
            testnet=self.testnet,
            api_key=self.api_key,
            api_secret=self.secret_key
        )
        
        logger.info(f"Bybit trader initialized (testnet: {self.testnet})")
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        try:
            response = self.session.get_wallet_balance(accountType="UNIFIED")
            return response
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return {}
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """Get symbol information including tick size and lot size"""
        try:
            response = self.session.get_instruments_info(
                category="linear",
                symbol=symbol.replace('/', '')
            )
            if response['result']['list']:
                return response['result']['list'][0]
            return {}
        except Exception as e:
            logger.error(f"Failed to get symbol info for {symbol}: {e}")
            return {}
    
    def calculate_position_size(self, risk_pct: float, stop_loss: float, entry_price: float, symbol_info: Dict[str, Any]) -> float:
        """Calculate position size based on risk percentage"""
        try:
            # Get account balance
            account_info = self.get_account_info()
            if not account_info or 'result' not in account_info:
                logger.error("Failed to get account balance")
                return 0.0
            
            # Find USDT balance
            usdt_balance = 0.0
            for account in account_info['result']['list']:
                if 'coin' in account:
                    for coin in account['coin']:
                        if coin['coin'] == 'USDT':
                            usdt_balance = float(coin['walletBalance'])
                            break
            
            if usdt_balance == 0.0:
                logger.error("No USDT balance found")
                return 0.0
            
            # Calculate risk amount
            risk_amount = usdt_balance * (risk_pct / 100)
            
            # Calculate position size based on stop loss distance
            stop_distance = abs(entry_price - stop_loss)
            if stop_distance == 0:
                logger.error("Invalid stop loss distance")
                return 0.0
            
            position_size = risk_amount / stop_distance
            
            # Round down to meet lot size requirements
            lot_size_filter = symbol_info.get('lotSizeFilter', {})
            min_order_qty = float(lot_size_filter.get('minOrderQty', 0.001))
            qty_step = float(lot_size_filter.get('qtyStep', 0.001))
            
            position_size = (position_size // qty_step) * qty_step
            position_size = max(position_size, min_order_qty)
            
            # Ensure minimum order value of 5 USDT for derivatives
            min_order_value = 5.0
            min_position_size = min_order_value / entry_price
            if position_size * entry_price < min_order_value:
                position_size = min_position_size
                # Round up to meet minimum order value
                position_size = ((position_size // qty_step) + 1) * qty_step
                position_size = max(position_size, min_order_qty)
            
            logger.info(f"Calculated position size: {position_size} (risk: {risk_pct}%, balance: {usdt_balance} USDT, order value: {position_size * entry_price:.2f} USDT)")
            return position_size
            
        except Exception as e:
            logger.error(f"Failed to calculate position size: {e}")
            return 0.0
    
    def place_limit_order(self, symbol: str, side: str, qty: float, price: float, 
                         stop_loss: float, take_profits: list, timeout_min: int = 120) -> Dict[str, Any]:
        """Place a limit order with stop loss and take profits using conditional orders"""
        try:
            # Convert symbol format (HYPE/USDT -> HYPEUSDT)
            bybit_symbol = symbol.replace('/', '')
            
            # Convert side to derivatives format
            derivatives_side = "Buy" if side.lower() == "long" else "Sell"
            
            # Place the main limit order
            order_response = self.session.place_order(
                category="linear",
                symbol=bybit_symbol,
                side=derivatives_side,
                orderType="Limit",
                qty=str(qty),
                price=str(price),
                timeInForce="GTC"
            )
            
            if order_response['retCode'] != 0:
                logger.error(f"Failed to place limit order: {order_response}")
                return order_response
            
            order_id = order_response['result']['orderId']
            logger.info(f"Placed {side} limit order: {order_id} for {qty} {symbol} at {price}")
            
            # Wait a moment for the order to be processed
            import time
            time.sleep(1)
            
            # Place conditional stop loss order
            sl_side = "Sell" if side.lower() == "long" else "Buy"
            sl_response = self.session.place_order(
                category="linear",
                symbol=bybit_symbol,
                side=sl_side,
                orderType="Stop",
                qty=str(qty),
                stopPrice=str(stop_loss),
                timeInForce="GTC",
                triggerBy="LastPrice"
            )
            
            if sl_response['retCode'] == 0:
                logger.info(f"Placed stop loss order: {sl_response['result']['orderId']} at {stop_loss}")
            else:
                logger.error(f"Failed to place stop loss: {sl_response}")
            
            # Place conditional take profit orders
            tp_side = "Sell" if side.lower() == "long" else "Buy"
            tp_responses = []
            for tp in take_profits:
                tp_qty = qty * (tp['size_pct'] / 100)
                tp_response = self.session.place_order(
                    category="linear",
                    symbol=bybit_symbol,
                    side=tp_side,
                    orderType="Limit",
                    qty=str(tp_qty),
                    price=str(tp['price']),
                    timeInForce="GTC"
                )
                
                if tp_response['retCode'] == 0:
                    logger.info(f"Placed take profit order: {tp_response['result']['orderId']} for {tp_qty} at {tp['price']}")
                    tp_responses.append(tp_response)
                else:
                    logger.error(f"Failed to place take profit: {tp_response}")
            
            return {
                'success': True,
                'main_order': order_response,
                'stop_loss': sl_response,
                'take_profits': tp_responses
            }
            
        except Exception as e:
            logger.error(f"Failed to place orders: {e}")
            return {'success': False, 'error': str(e)}
    
    def execute_trade(self, trade_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trade based on the received trade decision"""
        try:
            logger.info(f"Executing trade: {trade_data['symbol']} {trade_data['side']}")
            
            # Validate trade data
            required_fields = ['symbol', 'side', 'limit_plan', 'risk']
            for field in required_fields:
                if field not in trade_data:
                    return {'success': False, 'error': f'Missing required field: {field}'}
            
            symbol = trade_data['symbol']
            side = trade_data['side']
            limit_plan = trade_data['limit_plan']
            risk = trade_data['risk']
            
            # Get symbol information
            symbol_info = self.get_symbol_info(symbol)
            if not symbol_info:
                return {'success': False, 'error': f'Failed to get symbol info for {symbol}'}
            
            # Calculate position size
            entry_price = limit_plan['orders'][0]['price']
            stop_loss = limit_plan['stop_loss']
            risk_pct = risk.get('risk_per_trade_pct', 0.4)
            
            position_size = self.calculate_position_size(risk_pct, stop_loss, entry_price, symbol_info)
            if position_size == 0.0:
                return {'success': False, 'error': 'Failed to calculate position size'}
            
            # Place the order
            result = self.place_limit_order(
                symbol=symbol,
                side=side,
                qty=position_size,
                price=entry_price,
                stop_loss=stop_loss,
                take_profits=limit_plan['take_profits'],
                timeout_min=limit_plan['cancel_if']['timeout_min']
            )
            
            if result['success']:
                logger.info(f"Trade executed successfully: {symbol} {side} {position_size} at {entry_price}")
            else:
                logger.error(f"Trade execution failed: {result.get('error', 'Unknown error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to execute trade: {e}")
            return {'success': False, 'error': str(e)}

def main():
    """Main function to handle incoming trade decisions"""
    try:
        # Initialize trader
        trader = BybitTrader()
        
        # For testing, you can load the trade data from a file or pass it as input
        # In production, this would come from your webhook endpoint
        
        # Example: Read from stdin (for testing)
        print("Enter trade decision JSON (or press Enter to use sample data):")
        user_input = input().strip()
        
        if user_input:
            trade_data = json.loads(user_input)
        else:
            # Use sample data for testing
            trade_data = {
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
        
        # Execute the trade
        result = trader.execute_trade(trade_data['trade'])
        
        if result['success']:
            print("✅ Trade executed successfully!")
            print(json.dumps(result, indent=2))
        else:
            print("❌ Trade execution failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            
    except KeyboardInterrupt:
        print("\n👋 Trading bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
