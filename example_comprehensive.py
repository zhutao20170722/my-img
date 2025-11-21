"""
综合示例：多策略日内交易系统演示
Comprehensive Example: Multi-Strategy Day Trading System Demo
"""

from datetime import datetime, timedelta
from decimal import Decimal
import random

from trading_system import (
    TradingEngine,
    MomentumStrategy,
    MeanReversionStrategy,
    MarketData,
    RiskManager
)


def generate_complex_market_data(symbol: str, bars: int = 300) -> list:
    """
    生成复杂的市场数据（包含趋势和振荡）
    
    Args:
        symbol: 股票代码
        bars: K线数量
        
    Returns:
        市场数据列表
    """
    data = []
    base_price = Decimal('100.0')
    current_time = datetime.now() - timedelta(days=bars//10)
    
    # 添加趋势成分
    trend = 0
    
    for i in range(bars):
        # 每50根K线改变趋势
        if i % 50 == 0:
            trend = random.choice([-1, 0, 1])
        
        # 价格变化 = 趋势 + 随机波动
        trend_change = Decimal(str(trend * 0.5))
        noise = Decimal(str(random.uniform(-2, 2)))
        base_price = max(Decimal('50.0'), min(Decimal('150.0'), base_price + trend_change + noise))
        
        # 生成OHLC数据
        open_price = base_price
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


def print_separator():
    """打印分隔线"""
    print("=" * 70)


def main():
    """主函数"""
    print_separator()
    print("           日内交易系统 - 综合演示")
    print("     Day Trading System - Comprehensive Demo")
    print_separator()
    print()
    
    # 1. 创建风险管理器
    print("📊 步骤 1: 初始化风险管理器")
    print("-" * 70)
    risk_manager = RiskManager(
        max_position_size=500,
        max_order_value=Decimal('50000'),
        max_daily_loss=Decimal('5000'),
        max_positions=3
    )
    print("✅ 风控参数设置:")
    print(f"   - 最大持仓: 500 股")
    print(f"   - 最大订单金额: ¥50,000")
    print(f"   - 最大日亏损: ¥5,000")
    print(f"   - 最大持仓数: 3 个")
    print()
    
    # 2. 创建交易引擎
    print("🚀 步骤 2: 创建交易引擎")
    print("-" * 70)
    initial_capital = Decimal('100000')
    engine = TradingEngine(
        initial_capital=initial_capital,
        risk_manager=risk_manager
    )
    print(f"✅ 初始资金: ¥{initial_capital:,.2f}")
    print()
    
    # 3. 添加多个策略
    print("🎯 步骤 3: 添加交易策略")
    print("-" * 70)
    
    # 动量策略
    momentum = MomentumStrategy(
        name="动量策略",
        short_period=5,
        long_period=20,
        quantity=100
    )
    engine.add_strategy(momentum)
    print("✅ 已添加: 动量策略 (短期=5, 长期=20)")
    
    # 均值回归策略
    mean_reversion = MeanReversionStrategy(
        name="均值回归策略",
        period=20,
        std_multiplier=2.0,
        quantity=50
    )
    engine.add_strategy(mean_reversion)
    print("✅ 已添加: 均值回归策略 (周期=20, 标准差倍数=2.0)")
    print()
    
    # 4. 生成市场数据
    print("📈 步骤 4: 生成市场数据")
    print("-" * 70)
    symbols = ["AAPL", "TSLA", "GOOGL"]
    all_market_data = {}
    
    for symbol in symbols:
        data = generate_complex_market_data(symbol, bars=100)
        all_market_data[symbol] = data
        print(f"✅ {symbol}: 生成 {len(data)} 条K线数据")
    print()
    
    # 5. 启动引擎并回测
    print("⚡ 步骤 5: 启动引擎并开始回测")
    print("-" * 70)
    engine.start()
    print("✅ 交易引擎已启动")
    print()
    
    # 模拟实时行情推送
    total_bars = len(all_market_data[symbols[0]])
    for i in range(total_bars):
        for symbol in symbols:
            if i < len(all_market_data[symbol]):
                engine.on_market_data(all_market_data[symbol][i])
        
        # 每20根K线打印一次进度
        if (i + 1) % 20 == 0:
            progress = (i + 1) / total_bars * 100
            print(f"⏳ 回测进度: {i + 1}/{total_bars} ({progress:.1f}%)")
    
    print("✅ 回测完成")
    print()
    
    # 6. 停止引擎
    engine.stop()
    
    # 7. 展示结果
    print_separator()
    print("           📊 回测结果报告")
    print_separator()
    print()
    
    # 账户摘要
    account = engine.get_account_summary()
    print("💰 账户概览")
    print("-" * 70)
    print(f"初始资金:    ¥{account['initial_capital']:>15,.2f}")
    print(f"现金余额:    ¥{account['cash']:>15,.2f}")
    print(f"持仓市值:    ¥{(account['portfolio_value'] - account['cash']):>15,.2f}")
    print(f"组合总值:    ¥{account['portfolio_value']:>15,.2f}")
    print(f"总盈亏:      ¥{account['total_pnl']:>15,.2f}")
    
    roi = (account['total_pnl'] / account['initial_capital'] * 100)
    roi_symbol = "📈" if roi >= 0 else "📉"
    print(f"收益率:       {roi_symbol} {roi:>14.2f}%")
    print()
    
    # 交易统计
    print("📊 交易统计")
    print("-" * 70)
    print(f"持仓数量:    {account['positions_count']:>15} 个")
    print(f"活跃订单:    {account['active_orders_count']:>15} 笔")
    print(f"总成交:      {account['total_trades']:>15} 笔")
    print()
    
    # 持仓详情
    positions = engine.get_positions_summary()
    if positions:
        print("📋 当前持仓明细")
        print("-" * 70)
        print(f"{'股票':^10} {'数量':^8} {'成本':^12} {'现价':^12} {'盈亏':^15}")
        print("-" * 70)
        
        for pos in positions:
            pnl_symbol = "🟢" if pos['total_pnl'] >= 0 else "🔴"
            print(f"{pos['symbol']:^10} {pos['quantity']:^8} "
                  f"¥{pos['average_cost']:>10.2f} "
                  f"¥{pos['current_price']:>10.2f} "
                  f"{pnl_symbol} ¥{pos['total_pnl']:>10.2f}")
        print()
    else:
        print("📋 当前持仓: 空仓")
        print()
    
    # 风控指标
    risk_metrics = account['risk_metrics']
    print("🛡️ 风控指标")
    print("-" * 70)
    print(f"当日盈亏:    ¥{risk_metrics['daily_pnl']:>15,.2f}")
    print(f"剩余止损额度: ¥{risk_metrics['daily_loss_remaining']:>15,.2f}")
    print()
    
    # 交易记录摘要
    trades = engine.order_manager.get_trades()
    if trades:
        print("📜 成交记录 (最近5笔)")
        print("-" * 70)
        print(f"{'股票':^10} {'方向':^6} {'数量':^8} {'价格':^12} {'金额':^15}")
        print("-" * 70)
        
        for trade in trades[-5:]:
            side_text = "买入" if trade.side.value == "buy" else "卖出"
            side_symbol = "🟢" if trade.side.value == "buy" else "🔴"
            print(f"{trade.symbol:^10} {side_symbol}{side_text:^4} "
                  f"{trade.quantity:^8} "
                  f"¥{trade.price:>10.2f} "
                  f"¥{trade.value:>13,.2f}")
        print()
    
    # 结论
    print_separator()
    if account['total_pnl'] > 0:
        print("🎉 回测结果: 盈利 - 策略表现良好!")
    elif account['total_pnl'] < 0:
        print("⚠️  回测结果: 亏损 - 需要优化策略参数")
    else:
        print("➡️  回测结果: 持平 - 策略需要进一步调整")
    print_separator()
    print()
    
    print("💡 提示:")
    print("   1. 这是基于模拟数据的回测结果")
    print("   2. 实盘交易需要考虑滑点、手续费等因素")
    print("   3. 建议在使用前进行充分的历史数据回测")
    print("   4. 风险管理至关重要，请谨慎设置参数")
    print()
    print_separator()


if __name__ == "__main__":
    main()
