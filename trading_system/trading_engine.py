"""
Trading Engine (交易引擎)
"""

from typing import Dict, List, Optional
from decimal import Decimal
from datetime import datetime

from .models import MarketData, Order, Position, Trade, OrderStatus
from .strategies import BaseStrategy
from .order_manager import OrderManager
from .risk_manager import RiskManager


class TradingEngine:
    """交易引擎 - 日内交易系统核心"""
    
    def __init__(self,
                 initial_capital: Decimal = Decimal('100000'),
                 risk_manager: Optional[RiskManager] = None,
                 order_manager: Optional[OrderManager] = None):
        """
        初始化交易引擎
        
        Args:
            initial_capital: 初始资金
            risk_manager: 风险管理器
            order_manager: 订单管理器
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.positions: Dict[str, Position] = {}
        self.strategies: List[BaseStrategy] = []
        
        self.risk_manager = risk_manager or RiskManager()
        self.order_manager = order_manager or OrderManager()
        
        self.market_data_buffer: Dict[str, List[MarketData]] = {}
        self.current_prices: Dict[str, Decimal] = {}
        
        self.is_running = False
    
    def add_strategy(self, strategy: BaseStrategy):
        """添加交易策略"""
        self.strategies.append(strategy)
    
    def remove_strategy(self, strategy_name: str):
        """移除交易策略"""
        self.strategies = [s for s in self.strategies if s.name != strategy_name]
    
    def on_market_data(self, market_data: MarketData):
        """
        处理市场数据
        
        Args:
            market_data: 市场数据
        """
        symbol = market_data.symbol
        
        # 更新市场数据缓冲区
        if symbol not in self.market_data_buffer:
            self.market_data_buffer[symbol] = []
        self.market_data_buffer[symbol].append(market_data)
        
        # 更新当前价格
        self.current_prices[symbol] = market_data.close
        
        # 生成交易信号
        if self.is_running:
            self._generate_signals(symbol)
            self._execute_orders()
    
    def _generate_signals(self, symbol: str):
        """根据策略生成交易信号"""
        if symbol not in self.market_data_buffer:
            return
        
        market_data = self.market_data_buffer[symbol]
        
        for strategy in self.strategies:
            if not strategy.enabled:
                continue
            
            signal = strategy.generate_signals(market_data)
            if signal:
                self._create_order_from_signal(signal)
    
    def _create_order_from_signal(self, signal: dict):
        """根据信号创建订单"""
        order = self.order_manager.create_order(
            symbol=signal['symbol'],
            side=signal['side'],
            order_type=signal['order_type'],
            quantity=signal['quantity'],
            price=signal.get('price')
        )
        
        # 风控检查
        current_price = self.current_prices.get(signal['symbol'])
        if current_price:
            passed, reason = self.risk_manager.check_order(
                order, self.positions, current_price
            )
            
            if passed:
                self.order_manager.submit_order(order)
            else:
                order.status = OrderStatus.REJECTED
                print(f"订单被拒绝: {reason}")
    
    def _execute_orders(self):
        """执行订单（模拟成交）"""
        active_orders = self.order_manager.get_active_orders()
        
        for order in active_orders:
            current_price = self.current_prices.get(order.symbol)
            if not current_price:
                continue
            
            # 简化的成交逻辑：市价单立即成交，限价单按条件成交
            should_fill = False
            fill_price = current_price
            
            if order.order_type.value == "market":
                should_fill = True
            elif order.order_type.value == "limit" and order.price:
                if order.side.value == "buy" and current_price <= order.price:
                    should_fill = True
                    fill_price = order.price
                elif order.side.value == "sell" and current_price >= order.price:
                    should_fill = True
                    fill_price = order.price
            
            if should_fill:
                trade = self.order_manager.fill_order(
                    order.order_id,
                    order.quantity - order.filled_quantity,
                    fill_price
                )
                
                if trade:
                    self._update_position(trade)
    
    def _update_position(self, trade: Trade):
        """更新持仓"""
        symbol = trade.symbol
        
        # 获取或创建持仓
        if symbol not in self.positions:
            self.positions[symbol] = Position(symbol=symbol)
        
        position = self.positions[symbol]
        old_quantity = position.quantity
        
        # 更新持仓
        position.update(trade)
        
        # 更新现金
        if trade.side.value == "buy":
            self.cash -= trade.value
        else:
            self.cash += trade.value
        
        # 如果持仓为0，移除
        if position.quantity == 0:
            self.risk_manager.update_daily_pnl(position.realized_pnl)
            del self.positions[symbol]
    
    def start(self):
        """启动交易引擎"""
        self.is_running = True
        print("交易引擎已启动")
    
    def stop(self):
        """停止交易引擎"""
        self.is_running = False
        
        # 取消所有活跃订单
        for order in self.order_manager.get_active_orders():
            self.order_manager.cancel_order(order.order_id)
        
        print("交易引擎已停止")
    
    def get_portfolio_value(self) -> Decimal:
        """计算投资组合总价值"""
        total_value = self.cash
        
        for symbol, position in self.positions.items():
            current_price = self.current_prices.get(symbol, Decimal('0'))
            total_value += position.quantity * current_price
        
        return total_value
    
    def get_total_pnl(self) -> Decimal:
        """计算总盈亏"""
        return self.get_portfolio_value() - self.initial_capital
    
    def get_positions_summary(self) -> List[dict]:
        """获取持仓摘要"""
        summary = []
        for symbol, position in self.positions.items():
            current_price = self.current_prices.get(symbol, Decimal('0'))
            summary.append({
                'symbol': symbol,
                'quantity': position.quantity,
                'average_cost': position.average_cost,
                'current_price': current_price,
                'market_value': position.quantity * current_price,
                'unrealized_pnl': position.unrealized_pnl(current_price),
                'realized_pnl': position.realized_pnl,
                'total_pnl': position.total_pnl(current_price)
            })
        return summary
    
    def get_account_summary(self) -> dict:
        """获取账户摘要"""
        return {
            'initial_capital': self.initial_capital,
            'cash': self.cash,
            'portfolio_value': self.get_portfolio_value(),
            'total_pnl': self.get_total_pnl(),
            'positions_count': len(self.positions),
            'active_orders_count': len(self.order_manager.get_active_orders()),
            'total_trades': len(self.order_manager.trades),
            'risk_metrics': self.risk_manager.get_risk_metrics()
        }
