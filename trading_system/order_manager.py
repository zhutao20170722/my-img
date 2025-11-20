"""
Order Manager (订单管理器)
"""

from typing import Dict, List, Optional
from datetime import datetime
from decimal import Decimal
import uuid

from .models import Order, OrderStatus, OrderType, Trade, OrderSide


class OrderManager:
    """订单管理器"""
    
    def __init__(self):
        self.orders: Dict[str, Order] = {}
        self.trades: List[Trade] = []
    
    def create_order(self,
                    symbol: str,
                    side: OrderSide,
                    order_type: OrderType,
                    quantity: int,
                    price: Optional[Decimal] = None) -> Order:
        """
        创建订单
        
        Args:
            symbol: 股票代码
            side: 买卖方向
            order_type: 订单类型
            quantity: 数量
            price: 价格（市价单可为None）
            
        Returns:
            创建的订单
        """
        order_id = str(uuid.uuid4())
        order = Order(
            order_id=order_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        self.orders[order_id] = order
        return order
    
    def submit_order(self, order: Order) -> bool:
        """
        提交订单
        
        Args:
            order: 订单对象
            
        Returns:
            是否提交成功
        """
        if order.status != OrderStatus.PENDING:
            return False
        
        order.status = OrderStatus.SUBMITTED
        order.updated_time = datetime.now()
        return True
    
    def cancel_order(self, order_id: str) -> bool:
        """
        取消订单
        
        Args:
            order_id: 订单ID
            
        Returns:
            是否取消成功
        """
        order = self.orders.get(order_id)
        if not order or not order.is_active:
            return False
        
        order.status = OrderStatus.CANCELLED
        order.updated_time = datetime.now()
        return True
    
    def fill_order(self,
                   order_id: str,
                   fill_quantity: int,
                   fill_price: Decimal) -> Optional[Trade]:
        """
        订单成交
        
        Args:
            order_id: 订单ID
            fill_quantity: 成交数量
            fill_price: 成交价格
            
        Returns:
            成交记录
        """
        order = self.orders.get(order_id)
        if not order or not order.is_active:
            return None
        
        if not isinstance(fill_price, Decimal):
            fill_price = Decimal(str(fill_price))
        
        # 更新订单状态
        remaining_quantity = order.quantity - order.filled_quantity
        actual_fill_quantity = min(fill_quantity, remaining_quantity)
        
        # 更新成交均价
        total_filled = order.filled_quantity + actual_fill_quantity
        order.average_price = (
            (order.average_price * order.filled_quantity + fill_price * actual_fill_quantity)
            / total_filled
        )
        
        order.filled_quantity += actual_fill_quantity
        
        # 更新订单状态
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIAL
        
        order.updated_time = datetime.now()
        
        # 创建成交记录
        trade = Trade(
            trade_id=str(uuid.uuid4()),
            order_id=order_id,
            symbol=order.symbol,
            side=order.side,
            quantity=actual_fill_quantity,
            price=fill_price
        )
        self.trades.append(trade)
        
        return trade
    
    def get_order(self, order_id: str) -> Optional[Order]:
        """获取订单"""
        return self.orders.get(order_id)
    
    def get_active_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """获取活跃订单"""
        active_orders = [o for o in self.orders.values() if o.is_active]
        if symbol:
            active_orders = [o for o in active_orders if o.symbol == symbol]
        return active_orders
    
    def get_trades(self, symbol: Optional[str] = None) -> List[Trade]:
        """获取成交记录"""
        if symbol:
            return [t for t in self.trades if t.symbol == symbol]
        return self.trades
    
    def get_order_history(self, symbol: Optional[str] = None) -> List[Order]:
        """获取订单历史"""
        orders = list(self.orders.values())
        if symbol:
            orders = [o for o in orders if o.symbol == symbol]
        return sorted(orders, key=lambda x: x.created_time, reverse=True)
