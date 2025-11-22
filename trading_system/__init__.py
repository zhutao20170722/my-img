"""
Day Trading System (日内交易系统)
A comprehensive intraday trading system with order management, risk control, and strategy execution.
"""

__version__ = "1.0.0"
__author__ = "Day Trading System"

from .models import Order, Position, Trade, MarketData
from .strategies import BaseStrategy, MomentumStrategy, MeanReversionStrategy
from .order_manager import OrderManager
from .risk_manager import RiskManager
from .trading_engine import TradingEngine
from .backtesting import BacktestResult, BacktestAnalyzer
from .connectors import BaseConnector, MT5Connector, IBConnector

__all__ = [
    "Order",
    "Position", 
    "Trade",
    "MarketData",
    "BaseStrategy",
    "MomentumStrategy",
    "MeanReversionStrategy",
    "OrderManager",
    "RiskManager",
    "TradingEngine",
    "BacktestResult",
    "BacktestAnalyzer",
    "BaseConnector",
    "MT5Connector",
    "IBConnector",
]
