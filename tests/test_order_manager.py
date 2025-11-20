"""
Unit tests for order manager
"""

import unittest
from decimal import Decimal

from trading_system.models import OrderType, OrderSide, OrderStatus
from trading_system.order_manager import OrderManager


class TestOrderManager(unittest.TestCase):
    """测试订单管理器"""
    
    def setUp(self):
        """每个测试前初始化"""
        self.manager = OrderManager()
    
    def test_create_order(self):
        """测试创建订单"""
        order = self.manager.create_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=Decimal('150.0')
        )
        
        self.assertIsNotNone(order.order_id)
        self.assertEqual(order.symbol, "AAPL")
        self.assertEqual(order.quantity, 100)
        self.assertEqual(order.status, OrderStatus.PENDING)
    
    def test_submit_order(self):
        """测试提交订单"""
        order = self.manager.create_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100
        )
        
        success = self.manager.submit_order(order)
        
        self.assertTrue(success)
        self.assertEqual(order.status, OrderStatus.SUBMITTED)
    
    def test_cancel_order(self):
        """测试取消订单"""
        order = self.manager.create_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=Decimal('150.0')
        )
        self.manager.submit_order(order)
        
        success = self.manager.cancel_order(order.order_id)
        
        self.assertTrue(success)
        self.assertEqual(order.status, OrderStatus.CANCELLED)
    
    def test_fill_order(self):
        """测试订单成交"""
        order = self.manager.create_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100
        )
        self.manager.submit_order(order)
        
        trade = self.manager.fill_order(
            order.order_id,
            fill_quantity=100,
            fill_price=Decimal('150.0')
        )
        
        self.assertIsNotNone(trade)
        self.assertEqual(order.status, OrderStatus.FILLED)
        self.assertEqual(order.filled_quantity, 100)
        self.assertEqual(order.average_price, Decimal('150.0'))
    
    def test_partial_fill_order(self):
        """测试订单部分成交"""
        order = self.manager.create_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=Decimal('150.0')
        )
        self.manager.submit_order(order)
        
        # 第一次部分成交
        trade1 = self.manager.fill_order(
            order.order_id,
            fill_quantity=50,
            fill_price=Decimal('150.0')
        )
        
        self.assertEqual(order.status, OrderStatus.PARTIAL)
        self.assertEqual(order.filled_quantity, 50)
        
        # 第二次成交完毕
        trade2 = self.manager.fill_order(
            order.order_id,
            fill_quantity=50,
            fill_price=Decimal('151.0')
        )
        
        self.assertEqual(order.status, OrderStatus.FILLED)
        self.assertEqual(order.filled_quantity, 100)
        self.assertEqual(order.average_price, Decimal('150.5'))
    
    def test_get_active_orders(self):
        """测试获取活跃订单"""
        order1 = self.manager.create_order(
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100
        )
        self.manager.submit_order(order1)
        
        order2 = self.manager.create_order(
            symbol="TSLA",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=50,
            price=Decimal('200.0')
        )
        self.manager.submit_order(order2)
        
        active_orders = self.manager.get_active_orders()
        self.assertEqual(len(active_orders), 2)
        
        active_aapl = self.manager.get_active_orders(symbol="AAPL")
        self.assertEqual(len(active_aapl), 1)
        self.assertEqual(active_aapl[0].symbol, "AAPL")


if __name__ == '__main__':
    unittest.main()
