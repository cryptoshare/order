#!/usr/bin/env python3
"""
Webhook Server for Bybit Trading Bot
Receives trade decisions from make.com and executes them
"""

import json
import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading
import time
from typing import Dict, Any

from dotenv import load_dotenv
from bybit_trader import BybitTrader

# Load environment variables
load_dotenv('config.env')
load_dotenv()  # Also load from .env file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('webhook.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingWebhookHandler(BaseHTTPRequestHandler):
    """HTTP request handler for trading webhooks"""
    
    def __init__(self, *args, trader: BybitTrader = None, **kwargs):
        self.trader = trader
        super().__init__(*args, **kwargs)
    
    def do_POST(self):
        """Handle POST requests with trade decisions"""
        try:
            # Get content length
            content_length = int(self.headers.get('Content-Length', 0))
            
            if content_length == 0:
                self.send_error_response(400, "No content received")
                return
            
            # Read request body
            post_data = self.rfile.read(content_length)
            
            try:
                trade_data = json.loads(post_data.decode('utf-8'))
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON received: {e}")
                self.send_error_response(400, "Invalid JSON format")
                return
            
            # Log received data
            logger.info(f"Received webhook: {json.dumps(trade_data, indent=2)}")
            
            # Validate webhook data
            if not self.validate_webhook_data(trade_data):
                self.send_error_response(400, "Invalid webhook data format")
                return
            
            # Execute trade in background thread
            if self.trader:
                threading.Thread(
                    target=self.execute_trade_async,
                    args=(trade_data,),
                    daemon=True
                ).start()
                
                # Send immediate response
                self.send_success_response({
                    "status": "accepted",
                    "message": "Trade decision received and queued for execution",
                    "timestamp": time.time()
                })
            else:
                self.send_error_response(500, "Trader not initialized")
                
        except Exception as e:
            logger.error(f"Error processing webhook: {e}")
            self.send_error_response(500, f"Internal server error: {str(e)}")
    
    def do_GET(self):
        """Handle GET requests for health checks"""
        if self.path == '/health':
            self.send_success_response({
                "status": "healthy",
                "timestamp": time.time(),
                "service": "Bybit Trading Bot Webhook"
            })
        else:
            self.send_error_response(404, "Not found")
    
    def validate_webhook_data(self, data: Dict[str, Any]) -> bool:
        """Validate the structure of received webhook data"""
        try:
            # Check required top-level fields
            if 'intent' not in data or data['intent'] != 'trade_decision':
                logger.error("Missing or invalid 'intent' field")
                return False
            
            if 'trade' not in data:
                logger.error("Missing 'trade' field")
                return False
            
            trade = data['trade']
            required_trade_fields = ['action', 'symbol', 'side', 'limit_plan', 'risk']
            
            for field in required_trade_fields:
                if field not in trade:
                    logger.error(f"Missing required trade field: {field}")
                    return False
            
            # Validate limit plan structure
            limit_plan = trade['limit_plan']
            if 'orders' not in limit_plan or 'stop_loss' not in limit_plan or 'take_profits' not in limit_plan:
                logger.error("Invalid limit_plan structure")
                return False
            
            # Validate orders
            if not limit_plan['orders'] or not isinstance(limit_plan['orders'], list):
                logger.error("Invalid orders structure")
                return False
            
            # Validate take profits
            if not limit_plan['take_profits'] or not isinstance(limit_plan['take_profits'], list):
                logger.error("Invalid take_profits structure")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating webhook data: {e}")
            return False
    
    def execute_trade_async(self, trade_data: Dict[str, Any]):
        """Execute trade asynchronously"""
        try:
            logger.info(f"Executing trade asynchronously: {trade_data['trade']['symbol']}")
            
            result = self.trader.execute_trade(trade_data['trade'])
            
            if result['success']:
                logger.info(f"Trade executed successfully: {result}")
            else:
                logger.error(f"Trade execution failed: {result}")
                
        except Exception as e:
            logger.error(f"Error in async trade execution: {e}")
    
    def send_success_response(self, data: Dict[str, Any]):
        """Send successful response"""
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_data = {
            "error": True,
            "message": message,
            "status_code": status_code,
            "timestamp": time.time()
        }
        
        response = json.dumps(error_data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Override to use our logger instead of stderr"""
        logger.info(f"{self.address_string()} - {format % args}")

def create_webhook_handler(trader: BybitTrader):
    """Create a webhook handler with the trader instance"""
    def handler(*args, **kwargs):
        return TradingWebhookHandler(*args, trader=trader, **kwargs)
    return handler

def run_webhook_server(host: str = '0.0.0.0', port: int = 8080):
    """Run the webhook server"""
    try:
        # Initialize trader
        trader = BybitTrader()
        logger.info("Bybit trader initialized successfully")
        
        # Create server with custom handler
        handler = create_webhook_handler(trader)
        server = HTTPServer((host, port), handler)
        
        logger.info(f"Webhook server started on {host}:{port}")
        logger.info("Ready to receive trade decisions from make.com")
        logger.info("Health check available at: http://localhost:{port}/health")
        
        # Start server
        server.serve_forever()
        
    except KeyboardInterrupt:
        logger.info("Shutting down webhook server...")
        server.shutdown()
    except Exception as e:
        logger.error(f"Failed to start webhook server: {e}")
        raise

def main():
    """Main function to run the webhook server"""
    # Get configuration from environment or use defaults
    host = os.getenv('WEBHOOK_HOST', '0.0.0.0')
    port = int(os.getenv('PORT', os.getenv('WEBHOOK_PORT', '8080')))
    
    logger.info(f"Starting Bybit Trading Bot Webhook Server...")
    logger.info(f"Host: {host}, Port: {port}")
    
    run_webhook_server(host, port)

if __name__ == "__main__":
    main()
