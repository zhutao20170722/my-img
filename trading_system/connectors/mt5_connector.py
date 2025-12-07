"""
MetaTrader 5 platform connector
MetaTrader 5 平台连接器
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from decimal import Decimal
import logging

from .base_connector import BaseConnector
from ..models import MarketData, Order, OrderSide, OrderType, OrderStatus

logger = logging.getLogger(__name__)


class MT5Connector(BaseConnector):
    """
    MetaTrader 5 platform connector
    
    This connector provides integration with MetaTrader 5 trading platform.
    Note: Requires MetaTrader5 Python package to be installed for live trading.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize MT5 connector
        
        Args:
            config: Configuration dictionary with MT5 settings:
                - account: MT5 account number
                - password: MT5 account password
                - server: MT5 server name
                - path: Optional MT5 terminal path
                - timeout: Connection timeout in seconds (default: 60000)
        """
        super().__init__(config)
        self.account = config.get('account')
        self.password = config.get('password')
        self.server = config.get('server')
        self.path = config.get('path')
        self.timeout = config.get('timeout', 60000)
        self.mt5 = None
        self._subscriptions = {}
        
    def connect(self) -> bool:
        """
        Connect to MT5 platform
        连接到MT5平台
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to import MetaTrader5 package
            try:
                import MetaTrader5 as mt5
                self.mt5 = mt5
            except ImportError:
                logger.warning("MetaTrader5 package not installed. Running in simulation mode.")
                logger.info("To use live MT5 connection, install: pip install MetaTrader5")
                self.connected = True  # Simulation mode
                return True
            
            # Initialize MT5 connection
            if self.path:
                if not self.mt5.initialize(self.path):
                    logger.error(f"MT5 initialize() failed: {self.mt5.last_error()}")
                    return False
            else:
                if not self.mt5.initialize():
                    logger.error(f"MT5 initialize() failed: {self.mt5.last_error()}")
                    return False
            
            # Login to account
            if self.account and self.password and self.server:
                authorized = self.mt5.login(
                    login=int(self.account),
                    password=self.password,
                    server=self.server,
                    timeout=self.timeout
                )
                if not authorized:
                    logger.error(f"MT5 login failed: {self.mt5.last_error()}")
                    self.mt5.shutdown()
                    return False
            
            self.connected = True
            logger.info("Successfully connected to MT5")
            return True
            
        except Exception as e:
            logger.error(f"Error connecting to MT5: {e}")
            return False
    
    def disconnect(self) -> bool:
        """
        Disconnect from MT5 platform
        断开MT5连接
        
        Returns:
            True if disconnection successful, False otherwise
        """
        try:
            if self.mt5:
                self.mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MT5")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from MT5: {e}")
            return False
    
    def get_market_data(self, symbol: str, timeframe: str = "1m", 
                       count: int = 100) -> List[MarketData]:
        """
        Get historical market data from MT5
        从MT5获取历史市场数据
        
        Args:
            symbol: Symbol (e.g., "EURUSD", "GBPUSD")
            timeframe: Timeframe ("1m", "5m", "15m", "30m", "1h", "4h", "1d")
            count: Number of bars to retrieve
            
        Returns:
            List of MarketData objects
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return []
        
        if not self.mt5:
            logger.warning("MT5 package not available, returning empty data")
            return []
        
        try:
            # Map timeframe string to MT5 timeframe constant
            timeframe_map = {
                "1m": self.mt5.TIMEFRAME_M1,
                "5m": self.mt5.TIMEFRAME_M5,
                "15m": self.mt5.TIMEFRAME_M15,
                "30m": self.mt5.TIMEFRAME_M30,
                "1h": self.mt5.TIMEFRAME_H1,
                "4h": self.mt5.TIMEFRAME_H4,
                "1d": self.mt5.TIMEFRAME_D1,
            }
            
            mt5_timeframe = timeframe_map.get(timeframe, self.mt5.TIMEFRAME_M1)
            
            # Get rates
            rates = self.mt5.copy_rates_from_pos(symbol, mt5_timeframe, 0, count)
            
            if rates is None or len(rates) == 0:
                logger.warning(f"No data received for {symbol}")
                return []
            
            # Convert to MarketData objects
            market_data = []
            for rate in rates:
                data = MarketData(
                    symbol=symbol,
                    timestamp=datetime.fromtimestamp(rate['time']),
                    open=Decimal(str(rate['open'])),
                    high=Decimal(str(rate['high'])),
                    low=Decimal(str(rate['low'])),
                    close=Decimal(str(rate['close'])),
                    volume=int(rate['tick_volume'])
                )
                market_data.append(data)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error getting market data from MT5: {e}")
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
            logger.error("Not connected to MT5")
            return False
        
        self._subscriptions[symbol] = callback
        logger.info(f"Subscribed to market data for {symbol}")
        return True
    
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
            del self._subscriptions[symbol]
            logger.info(f"Unsubscribed from market data for {symbol}")
            return True
        return False
    
    def place_order(self, order: Order) -> Optional[str]:
        """
        Place an order on MT5
        在MT5上下单
        
        Args:
            order: Order object to place
            
        Returns:
            MT5 order ticket if successful, None otherwise
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return None
        
        if not self.mt5:
            logger.warning("MT5 package not available, simulating order placement")
            return f"SIM-{order.order_id}"
        
        try:
            # Prepare order request
            request = {
                "action": self.mt5.TRADE_ACTION_DEAL,
                "symbol": order.symbol,
                # MT5 uses lot size (volume). 1 lot = 100 shares for most instruments.
                # Note: This may vary by broker and instrument type (e.g., forex uses different lot sizes)
                "volume": float(order.quantity) / 100,  # Convert shares to lots
                "type": self._convert_order_type(order.order_type, order.side),
                "deviation": 20,
                "magic": 234000,
                "comment": f"Order {order.order_id}",
                "type_time": self.mt5.ORDER_TIME_GTC,
                "type_filling": self.mt5.ORDER_FILLING_IOC,
            }
            
            # Add price for limit/stop orders
            if order.price and order.order_type != OrderType.MARKET:
                request["price"] = float(order.price)
            
            # Send order
            result = self.mt5.order_send(request)
            
            if result.retcode != self.mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order failed: {result.comment}")
                return None
            
            logger.info(f"Order placed successfully: {result.order}")
            return str(result.order)
            
        except Exception as e:
            logger.error(f"Error placing order on MT5: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order on MT5
        取消MT5订单
        
        Args:
            order_id: Order ticket number
            
        Returns:
            True if cancellation successful, False otherwise
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return False
        
        if not self.mt5:
            logger.warning("MT5 package not available, simulating order cancellation")
            return True
        
        try:
            request = {
                "action": self.mt5.TRADE_ACTION_REMOVE,
                "order": int(order_id),
            }
            
            result = self.mt5.order_send(request)
            
            if result.retcode != self.mt5.TRADE_RETCODE_DONE:
                logger.error(f"Order cancellation failed: {result.comment}")
                return False
            
            logger.info(f"Order cancelled successfully: {order_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error cancelling order on MT5: {e}")
            return False
    
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get MT5 account information
        获取MT5账户信息
        
        Returns:
            Dictionary containing account information
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return {}
        
        if not self.mt5:
            logger.warning("MT5 package not available, returning simulated account info")
            return {
                "balance": Decimal("10000.00"),
                "equity": Decimal("10000.00"),
                "margin": Decimal("0.00"),
                "free_margin": Decimal("10000.00"),
                "margin_level": Decimal("0.00"),
                "profit": Decimal("0.00"),
            }
        
        try:
            account_info = self.mt5.account_info()
            if account_info is None:
                return {}
            
            return {
                "balance": Decimal(str(account_info.balance)),
                "equity": Decimal(str(account_info.equity)),
                "margin": Decimal(str(account_info.margin)),
                "free_margin": Decimal(str(account_info.margin_free)),
                "margin_level": Decimal(str(account_info.margin_level)) if account_info.margin_level else Decimal("0"),
                "profit": Decimal(str(account_info.profit)),
            }
            
        except Exception as e:
            logger.error(f"Error getting account info from MT5: {e}")
            return {}
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions from MT5
        获取MT5当前持仓
        
        Returns:
            List of position dictionaries
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return []
        
        if not self.mt5:
            logger.warning("MT5 package not available, returning empty positions")
            return []
        
        try:
            positions = self.mt5.positions_get()
            if positions is None or len(positions) == 0:
                return []
            
            result = []
            for pos in positions:
                result.append({
                    "symbol": pos.symbol,
                    "volume": pos.volume,
                    "type": "buy" if pos.type == 0 else "sell",
                    "price": Decimal(str(pos.price_open)),
                    "current_price": Decimal(str(pos.price_current)),
                    "profit": Decimal(str(pos.profit)),
                    "swap": Decimal(str(pos.swap)),
                    "ticket": pos.ticket,
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting positions from MT5: {e}")
            return []
    
    def get_orders(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get orders from MT5
        获取MT5订单列表
        
        Args:
            active_only: If True, only return active orders
            
        Returns:
            List of order dictionaries
        """
        if not self.connected:
            logger.error("Not connected to MT5")
            return []
        
        if not self.mt5:
            logger.warning("MT5 package not available, returning empty orders")
            return []
        
        try:
            if active_only:
                orders = self.mt5.orders_get()
            else:
                orders = self.mt5.history_orders_get(
                    datetime.now() - timedelta(days=7),
                    datetime.now()
                )
            
            if orders is None or len(orders) == 0:
                return []
            
            result = []
            for order in orders:
                result.append({
                    "ticket": order.ticket,
                    "symbol": order.symbol,
                    "type": order.type,
                    "volume": order.volume_initial,
                    "price": Decimal(str(order.price_open)),
                    "state": order.state,
                    "time_setup": datetime.fromtimestamp(order.time_setup),
                })
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting orders from MT5: {e}")
            return []
    
    def _convert_order_type(self, order_type: OrderType, side: OrderSide) -> int:
        """
        Convert order type to MT5 order type constant
        
        Args:
            order_type: Order type
            side: Order side
            
        Returns:
            MT5 order type constant
        """
        if not self.mt5:
            return 0
        
        if order_type == OrderType.MARKET:
            return self.mt5.ORDER_TYPE_BUY if side == OrderSide.BUY else self.mt5.ORDER_TYPE_SELL
        elif order_type == OrderType.LIMIT:
            return self.mt5.ORDER_TYPE_BUY_LIMIT if side == OrderSide.BUY else self.mt5.ORDER_TYPE_SELL_LIMIT
        elif order_type == OrderType.STOP:
            return self.mt5.ORDER_TYPE_BUY_STOP if side == OrderSide.BUY else self.mt5.ORDER_TYPE_SELL_STOP
        
        return self.mt5.ORDER_TYPE_BUY
