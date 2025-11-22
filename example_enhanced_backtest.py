"""
示例：使用MT5连接器和增强的回测功能
Example: Using MT5 connector with enhanced backtesting features
"""

from datetime import datetime, timedelta
from decimal import Decimal
import random

from trading_system import (
    TradingEngine,
    MomentumStrategy,
    RiskManager,
    MarketData,
    MT5Connector,
    BacktestAnalyzer
)


def generate_market_data(symbol: str, bars: int = 200) -> list:
    """生成模拟市场数据"""
    data = []
    base_price = Decimal('100.0')
    current_time = datetime.now() - timedelta(days=bars//10)
    
    for i in range(bars):
        change = Decimal(str(random.uniform(-2, 2)))
        base_price = max(Decimal('80.0'), min(Decimal('120.0'), base_price + change))
        
        open_price = base_price
        high_price = open_price + Decimal(str(abs(random.uniform(0, 1.5))))
        low_price = open_price - Decimal(str(abs(random.uniform(0, 1.5))))
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
    print("=" * 80)


def main():
    print_separator()
    print("           MT5连接器 & 增强回测功能演示")
    print("     MT5 Connector & Enhanced Backtesting Demo")
    print_separator()
    print()
    
    # 1. 测试MT5连接器（模拟模式）
    print("📡 步骤 1: 测试MT5连接器")
    print("-" * 80)
    
    mt5_config = {
        'account': '12345678',
        'password': 'password',
        'server': 'Demo-Server',
    }
    
    connector = MT5Connector(mt5_config)
    
    if connector.connect():
        print("✅ MT5连接成功 (模拟模式)")
        
        # 获取账户信息
        account_info = connector.get_account_info()
        print(f"   账户余额: ¥{account_info.get('balance', 0):,.2f}")
        print(f"   净值: ¥{account_info.get('equity', 0):,.2f}")
        
        connector.disconnect()
        print("✅ MT5断开连接")
    else:
        print("❌ MT5连接失败")
    
    print()
    
    # 2. 创建交易引擎并启用权益跟踪
    print("🚀 步骤 2: 创建交易引擎并启用回测跟踪")
    print("-" * 80)
    
    risk_manager = RiskManager(
        max_position_size=500,
        max_order_value=Decimal('50000'),
        max_daily_loss=Decimal('5000'),
        max_positions=3
    )
    
    engine = TradingEngine(
        initial_capital=Decimal('100000'),
        risk_manager=risk_manager
    )
    
    # 启用权益跟踪
    engine.enable_equity_tracking()
    print("✅ 已启用权益跟踪")
    
    # 添加策略
    strategy = MomentumStrategy(
        name="动量策略",
        short_period=5,
        long_period=20,
        quantity=100
    )
    engine.add_strategy(strategy)
    print("✅ 已添加动量策略")
    print()
    
    # 3. 生成市场数据并回测
    print("📈 步骤 3: 生成市场数据并运行回测")
    print("-" * 80)
    
    market_data = generate_market_data("AAPL", bars=200)
    print(f"✅ 生成 {len(market_data)} 条市场数据")
    
    engine.start()
    print("✅ 引擎已启动")
    print()
    
    # 运行回测
    for i, data in enumerate(market_data):
        engine.on_market_data(data)
        
        if (i + 1) % 40 == 0:
            progress = (i + 1) / len(market_data) * 100
            print(f"⏳ 回测进度: {i + 1}/{len(market_data)} ({progress:.1f}%)")
    
    engine.stop()
    print("✅ 回测完成")
    print()
    
    # 4. 获取并显示增强的回测结果
    print_separator()
    print("           📊 增强回测结果报告")
    print_separator()
    print()
    
    result = engine.get_backtest_result()
    
    # 基本指标
    print("💰 基本指标 / Basic Metrics")
    print("-" * 80)
    print(f"初始资金:    ¥{result.initial_capital:>15,.2f}")
    print(f"最终资金:    ¥{result.final_capital:>15,.2f}")
    print(f"总盈亏:      ¥{result.total_pnl:>15,.2f}")
    
    roi_symbol = "📈" if result.total_return >= 0 else "📉"
    print(f"总收益率:     {roi_symbol} {result.total_return:>14.2f}%")
    print()
    
    # 交易统计
    print("📊 交易统计 / Trade Statistics")
    print("-" * 80)
    print(f"总交易次数:  {result.total_trades:>15}")
    print(f"盈利交易:    {result.winning_trades:>15}")
    print(f"亏损交易:    {result.losing_trades:>15}")
    print(f"胜率:        {result.win_rate:>14.2f}%")
    print()
    
    # 盈亏分析
    print("💵 盈亏分析 / Profit Analysis")
    print("-" * 80)
    print(f"总盈利:      ¥{result.gross_profit:>15,.2f}")
    print(f"总亏损:      ¥{result.gross_loss:>15,.2f}")
    print(f"盈利因子:    {result.profit_factor:>16.2f}")
    print(f"平均盈利:    ¥{result.average_win:>15,.2f}")
    print(f"平均亏损:    ¥{result.average_loss:>15,.2f}")
    print()
    
    # 风险指标
    print("🛡️ 风险指标 / Risk Metrics")
    print("-" * 80)
    print(f"最大回撤:    ¥{result.max_drawdown:>15,.2f}")
    print(f"最大回撤率:  {result.max_drawdown_percent:>15.2f}%")
    print(f"夏普比率:    {result.sharpe_ratio:>16.2f}")
    print(f"索提诺比率:  {result.sortino_ratio:>16.2f}")
    print()
    
    # 时间指标
    if result.start_date and result.end_date:
        print("📅 时间指标 / Time Metrics")
        print("-" * 80)
        print(f"开始日期:    {result.start_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"结束日期:    {result.end_date.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"回测天数:    {result.duration_days} 天")
        print()
    
    # 5. 导出结果到JSON
    print("💾 步骤 5: 导出回测结果")
    print("-" * 80)
    
    output_file = "/tmp/backtest_result.json"
    result.to_json(output_file)
    print(f"✅ 回测结果已保存到: {output_file}")
    print()
    
    # 结论
    print_separator()
    if result.total_return > 0 and result.sharpe_ratio > 1.0:
        print("🎉 回测结果优秀: 盈利 + 高夏普比率!")
    elif result.total_return > 0:
        print("✅ 回测结果良好: 盈利，但需要优化风险指标")
    else:
        print("⚠️  回测结果需改进: 需要调整策略参数")
    print_separator()
    print()
    
    print("💡 新功能说明:")
    print("   1. MT5/IB连接器 - 支持实盘交易平台连接")
    print("   2. 增强回测 - 包含夏普比率、最大回撤等专业指标")
    print("   3. 性能分析 - 详细的交易统计和盈亏分析")
    print("   4. 结果导出 - 支持JSON格式导出")
    print()
    print("💻 Web界面使用:")
    print("   运行: python web/app.py")
    print("   访问: http://localhost:5000")
    print()
    print_separator()


if __name__ == "__main__":
    main()
