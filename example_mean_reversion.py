"""
示例：均值回归策略回测
Mean Reversion Strategy Backtesting Example
"""

from datetime import datetime, timedelta
from decimal import Decimal
import random

from trading_system import (
    TradingEngine,
    MeanReversionStrategy,
    MarketData,
    RiskManager
)


def generate_oscillating_data(symbol: str, bars: int = 200) -> list:
    """
    生成振荡型市场数据（适合均值回归策略）
    
    Args:
        symbol: 股票代码
        bars: K线数量
        
    Returns:
        市场数据列表
    """
    data = []
    base_price = Decimal('100.0')
    current_time = datetime.now() - timedelta(days=bars//10)
    
    for i in range(bars):
        # 生成围绕均值振荡的价格
        oscillation = Decimal(str(10 * random.uniform(-1, 1) * (1 + 0.5 * random.random())))
        noise = Decimal(str(random.uniform(-1, 1)))
        price = base_price + oscillation + noise
        
        # 确保价格在合理范围内
        price = max(Decimal('80.0'), min(Decimal('120.0'), price))
        
        # 生成OHLC数据
        open_price = price
        high_price = open_price + Decimal(str(abs(random.uniform(0, 2))))
        low_price = open_price - Decimal(str(abs(random.uniform(0, 2))))
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
        current_time += timedelta(minutes=15)
    
    return data


def main():
    """主函数"""
    print("=" * 60)
    print("日内交易系统 - 均值回归策略示例")
    print("Day Trading System - Mean Reversion Strategy Example")
    print("=" * 60)
    print()
    
    # 创建交易引擎
    initial_capital = Decimal('100000')
    risk_manager = RiskManager(
        max_position_size=300,
        max_order_value=Decimal('30000'),
        max_daily_loss=Decimal('3000')
    )
    
    engine = TradingEngine(
        initial_capital=initial_capital,
        risk_manager=risk_manager
    )
    
    # 添加均值回归策略
    mean_reversion = MeanReversionStrategy(
        name="均值回归策略",
        period=20,
        std_multiplier=2.0,
        quantity=100
    )
    engine.add_strategy(mean_reversion)
    
    # 启动引擎
    engine.start()
    
    # 生成示例数据并回测
    print("生成示例市场数据（振荡型）...")
    market_data = generate_oscillating_data("TSLA", bars=200)
    print(f"生成 {len(market_data)} 条市场数据")
    print()
    
    print("开始回测...")
    for i, data in enumerate(market_data):
        engine.on_market_data(data)
        
        # 每40条数据打印一次进度
        if (i + 1) % 40 == 0:
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
    
    # 打印风控指标
    risk_metrics = account['risk_metrics']
    print("风控指标:")
    print(f"  当日盈亏: ¥{risk_metrics['daily_pnl']:,.2f}")
    print(f"  剩余可亏损额度: ¥{risk_metrics['daily_loss_remaining']:,.2f}")
    print()
    
    # 打印持仓详情
    if engine.positions:
        print("当前持仓:")
        positions = engine.get_positions_summary()
        for pos in positions:
            print(f"  {pos['symbol']}: {pos['quantity']} 股")
            print(f"    成本: ¥{pos['average_cost']:.2f}")
            print(f"    现价: ¥{pos['current_price']:.2f}")
            print(f"    未实现盈亏: ¥{pos['unrealized_pnl']:,.2f}")
            print(f"    已实现盈亏: ¥{pos['realized_pnl']:,.2f}")
    else:
        print("当前无持仓")
    
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
