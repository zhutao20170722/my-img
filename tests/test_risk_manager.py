"""
Unit tests for risk manager
"""

import unittest
from decimal import Decimal

from trading_system.models import Order, OrderType, OrderSide, Position
from trading_system.risk_manager import RiskManager


class TestRiskManager(unittest.TestCase):
    """测试风险管理器"""
    
    def setUp(self):
        """每个测试前初始化"""
        self.risk_manager = RiskManager(
            max_position_size=1000,
            max_order_value=Decimal('100000'),
            max_daily_loss=Decimal('10000'),
            max_positions=5
        )
    
    def test_check_order_passes(self):
        """测试通过风控检查的订单"""
        order = Order(
            order_id="test-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=Decimal('150.0')
        )
        
        positions = {}
        current_price = Decimal('150.0')
        
        passed, reason = self.risk_manager.check_order(order, positions, current_price)
        
        self.assertTrue(passed)
        self.assertEqual(reason, "通过风控检查")
    
    def test_check_order_exceeds_value(self):
        """测试订单金额超限"""
        order = Order(
            order_id="test-002",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=1000,
            price=Decimal('150.0')
        )
        
        positions = {}
        current_price = Decimal('150.0')
        
        passed, reason = self.risk_manager.check_order(order, positions, current_price)
        
        self.assertFalse(passed)
        self.assertIn("订单金额", reason)
    
    def test_check_order_exceeds_position_size(self):
        """测试持仓数量超限"""
        order = Order(
            order_id="test-003",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=600,
            price=Decimal('150.0')
        )
        
        positions = {
            "AAPL": Position(
                symbol="AAPL",
                quantity=500,
                average_cost=Decimal('145.0')
            )
        }
        current_price = Decimal('150.0')
        
        passed, reason = self.risk_manager.check_order(order, positions, current_price)
        
        self.assertFalse(passed)
        self.assertIn("持仓数量", reason)
    
    def test_check_order_exceeds_max_positions(self):
        """测试持仓标的数量超限"""
        order = Order(
            order_id="test-004",
            symbol="NEW",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=Decimal('50.0')
        )
        
        # 已有5个持仓
        positions = {
            f"STOCK{i}": Position(symbol=f"STOCK{i}", quantity=100)
            for i in range(5)
        }
        current_price = Decimal('50.0')
        
        passed, reason = self.risk_manager.check_order(order, positions, current_price)
        
        self.assertFalse(passed)
        self.assertIn("持仓数量已达上限", reason)
    
    def test_check_order_daily_loss_limit(self):
        """测试当日亏损超限"""
        self.risk_manager.daily_pnl = Decimal('-11000')
        
        order = Order(
            order_id="test-005",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=Decimal('150.0')
        )
        
        positions = {}
        current_price = Decimal('150.0')
        
        passed, reason = self.risk_manager.check_order(order, positions, current_price)
        
        self.assertFalse(passed)
        self.assertIn("当日亏损", reason)
    
    def test_update_daily_pnl(self):
        """测试更新当日盈亏"""
        self.assertEqual(self.risk_manager.daily_pnl, Decimal('0'))
        
        self.risk_manager.update_daily_pnl(Decimal('1000'))
        self.assertEqual(self.risk_manager.daily_pnl, Decimal('1000'))
        
        self.risk_manager.update_daily_pnl(Decimal('-500'))
        self.assertEqual(self.risk_manager.daily_pnl, Decimal('500'))
    
    def test_reset_daily_pnl(self):
        """测试重置当日盈亏"""
        self.risk_manager.update_daily_pnl(Decimal('1000'))
        self.risk_manager.reset_daily_pnl()
        
        self.assertEqual(self.risk_manager.daily_pnl, Decimal('0'))
    
    def test_get_risk_metrics(self):
        """测试获取风控指标"""
        metrics = self.risk_manager.get_risk_metrics()
        
        self.assertIn('max_position_size', metrics)
        self.assertIn('daily_pnl', metrics)
        self.assertEqual(metrics['max_positions'], 5)


if __name__ == '__main__':
    unittest.main()
