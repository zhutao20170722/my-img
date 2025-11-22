"""
Interactive Brokers platform connector
Interactive Brokers 平台连接器
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from .base_connector import BaseConnector
from ..models import MarketData, Order, OrderSide, OrderType, OrderStatus

logger = logging.getLogger(__name__)


class IBConnector(BaseConnector):
    """
    Interactive Brokers platform connector
    
    This connector provides integration with Interactive Brokers TWS/Gateway.
    Note: Requires ib_insync Python package to be installed for live trading.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize IB connector
        
        Args:
            config: Configuration dictionary with IB settings:
                - host: IB TWS/Gateway host (default: "127.0.0.1")
                - port: IB TWS/Gateway port (default: 7497 for TWS, 4001 for Gateway)
                - client_id: Client ID (default: 1)
                - timeout: Connection timeout in seconds (default: 20)
                - readonly: Read-only mode (default: False)
        """
        super().__init__(config)
        self.host = config.get('host', '127.0.0.1')
        self.port = config.get('port', 7497)
        self.client_id = config.get('client_id', 1)
        self.timeout = config.get('timeout', 20)
        self.readonly = config.get('readonly', False)
        self.ib = None
        self._subscriptions = {}
        
    def connect(self) -> bool:
        """
        Connect to Interactive Brokers TWS/Gateway
        连接到Interactive Brokers TWS/Gateway
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to import ib_insync package
            try:
                from ib_insync import IB
                self.ib = IB()
            except ImportError:
                logger.warning("ib_insync package not installed. Running in simulation mode.")
                logger.info("To use live IB connection, install: pip install ib_insync")
                self.connected = True  # Simulation mode
                return True
            
            # Connect to TWS/Gateway
            self.ib.connect(
                host=self.host,
                port=self.port,
                clientId=self.client_id,
                timeout=self.timeout,
                readonly=self.readonly
            )
            
            if not self.ib.isConnected():
                logger.error("Failed to connect to IB TWS/Gateway")
                return False
            
            self.connected = True
            logger.info(f"Successfully connected to IB at {self.host}:{self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to IB: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from Interactive Brokers
        断开IB连接
        
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            if self.ib and self.ib.isConnected():
                self.ib.disconnect()
            self.connected = False
            logger.info("Disconnected from IB")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from IB: {e}")
            return False
    
    def get_market_data(self, symbol: str, timeframe: str = "1m", 
                       count: int = 100) -> List[MarketData]:
        """
        Get historical market data from IB
        从IB获取历史市场数据
        
        Args:
            symbol: Symbol (e.g., "AAPL", "EUR.USD")
            timeframe: Timeframe ("1m", "5m", "15m", "30m", "1h", "4h", "1d")
            count: Number of bars to retrieve
            
        Returns:
            List of MarketData objects
        """
        if not self.connected:
            logger.error("Not connected to IB")
            return []
        
        if not self.ib:
            logger.warning("IB package not available, returning empty data")
            return []
        
        try:
            from ib_insync import Stock, Forex
            
            # Create contract
            if '.' in symbol:
                # Forex pair (e.g., EUR.USD)
                base, quote = symbol.split('.')
                contract = Forex(base + quote)
            else:
                # Stock
                contract = Stock(symbol, 'SMART', 'USD')
            
            # Map timeframe to IB bar size
            timeframe_map = {
                "1m": "1 min",
                "5m": "5 mins",
                "15m": "15 mins",
                "30m": "30 mins",
                "1h": "1 hour",
                "4h": "4 hours",
                "1d": "1 day",
            }
            
            bar_size = timeframe_map.get(timeframe, "1 min")
            
            # Calculate duration based on timeframe and count
            # IB duration format: "S" (seconds), "D" (days), "W" (weeks), "M" (months), "Y" (years)
            duration_map = {
                "1 min": f"{max(1, count * 60)} S",  # Convert to seconds
                "5 mins": f"{max(1, count * 5 * 60)} S",  # Convert to seconds
                "15 mins": f"{max(1, count // 4 + 1)} D",  # ~4 bars per hour
                "30 mins": f"{max(1, count // 2 + 1)} D",  # ~2 bars per hour
                "1 hour": f"{max(1, count // 6 + 1)} D",  # ~6 bars per day (trading hours)
                "4 hours": f"{max(1, count + 1)} D",  # ~1-2 bars per day
                "1 day": f"{max(1, count)} D",  # 1 bar per day
            }
            
            duration = duration_map.get(bar_size, "1 D")
            
            # Request historical data
            bars = self.ib.reqHistoricalData(
                contract,
                endDateTime='',
                durationStr=duration,
                barSizeSetting=bar_size,
                whatToShow='TRADES',
                useRTH=True,
                formatDate=1
            )
            
            if not bars:
                logger.warning(f"No data received for {symbol}")
                return []
            
            # Convert to MarketData objects
            market_data = []
            for bar in bars:
                data = MarketData(
                    symbol=symbol,
                    timestamp=bar.date,
                    open=Decimal(str(bar.open)),
                    high=Decimal(str(bar.high)),
                    low=Decimal(str(bar.low)),
                    close=Decimal(str(bar.close)),
                    volume=int(bar.volume)
                )
                market_data.append(data)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data from IB: {e}")
            return []
    
    def subscribe_market_data(self, symbol: str, callback) -> bool:
        """
        Subscribe to real-time market data
        订阅实时市场数据
        
        Args:
            symbol: Symbol to subscribe
            callback: Callback function to receive market data
            
        Returns:
            True if subscription successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to IB")
            return False
        
        if not self.ib:
            logger.warning("IB package not available")
            return False
        
        try:
            from ib_insync import Stock, Forex
            
            # Create contract
            if '.' in symbol:
                base, quote = symbol.split('.')
                contract = Forex(base + quote)
            else:
                contract = Stock(symbol, 'SMART', 'USD')
            
            # Request market data
            self.ib.reqMktData(contract, '', False, False)
            self._subscriptions[symbol] = {
                'contract': contract,
                'callback': callback
            }
            
            logger.info(f"Subscribed to market data for {symbol}")
            return True
            
        except Exception as e:
            logger.error(f"Error subscribing to market data: {e}")
            return False
    
    def unsubscribe_market_data(self, symbol: str) -> bool:
        """
        Unsubscribe from real-time market data
        取消订阅实时市场数据
        
        Args:
            symbol: Symbol to unsubscribe
            
        Returns:
            True if unsubscription successful, False otherwise
        """
        if symbol in self._subscriptions:
            if self.ib and self.ib.isConnected():
                contract = self._subscriptions[symbol]['contract']
                self.ib.cancelMktData(contract)
            
            del self._subscriptions[symbol]
            logger.info(f"Unsubscribed from market data for {symbol}")
            return True
        return False
    
    def place_order(self, order: Order) -> Optional[str]:
        """
        Place an order on IB
        在IB上下单
        
        Args:
            order: Order object to place
            
        Returns:
            IB order ID if successful, None otherwise
        """
        if not self.connected:
            logger.error("Not connected to IB")
            return None
        
        if not self.ib:
            logger.warning("IB package not available, simulating order placement")
            return f"SIM-{order.order_id}"
        
        try:
            from ib_insync import Stock, MarketOrder, LimitOrder, StopOrder
            
            # Create contract
            contract = Stock(order.symbol, 'SMART', 'USD')
            
            # Create order based on type
            if order.order_type == OrderType.MARKET:
                ib_order = MarketOrder(
                    action='BUY' if order.side == OrderSide.BUY else 'SELL',
                    totalQuantity=order.quantity
                )
            elif order.order_type == OrderType.LIMIT and order.price:
                ib_order = LimitOrder(
                    action='BUY' if order.side == OrderSide.BUY else 'SELL',
                    totalQuantity=order.quantity,
                    lmtPrice=float(order.price)
                )
            elif order.order_type == OrderType.STOP and order.price:
                ib_order = StopOrder(
                    action='BUY' if order.side == OrderSide.BUY else 'SELL',
                    totalQuantity=order.quantity,
                    stopPrice=float(order.price)
                )
            else:
                logger.error(f"Invalid order type or missing price")
                return None
            
            # Place order
            trade = self.ib.placeOrder(contract, ib_order)
            
            if trade:
                logger.info(f"Order placed successfully: {trade.order.orderId}")
                return str(trade.order.orderId)
            else:
                logger.error("Failed to place order")
                return None
            
        except Exception as e:
            logger.error(f"Error placing order on IB: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order on IB
        取消IB订单
        
        Args:
            order_id: IB order ID
            
        Returns:
            True if cancellation successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to IB")
            return False
        
        if not self.ib:
            logger.warning("IB package not available, simulating order cancellation")
            return True
        
        try:
            # Find the order
            for trade in self.ib.trades():
                if str(trade.order.orderId) == order_id:
                    self.ib.cancelOrder(trade.order)
                    logger.info(f"Order cancelled successfully: {order_id}")
                    return True
            
            logger.warning(f"Order not found: {order_id}")
            return False
            
        except Exception as e:
            logger.error(f"Error cancelling order on IB: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get IB account information
        获取IB账户信息
        
        Returns:
            Dictionary containing account information
        """
        if not self.connected:
            logger.error("Not connected to IB")
            return {}
        
        if not self.ib:
            logger.warning("IB package not available, returning simulated account info")
            return {
                "balance": Decimal("10000.00"),
                "equity": Decimal("10000.00"),
                "available_funds": Decimal("10000.00"),
                "buying_power": Decimal("40000.00"),
                "net_liquidation": Decimal("10000.00"),
            }
        
        try:
            account_values = self.ib.accountValues()
            
            result = {}
            for av in account_values:
                if av.tag == 'TotalCashValue':
                    result['balance'] = Decimal(av.value)
                elif av.tag == 'NetLiquidation':
                    result['net_liquidation'] = Decimal(av.value)
                    result['equity'] = Decimal(av.value)
                elif av.tag == 'AvailableFunds':
                    result['available_funds'] = Decimal(av.value)
                elif av.tag == 'BuyingPower':
                    result['buying_power'] = Decimal(av.value)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting account info from IB: {e}")
            return {}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions from IB
        获取IB当前持仓
        
        Returns:
            List of position dictionaries
        """
        if not self.connected:
            logger.error("Not connected to IB")
            return []
        
        if not self.ib:
            logger.warning("IB package not available, returning empty positions")
            return []
        
        try:
            positions = self.ib.positions()
            
            result = []
            for pos in positions:
                result.append({
                    "symbol": pos.contract.symbol,
                    "position": pos.position,
                    "average_cost": Decimal(str(pos.avgCost)),
                    "market_value": Decimal(str(pos.marketValue)) if pos.marketValue else Decimal("0"),
                    "unrealized_pnl": Decimal(str(pos.unrealizedPNL)) if pos.unrealizedPNL else Decimal("0"),
                    "realized_pnl": Decimal(str(pos.realizedPNL)) if pos.realizedPNL else Decimal("0"),
                    "account": pos.account,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting positions from IB: {e}")
            return []
    
    def get_orders(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get orders from IB
        获取IB订单列表
        
        Args:
            active_only: If True, only return active orders
            
        Returns:
            List of order dictionaries
        """
        if not self.connected:
            logger.error("Not connected to IB")
            return []
        
        if not self.ib:
            logger.warning("IB package not available, returning empty orders")
            return []
        
        try:
            if active_only:
                trades = self.ib.openTrades()
            else:
                trades = self.ib.trades()
            
            result = []
            for trade in trades:
                result.append({
                    "order_id": trade.order.orderId,
                    "symbol": trade.contract.symbol,
                    "action": trade.order.action,
                    "order_type": trade.order.orderType,
                    "quantity": trade.order.totalQuantity,
                    "filled_quantity": trade.orderStatus.filled,
                    "status": trade.orderStatus.status,
                    "limit_price": Decimal(str(trade.order.lmtPrice)) if hasattr(trade.order, 'lmtPrice') and trade.order.lmtPrice else None,
                    "stop_price": Decimal(str(trade.order.auxPrice)) if hasattr(trade.order, 'auxPrice') and trade.order.auxPrice else None,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting orders from IB: {e}")
            return []
