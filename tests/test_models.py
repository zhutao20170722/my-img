"""
Unit tests for trading system models
"""

import unittest
from datetime import datetime
from decimal import Decimal

from trading_system.models import (
    Order, OrderType, OrderSide, OrderStatus,
    Position, Trade, MarketData
)


class TestMarketData(unittest.TestCase):
    """测试市场数据模型"""
    
    def test_market_data_creation(self):
        """测试创建市场数据"""
        data = MarketData(
            symbol="AAPL",
            timestamp=datetime.now(),
            open=Decimal('150.0'),
            high=Decimal('152.0'),
            low=Decimal('149.0'),
            close=Decimal('151.0'),
            volume=1000000
        )
        
        self.assertEqual(data.symbol, "AAPL")
        self.assertIsInstance(data.open, Decimal)
        self.assertEqual(data.volume, 1000000)


class TestOrder(unittest.TestCase):
    """测试订单模型"""
    
    def test_order_creation(self):
        """测试创建订单"""
        order = Order(
            order_id="test-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=100,
            price=Decimal('150.0')
        )
        
        self.assertEqual(order.order_id, "test-001")
        self.assertEqual(order.quantity, 100)
        self.assertEqual(order.status, OrderStatus.PENDING)
        self.assertTrue(order.is_active)
        self.assertFalse(order.is_filled)
    
    def test_order_filled_status(self):
        """测试订单成交状态"""
        order = Order(
            order_id="test-002",
            symbol="AAPL",
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=100,
            status=OrderStatus.FILLED,
            filled_quantity=100
        )
        
        self.assertTrue(order.is_filled)
        self.assertFalse(order.is_active)


class TestTrade(unittest.TestCase):
    """测试成交记录模型"""
    
    def test_trade_creation(self):
        """测试创建成交记录"""
        trade = Trade(
            trade_id="trade-001",
            order_id="order-001",
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            price=Decimal('150.0')
        )
        
        self.assertEqual(trade.quantity, 100)
        self.assertEqual(trade.value, Decimal('15000.0'))


class TestPosition(unittest.TestCase):
    """测试持仓模型"""
    
    def test_position_creation(self):
        """测试创建持仓"""
        position = Position(symbol="AAPL")
        
        self.assertEqual(position.symbol, "AAPL")
        self.assertEqual(position.quantity, 0)
        self.assertEqual(position.average_cost, Decimal('0'))
    
    def test_position_buy(self):
        """测试买入更新持仓"""
        position = Position(symbol="AAPL")
        
        # 第一次买入
        trade1 = Trade(
            trade_id="t1",
            order_id="o1",
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            price=Decimal('150.0')
        )
        position.update(trade1)
        
        self.assertEqual(position.quantity, 100)
        self.assertEqual(position.average_cost, Decimal('150.0'))
        
        # 第二次买入
        trade2 = Trade(
            trade_id="t2",
            order_id="o2",
            symbol="AAPL",
            side=OrderSide.BUY,
            quantity=100,
            price=Decimal('160.0')
        )
        position.update(trade2)
        
        self.assertEqual(position.quantity, 200)
        self.assertEqual(position.average_cost, Decimal('155.0'))
    
    def test_position_sell(self):
        """测试卖出更新持仓"""
        position = Position(
            symbol="AAPL",
            quantity=100,
            average_cost=Decimal('150.0')
        )
        
        # 卖出
        trade = Trade(
            trade_id="t1",
            order_id="o1",
            symbol="AAPL",
            side=OrderSide.SELL,
            quantity=50,
            price=Decimal('160.0')
        )
        position.update(trade)
        
        self.assertEqual(position.quantity, 50)
        self.assertEqual(position.realized_pnl, Decimal('500.0'))  # (160-150)*50
    
    def test_unrealized_pnl(self):
        """测试未实现盈亏计算"""
        position = Position(
            symbol="AAPL",
            quantity=100,
            average_cost=Decimal('150.0')
        )
        
        current_price = Decimal('160.0')
        unrealized = position.unrealized_pnl(current_price)
        
        self.assertEqual(unrealized, Decimal('1000.0'))  # (160-150)*100
    
    def test_total_pnl(self):
        """测试总盈亏计算"""
        position = Position(
            symbol="AAPL",
            quantity=100,
            average_cost=Decimal('150.0'),
            realized_pnl=Decimal('500.0')
        )
        
        current_price = Decimal('160.0')
        total = position.total_pnl(current_price)
        
        # 已实现盈亏500 + 未实现盈亏1000 = 1500
        self.assertEqual(total, Decimal('1500.0'))


if __name__ == '__main__':
    unittest.main()
