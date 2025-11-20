"""
Data models for the trading system (交易系统数据模型)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from decimal import Decimal


class OrderType(Enum):
    """订单类型"""
    MARKET = "market"  # 市价单
    LIMIT = "limit"    # 限价单
    STOP = "stop"      # 止损单


class OrderSide(Enum):
    """订单方向"""
    BUY = "buy"   # 买入
    SELL = "sell" # 卖出


class OrderStatus(Enum):
    """订单状态"""
    PENDING = "pending"       # 待提交
    SUBMITTED = "submitted"   # 已提交
    PARTIAL = "partial"       # 部分成交
    FILLED = "filled"         # 完全成交
    CANCELLED = "cancelled"   # 已取消
    REJECTED = "rejected"     # 已拒绝


@dataclass
class MarketData:
    """市场数据"""
    symbol: str                    # 股票代码
    timestamp: datetime            # 时间戳
    open: Decimal                  # 开盘价
    high: Decimal                  # 最高价
    low: Decimal                   # 最低价
    close: Decimal                 # 收盘价
    volume: int                    # 成交量
    
    def __post_init__(self):
        """确保价格为Decimal类型"""
        if not isinstance(self.open, Decimal):
            self.open = Decimal(str(self.open))
        if not isinstance(self.high, Decimal):
            self.high = Decimal(str(self.high))
        if not isinstance(self.low, Decimal):
            self.low = Decimal(str(self.low))
        if not isinstance(self.close, Decimal):
            self.close = Decimal(str(self.close))


@dataclass
class Order:
    """订单"""
    order_id: str                  # 订单ID
    symbol: str                    # 股票代码
    side: OrderSide                # 买卖方向
    order_type: OrderType          # 订单类型
    quantity: int                  # 数量
    price: Optional[Decimal] = None  # 价格（市价单可为None）
    status: OrderStatus = OrderStatus.PENDING  # 订单状态
    filled_quantity: int = 0       # 已成交数量
    average_price: Decimal = Decimal('0')  # 成交均价
    created_time: datetime = field(default_factory=datetime.now)  # 创建时间
    updated_time: datetime = field(default_factory=datetime.now)  # 更新时间
    
    def __post_init__(self):
        """确保价格为Decimal类型"""
        if self.price and not isinstance(self.price, Decimal):
            self.price = Decimal(str(self.price))
        if not isinstance(self.average_price, Decimal):
            self.average_price = Decimal(str(self.average_price))
    
    @property
    def is_filled(self) -> bool:
        """是否完全成交"""
        return self.status == OrderStatus.FILLED
    
    @property
    def is_active(self) -> bool:
        """是否为活跃订单"""
        return self.status in [OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL]


@dataclass
class Trade:
    """成交记录"""
    trade_id: str                  # 成交ID
    order_id: str                  # 订单ID
    symbol: str                    # 股票代码
    side: OrderSide                # 买卖方向
    quantity: int                  # 成交数量
    price: Decimal                 # 成交价格
    timestamp: datetime = field(default_factory=datetime.now)  # 成交时间
    
    def __post_init__(self):
        """确保价格为Decimal类型"""
        if not isinstance(self.price, Decimal):
            self.price = Decimal(str(self.price))
    
    @property
    def value(self) -> Decimal:
        """成交金额"""
        return self.price * self.quantity


@dataclass
class Position:
    """持仓"""
    symbol: str                    # 股票代码
    quantity: int = 0              # 持仓数量（正数为多头，负数为空头）
    average_cost: Decimal = Decimal('0')  # 平均成本
    realized_pnl: Decimal = Decimal('0')  # 已实现盈亏
    
    def __post_init__(self):
        """确保价格为Decimal类型"""
        if not isinstance(self.average_cost, Decimal):
            self.average_cost = Decimal(str(self.average_cost))
        if not isinstance(self.realized_pnl, Decimal):
            self.realized_pnl = Decimal(str(self.realized_pnl))
    
    def update(self, trade: Trade):
        """根据成交更新持仓"""
        if trade.side == OrderSide.BUY:
            # 买入：增加持仓
            total_cost = self.average_cost * abs(self.quantity) + trade.price * trade.quantity
            self.quantity += trade.quantity
            if self.quantity != 0:
                self.average_cost = total_cost / abs(self.quantity)
        else:
            # 卖出：减少持仓
            if self.quantity > 0:
                # 平多仓
                close_quantity = min(trade.quantity, self.quantity)
                self.realized_pnl += (trade.price - self.average_cost) * close_quantity
                self.quantity -= trade.quantity
            else:
                # 开空仓或平空仓
                self.quantity -= trade.quantity
    
    def unrealized_pnl(self, current_price: Decimal) -> Decimal:
        """计算未实现盈亏"""
        if not isinstance(current_price, Decimal):
            current_price = Decimal(str(current_price))
        if self.quantity == 0:
            return Decimal('0')
        return (current_price - self.average_cost) * self.quantity
    
    def total_pnl(self, current_price: Decimal) -> Decimal:
        """计算总盈亏"""
        return self.realized_pnl + self.unrealized_pnl(current_price)
