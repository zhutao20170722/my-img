"""
Trading strategies (交易策略)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from decimal import Decimal
from .models import MarketData, OrderSide, OrderType


class BaseStrategy(ABC):
    """基础策略类"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
    
    @abstractmethod
    def generate_signals(self, market_data: List[MarketData]) -> Optional[dict]:
        """
        生成交易信号
        
        Args:
            market_data: 市场数据列表（按时间排序）
            
        Returns:
            交易信号字典，包含 {
                'side': OrderSide,
                'symbol': str,
                'quantity': int,
                'order_type': OrderType,
                'price': Optional[Decimal]
            } 或 None（无信号）
        """
        pass


class MomentumStrategy(BaseStrategy):
    """动量策略"""
    
    def __init__(self, 
                 name: str = "Momentum",
                 short_period: int = 5,
                 long_period: int = 20,
                 quantity: int = 100):
        """
        初始化动量策略
        
        Args:
            name: 策略名称
            short_period: 短期均线周期
            long_period: 长期均线周期
            quantity: 每次交易数量
        """
        super().__init__(name)
        self.short_period = short_period
        self.long_period = long_period
        self.quantity = quantity
        self.last_signal = None
    
    def _calculate_sma(self, data: List[MarketData], period: int) -> Optional[Decimal]:
        """计算简单移动平均线"""
        if len(data) < period:
            return None
        
        prices = [d.close for d in data[-period:]]
        return sum(prices) / len(prices)
    
    def generate_signals(self, market_data: List[MarketData]) -> Optional[dict]:
        """
        动量策略信号生成：
        - 短期均线上穿长期均线：买入信号
        - 短期均线下穿长期均线：卖出信号
        """
        if not self.enabled or len(market_data) < self.long_period:
            return None
        
        # 计算当前和前一周期的均线
        current_short_sma = self._calculate_sma(market_data, self.short_period)
        current_long_sma = self._calculate_sma(market_data, self.long_period)
        
        prev_short_sma = self._calculate_sma(market_data[:-1], self.short_period)
        prev_long_sma = self._calculate_sma(market_data[:-1], self.long_period)
        
        if not all([current_short_sma, current_long_sma, prev_short_sma, prev_long_sma]):
            return None
        
        symbol = market_data[-1].symbol
        
        # 金叉：短期均线上穿长期均线
        if prev_short_sma <= prev_long_sma and current_short_sma > current_long_sma:
            if self.last_signal != "BUY":
                self.last_signal = "BUY"
                return {
                    'side': OrderSide.BUY,
                    'symbol': symbol,
                    'quantity': self.quantity,
                    'order_type': OrderType.MARKET,
                    'price': None
                }
        
        # 死叉：短期均线下穿长期均线
        elif prev_short_sma >= prev_long_sma and current_short_sma < current_long_sma:
            if self.last_signal != "SELL":
                self.last_signal = "SELL"
                return {
                    'side': OrderSide.SELL,
                    'symbol': symbol,
                    'quantity': self.quantity,
                    'order_type': OrderType.MARKET,
                    'price': None
                }
        
        return None


class MeanReversionStrategy(BaseStrategy):
    """均值回归策略"""
    
    def __init__(self,
                 name: str = "MeanReversion",
                 period: int = 20,
                 std_multiplier: float = 2.0,
                 quantity: int = 100):
        """
        初始化均值回归策略
        
        Args:
            name: 策略名称
            period: 计算周期
            std_multiplier: 标准差倍数
            quantity: 每次交易数量
        """
        super().__init__(name)
        self.period = period
        self.std_multiplier = Decimal(str(std_multiplier))
        self.quantity = quantity
    
    def _calculate_bollinger_bands(self, data: List[MarketData]) -> Optional[tuple]:
        """计算布林带"""
        if len(data) < self.period:
            return None
        
        prices = [d.close for d in data[-self.period:]]
        mean = sum(prices) / len(prices)
        
        # 计算标准差
        variance = sum((p - mean) ** 2 for p in prices) / len(prices)
        std = variance ** Decimal('0.5')
        
        upper_band = mean + self.std_multiplier * std
        lower_band = mean - self.std_multiplier * std
        
        return lower_band, mean, upper_band
    
    def generate_signals(self, market_data: List[MarketData]) -> Optional[dict]:
        """
        均值回归策略信号生成：
        - 价格触及下轨：买入信号
        - 价格触及上轨：卖出信号
        """
        if not self.enabled or len(market_data) < self.period:
            return None
        
        bands = self._calculate_bollinger_bands(market_data)
        if not bands:
            return None
        
        lower_band, middle_band, upper_band = bands
        current_price = market_data[-1].close
        symbol = market_data[-1].symbol
        
        # 价格触及下轨：超卖，买入信号
        if current_price <= lower_band:
            return {
                'side': OrderSide.BUY,
                'symbol': symbol,
                'quantity': self.quantity,
                'order_type': OrderType.LIMIT,
                'price': current_price
            }
        
        # 价格触及上轨：超买，卖出信号
        elif current_price >= upper_band:
            return {
                'side': OrderSide.SELL,
                'symbol': symbol,
                'quantity': self.quantity,
                'order_type': OrderType.LIMIT,
                'price': current_price
            }
        
        return None
