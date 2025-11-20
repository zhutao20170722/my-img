"""
示例：动量策略回测
Momentum Strategy Backtesting Example
"""

from datetime import datetime, timedelta
from decimal import Decimal
import random

from trading_system import (
    TradingEngine,
    MomentumStrategy,
    MarketData,
    RiskManager
)


def generate_sample_data(symbol: str, days: int = 30, bars_per_day: int = 10) -> list:
    """
    生成示例市场数据
    
    Args:
        symbol: 股票代码
        days: 天数
        bars_per_day: 每天的K线数量
        
    Returns:
        市场数据列表
    """
    data = []
    base_price = Decimal('100.0')
    current_time = datetime.now() - timedelta(days=days)
    
    for day in range(days):
        for bar in range(bars_per_day):
            # 模拟价格波动
            change = Decimal(str(random.uniform(-2, 2)))
            base_price = max(Decimal('50.0'), base_price + change)
            
            # 生成OHLC数据
            open_price = base_price
            high_price = open_price + Decimal(str(random.uniform(0, 3)))
            low_price = open_price - Decimal(str(random.uniform(0, 3)))
            close_price = Decimal(str(random.uniform(float(low_price), float(high_price))))
            
            market_data = MarketData(
                symbol=symbol,
                timestamp=current_time,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=random.randint(10000, 100000)
            )
            
            data.append(market_data)
            current_time += timedelta(minutes=30)
    
    return data


def main():
    """主函数"""
    print("=" * 60)
    print("日内交易系统 - 动量策略示例")
    print("Day Trading System - Momentum Strategy Example")
    print("=" * 60)
    print()
    
    # 创建交易引擎
    initial_capital = Decimal('100000')
    risk_manager = RiskManager(
        max_position_size=500,
        max_order_value=Decimal('50000'),
        max_daily_loss=Decimal('5000')
    )
    
    engine = TradingEngine(
        initial_capital=initial_capital,
        risk_manager=risk_manager
    )
    
    # 添加动量策略
    momentum_strategy = MomentumStrategy(
        name="动量策略",
        short_period=5,
        long_period=20,
        quantity=100
    )
    engine.add_strategy(momentum_strategy)
    
    # 启动引擎
    engine.start()
    
    # 生成示例数据并回测
    print("生成示例市场数据...")
    market_data = generate_sample_data("AAPL", days=30, bars_per_day=10)
    print(f"生成 {len(market_data)} 条市场数据")
    print()
    
    print("开始回测...")
    for i, data in enumerate(market_data):
        engine.on_market_data(data)
        
        # 每50条数据打印一次进度
        if (i + 1) % 50 == 0:
            print(f"处理进度: {i + 1}/{len(market_data)}")
    
    print("回测完成")
    print()
    
    # 停止引擎
    engine.stop()
    
    # 打印结果
    print("=" * 60)
    print("回测结果")
    print("=" * 60)
    
    account = engine.get_account_summary()
    print(f"初始资金: ¥{account['initial_capital']:,.2f}")
    print(f"现金余额: ¥{account['cash']:,.2f}")
    print(f"组合价值: ¥{account['portfolio_value']:,.2f}")
    print(f"总盈亏: ¥{account['total_pnl']:,.2f}")
    print(f"收益率: {(account['total_pnl'] / account['initial_capital'] * 100):.2f}%")
    print()
    
    print(f"持仓数量: {account['positions_count']}")
    print(f"总交易次数: {account['total_trades']}")
    print()
    
    # 打印持仓详情
    if engine.positions:
        print("当前持仓:")
        positions = engine.get_positions_summary()
        for pos in positions:
            print(f"  {pos['symbol']}: {pos['quantity']} 股")
            print(f"    成本: ¥{pos['average_cost']:.2f}")
            print(f"    现价: ¥{pos['current_price']:.2f}")
            print(f"    市值: ¥{pos['market_value']:,.2f}")
            print(f"    盈亏: ¥{pos['total_pnl']:,.2f}")
    else:
        print("当前无持仓")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
