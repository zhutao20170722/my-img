"""
Base connector interface for trading platforms
交易平台基础连接器接口
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

from ..models import MarketData, Order, Trade, OrderSide, OrderType


class BaseConnector(ABC):
    """
    Base class for platform connectors
    平台连接器基类
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize connector with configuration
        
        Args:
            config: Configuration dictionary with platform-specific settings
        """
        self.config = config
        self.connected = False
        
    @abstractmethod
    def connect(self) -> bool:
        """
        Connect to the trading platform
        连接到交易平台
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the trading platform
        断开与交易平台的连接
        
        Returns:
            True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_market_data(self, symbol: str, timeframe: str = "1m", 
                       count: int = 100) -> List[MarketData]:
        """
        Get historical market data
        获取历史市场数据
        
        Args:
            symbol: Symbol/ticker
            timeframe: Timeframe (e.g., "1m", "5m", "1h", "1d")
            count: Number of bars to retrieve
            
        Returns:
            List of MarketData objects
        """
        pass
    
    @abstractmethod
    def subscribe_market_data(self, symbol: str, callback) -> bool:
        """
        Subscribe to real-time market data
        订阅实时市场数据
        
        Args:
            symbol: Symbol/ticker
            callback: Callback function to receive market data
            
        Returns:
            True if subscription successful, False otherwise
        """
        pass
    
    @abstractmethod
    def unsubscribe_market_data(self, symbol: str) -> bool:
        """
        Unsubscribe from real-time market data
        取消订阅实时市场数据
        
        Args:
            symbol: Symbol/ticker
            
        Returns:
            True if unsubscription successful, False otherwise
        """
        pass
    
    @abstractmethod
    def place_order(self, order: Order) -> Optional[str]:
        """
        Place an order on the platform
        在平台上下单
        
        Args:
            order: Order object to place
            
        Returns:
            Platform order ID if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str) -> bool:
        """
        Cancel an order
        取消订单
        
        Args:
            order_id: Order ID to cancel
            
        Returns:
            True if cancellation successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict[str, Any]:
        """
        Get account information
        获取账户信息
        
        Returns:
            Dictionary containing account information (balance, equity, etc.)
        """
        pass
    
    @abstractmethod
    def get_positions(self) -> List[Dict[str, Any]]:
        """
        Get current positions
        获取当前持仓
        
        Returns:
            List of position dictionaries
        """
        pass
    
    @abstractmethod
    def get_orders(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """
        Get orders
        获取订单列表
        
        Args:
            active_only: If True, only return active orders
            
        Returns:
            List of order dictionaries
        """
        pass
    
    def is_connected(self) -> bool:
        """
        Check if connected to platform
        检查是否已连接到平台
        
        Returns:
            True if connected, False otherwise
        """
        return self.connected
