"""
Risk Manager (风险管理器)
"""

from typing import Dict, Optional
from decimal import Decimal
from .models import Order, Position, OrderSide


class RiskManager:
    """风险管理器"""
    
    def __init__(self,
                 max_position_size: int = 1000,
                 max_order_value: Decimal = Decimal('100000'),
                 max_daily_loss: Decimal = Decimal('10000'),
                 max_positions: int = 10):
        """
        初始化风险管理器
        
        Args:
            max_position_size: 单个持仓最大数量
            max_order_value: 单笔订单最大金额
            max_daily_loss: 单日最大亏损
            max_positions: 最大持仓数量
        """
        self.max_position_size = max_position_size
        self.max_order_value = max_order_value
        self.max_daily_loss = max_daily_loss
        self.max_positions = max_positions
        self.daily_pnl = Decimal('0')
    
    def check_order(self,
                   order: Order,
                   positions: Dict[str, Position],
                   current_price: Decimal) -> tuple[bool, str]:
        """
        检查订单是否符合风控要求
        
        Args:
            order: 订单
            positions: 当前持仓字典
            current_price: 当前价格
            
        Returns:
            (是否通过, 原因)
        """
        if not isinstance(current_price, Decimal):
            current_price = Decimal(str(current_price))
        
        # 检查订单金额
        order_value = current_price * order.quantity
        if order_value > self.max_order_value:
            return False, f"订单金额 {order_value} 超过最大限制 {self.max_order_value}"
        
        # 检查持仓数量限制
        if order.side == OrderSide.BUY and len(positions) >= self.max_positions:
            if order.symbol not in positions:
                return False, f"持仓数量已达上限 {self.max_positions}"
        
        # 检查单个持仓大小
        current_position = positions.get(order.symbol)
        if current_position:
            new_quantity = current_position.quantity
            if order.side == OrderSide.BUY:
                new_quantity += order.quantity
            else:
                new_quantity -= order.quantity
            
            if abs(new_quantity) > self.max_position_size:
                return False, f"持仓数量 {abs(new_quantity)} 超过最大限制 {self.max_position_size}"
        else:
            if order.quantity > self.max_position_size:
                return False, f"持仓数量 {order.quantity} 超过最大限制 {self.max_position_size}"
        
        # 检查当日亏损
        if self.daily_pnl < -abs(self.max_daily_loss):
            return False, f"当日亏损 {abs(self.daily_pnl)} 已达上限 {self.max_daily_loss}"
        
        return True, "通过风控检查"
    
    def update_daily_pnl(self, pnl: Decimal):
        """更新当日盈亏"""
        if not isinstance(pnl, Decimal):
            pnl = Decimal(str(pnl))
        self.daily_pnl += pnl
    
    def reset_daily_pnl(self):
        """重置当日盈亏（每日开盘前调用）"""
        self.daily_pnl = Decimal('0')
    
    def get_position_limit(self, symbol: str) -> int:
        """获取某个标的的持仓限制"""
        return self.max_position_size
    
    def set_position_limit(self, max_position_size: int):
        """设置持仓限制"""
        self.max_position_size = max_position_size
    
    def get_risk_metrics(self) -> dict:
        """获取风控指标"""
        return {
            'max_position_size': self.max_position_size,
            'max_order_value': self.max_order_value,
            'max_daily_loss': self.max_daily_loss,
            'max_positions': self.max_positions,
            'daily_pnl': self.daily_pnl,
            'daily_loss_remaining': self.max_daily_loss + self.daily_pnl
        }
