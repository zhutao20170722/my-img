# 日内交易系统 (Day Trading System)

一个完整的Python日内交易系统，支持多策略回测、订单管理、风险控制、持仓跟踪、平台连接和Web界面。

## 功能特性 (Features)

### 核心功能
- ✅ **订单管理** - 支持市价单、限价单、止损单
- ✅ **持仓管理** - 实时持仓跟踪、盈亏计算
- ✅ **风险控制** - 多维度风控：持仓限制、订单限额、止损控制
- ✅ **策略引擎** - 可扩展的策略框架，支持多策略并行
- ✅ **增强回测** - 包含专业性能指标（夏普比率、最大回撤等）

### 平台集成 🆕
- ✅ **MetaTrader 5 (MT5)** - 支持MT5平台连接，获取实时行情和下单
- ✅ **Interactive Brokers (IB)** - 支持IB TWS/Gateway连接
- ✅ **模拟模式** - 无需安装平台包即可运行（自动降级为模拟模式）

### Web界面 🆕
- ✅ **实时Dashboard** - 账户概览、持仓监控
- ✅ **策略管理** - 在线添加和管理交易策略
- ✅ **回测分析** - 可视化回测结果和性能指标
- ✅ **平台连接** - 通过Web界面连接MT5/IB平台

### 内置交易策略
1. **动量策略 (Momentum Strategy)** - 基于均线交叉的趋势跟踪策略
2. **均值回归策略 (Mean Reversion Strategy)** - 基于布林带的反转策略

## 系统架构 (Architecture)

```
trading_system/
├── models.py              # 数据模型（订单、持仓、成交、行情）
├── strategies.py          # 交易策略
├── order_manager.py       # 订单管理器
├── risk_manager.py        # 风险管理器
├── trading_engine.py      # 交易引擎（核心）
├── backtesting.py         # 🆕 增强回测模块（性能指标分析）
└── connectors/            # 🆕 平台连接器
    ├── base_connector.py  # 连接器基类
    ├── mt5_connector.py   # MT5连接器
    └── ib_connector.py    # IB连接器

web/
├── app.py                 # 🆕 Flask Web服务器
├── templates/             # 🆕 HTML模板
└── static/                # 🆕 CSS/JS静态文件
```

## 快速开始 (Quick Start)

### 安装

```bash
# 克隆仓库
git clone https://github.com/zhutao20170722/my-img.git
cd my-img

# 核心功能仅依赖Python标准库，无需安装额外包
python --version  # 需要 Python 3.7+

# 可选：安装Web界面支持
pip install flask

# 可选：安装MT5支持（仅Windows）
# pip install MetaTrader5

# 可选：安装IB支持
# pip install ib_insync
```

### 运行示例

#### 基础回测示例
```bash
python example_momentum.py          # 动量策略示例
python example_mean_reversion.py    # 均值回归策略示例
python example_comprehensive.py     # 综合演示
```

#### 🆕 增强回测示例
```bash
python example_enhanced_backtest.py
```

输出示例：
```
================================================================================
           📊 增强回测结果报告
================================================================================

💰 基本指标 / Basic Metrics
--------------------------------------------------------------------------------
初始资金:    ¥     100,000.00
最终资金:    ¥     101,119.80
总盈亏:      ¥       1,119.80
总收益率:     📈           1.12%

📊 交易统计 / Trade Statistics
--------------------------------------------------------------------------------
总交易次数:                9
盈利交易:                  1
亏损交易:                  3
胜率:                 11.11%

🛡️ 风险指标 / Risk Metrics
--------------------------------------------------------------------------------
最大回撤:    ¥         757.78
最大回撤率:             0.75%
夏普比率:               -0.39
索提诺比率:             -0.28
```

#### 🆕 启动Web界面
```bash
# 启动Web服务器
python web/app.py

# 访问浏览器
# http://localhost:5000
```

Web界面功能：
- 📊 实时账户监控
- 🎯 在线策略管理
- 📈 回测结果可视化
- 🔌 MT5/IB平台连接

## 使用指南 (Usage Guide)

### 1. 创建交易引擎

```python
from decimal import Decimal
from trading_system import TradingEngine, RiskManager

# 创建风险管理器
risk_manager = RiskManager(
    max_position_size=1000,      # 单个持仓最大数量
    max_order_value=Decimal('100000'),  # 单笔订单最大金额
    max_daily_loss=Decimal('10000'),    # 单日最大亏损
    max_positions=10             # 最大持仓数量
)

# 创建交易引擎
engine = TradingEngine(
    initial_capital=Decimal('100000'),  # 初始资金
    risk_manager=risk_manager
)
```

### 2. 添加交易策略

```python
from trading_system import MomentumStrategy, MeanReversionStrategy

# 添加动量策略
momentum = MomentumStrategy(
    name="动量策略",
    short_period=5,    # 短期均线周期
    long_period=20,    # 长期均线周期
    quantity=100       # 每次交易数量
)
engine.add_strategy(momentum)

# 添加均值回归策略
mean_rev = MeanReversionStrategy(
    name="均值回归",
    period=20,         # 计算周期
    std_multiplier=2.0,  # 标准差倍数
    quantity=100
)
engine.add_strategy(mean_rev)
```

### 3. 启动引擎并处理行情

```python
from trading_system import MarketData
from datetime import datetime
from decimal import Decimal

# 启动引擎
engine.start()

# 处理市场数据
market_data = MarketData(
    symbol="AAPL",
    timestamp=datetime.now(),
    open=Decimal('150.0'),
    high=Decimal('152.0'),
    low=Decimal('149.0'),
    close=Decimal('151.5'),
    volume=1000000
)

engine.on_market_data(market_data)
```

### 4. 查看账户状态

```python
# 获取账户摘要
account = engine.get_account_summary()
print(f"组合价值: {account['portfolio_value']}")
print(f"总盈亏: {account['total_pnl']}")

# 获取持仓详情
positions = engine.get_positions_summary()
for pos in positions:
    print(f"{pos['symbol']}: {pos['quantity']} 股, 盈亏: {pos['total_pnl']}")
```

### 5. 🆕 使用平台连接器

#### 连接MT5平台
```python
from trading_system import MT5Connector

# 创建MT5连接器
mt5_config = {
    'account': '12345678',
    'password': 'your_password',
    'server': 'YourBroker-Server',
    # 'path': 'C:/Program Files/MetaTrader 5/terminal64.exe'  # 可选
}

connector = MT5Connector(mt5_config)

# 连接到MT5
if connector.connect():
    # 获取账户信息
    account_info = connector.get_account_info()
    print(f"账户余额: {account_info['balance']}")
    
    # 获取历史数据
    market_data = connector.get_market_data('EURUSD', timeframe='1h', count=100)
    
    # 获取当前持仓
    positions = connector.get_positions()
    
    # 断开连接
    connector.disconnect()
```

#### 连接Interactive Brokers
```python
from trading_system import IBConnector

# 创建IB连接器
ib_config = {
    'host': '127.0.0.1',
    'port': 7497,  # TWS paper trading port
    'client_id': 1
}

connector = IBConnector(ib_config)

# 连接到IB
if connector.connect():
    # 获取账户信息
    account_info = connector.get_account_info()
    
    # 获取历史数据
    market_data = connector.get_market_data('AAPL', timeframe='1h', count=100)
    
    connector.disconnect()
```

### 6. 🆕 使用增强回测功能

```python
from trading_system import TradingEngine, BacktestAnalyzer

# 创建引擎并启用权益跟踪
engine = TradingEngine(initial_capital=Decimal('100000'))
engine.enable_equity_tracking()

# 添加策略并运行回测
# ... 运行回测 ...

# 获取详细的回测结果
result = engine.get_backtest_result()

print(f"总收益率: {result.total_return:.2f}%")
print(f"夏普比率: {result.sharpe_ratio:.2f}")
print(f"最大回撤: {result.max_drawdown_percent:.2f}%")
print(f"盈利因子: {result.profit_factor:.2f}")
print(f"胜率: {result.win_rate:.2f}%")

# 导出结果到JSON
result.to_json('backtest_result.json')
```

### 7. 自定义策略

```python
from trading_system.strategies import BaseStrategy
from typing import List, Optional

class MyCustomStrategy(BaseStrategy):
    def __init__(self, name: str = "自定义策略"):
        super().__init__(name)
    
    def generate_signals(self, market_data: List[MarketData]) -> Optional[dict]:
        """实现你的策略逻辑"""
        if len(market_data) < 10:
            return None
        
        # 示例：价格突破策略
        current_price = market_data[-1].close
        highest = max(d.high for d in market_data[-10:])
        
        if current_price > highest:
            return {
                'side': OrderSide.BUY,
                'symbol': market_data[-1].symbol,
                'quantity': 100,
                'order_type': OrderType.MARKET,
                'price': None
            }
        
        return None
```

## 🆕 平台连接器 (Platform Connectors)

### MT5连接器特性
- ✅ 支持多种时间周期（1m, 5m, 15m, 30m, 1h, 4h, 1d）
- ✅ 实时市场数据订阅
- ✅ 下单、撤单、查询订单
- ✅ 获取账户信息和持仓
- ✅ 模拟模式（无需安装MT5包）

### IB连接器特性
- ✅ 支持股票和外汇交易
- ✅ 历史数据获取
- ✅ 实时行情订阅
- ✅ 订单管理（市价、限价、止损单）
- ✅ 账户和持仓查询
- ✅ 模拟模式（无需连接真实IB）

### 注意事项
- MT5连接器仅在Windows系统上可用
- 实盘交易需要安装相应的平台包（MetaTrader5或ib_insync）
- 未安装平台包时，连接器会自动运行在模拟模式
- 建议先在模拟模式下测试策略

## 🆕 增强回测指标 (Enhanced Backtesting Metrics)

### 基本指标
- **总收益率 (Total Return)** - 投资组合的总体表现
- **总盈亏 (Total P&L)** - 绝对盈亏金额

### 交易统计
- **总交易次数 (Total Trades)** - 执行的交易数量
- **胜率 (Win Rate)** - 盈利交易占比
- **盈利因子 (Profit Factor)** - 总盈利/总亏损的比率

### 风险指标
- **最大回撤 (Max Drawdown)** - 从峰值到谷值的最大跌幅
- **夏普比率 (Sharpe Ratio)** - 风险调整后的收益率
- **索提诺比率 (Sortino Ratio)** - 基于下行风险的收益率

### 数据导出
- 支持JSON格式导出完整回测结果
- 包含权益曲线和回撤曲线
- 包含所有交易记录

## 核心模块说明 (Core Modules)

### 数据模型 (models.py)

- **MarketData** - 市场行情数据（OHLCV）
- **Order** - 订单信息（订单类型、状态、价格等）
- **Trade** - 成交记录
- **Position** - 持仓信息（数量、成本、盈亏）

### 订单管理器 (order_manager.py)

- 订单创建、提交、取消
- 订单成交处理
- 订单历史查询
- 成交记录管理

### 风险管理器 (risk_manager.py)

- 持仓限制检查
- 订单金额限制
- 单日亏损控制
- 风控指标监控

### 交易引擎 (trading_engine.py)

- 市场数据处理
- 策略信号生成
- 订单执行
- 持仓更新
- 盈亏计算
- 🆕 权益跟踪（用于回测分析）

### 🆕 回测分析器 (backtesting.py)

- 计算专业回测指标
- 生成权益曲线和回撤曲线
- 计算夏普比率和索提诺比率
- 导出回测结果为JSON

### 🆕 平台连接器 (connectors/)

- **BaseConnector** - 连接器基类，定义标准接口
- **MT5Connector** - MetaTrader 5平台连接器
- **IBConnector** - Interactive Brokers平台连接器

## 风险控制 (Risk Management)

系统提供多层次风险控制：

1. **持仓限制** - 限制单个标的持仓数量
2. **订单限额** - 限制单笔订单金额
3. **亏损控制** - 限制单日最大亏损
4. **持仓数量** - 限制同时持有的标的数量

所有订单在提交前都会经过风控检查，不符合风控要求的订单将被拒绝。

## 注意事项 (Important Notes)

⚠️ **这是一个教学/演示系统，已支持平台连接但建议先在模拟模式下测试**

### 模拟模式特点
- 订单成交采用简化模拟逻辑
- 未考虑滑点、手续费等实际交易成本
- 平台连接器在未安装相应包时自动降级为模拟模式

### 实盘交易准备
如需用于实盘，需要：
1. ✅ **已支持** - MT5/IB平台连接（需安装对应包）
2. ✅ **已支持** - 真实行情数据获取
3. ❌ 添加滑点、手续费计算
4. ❌ 完善异常处理和日志系统
5. ❌ 添加实时监控和告警

### 安全建议
- 先在模拟账户上测试策略
- 设置合理的风险限制参数
- 小规模资金开始实盘测试
- 定期监控和调整策略

## 系统特点 (Highlights)

- 📊 **清晰的架构** - 模块化设计，职责分明
- 🔧 **易于扩展** - 支持自定义策略、风控规则
- 💰 **精确计算** - 使用Decimal类型确保金额计算精度
- 🛡️ **风控完善** - 多维度风险控制
- 🐍 **纯Python核心** - 核心功能仅使用标准库，可选依赖灵活
- 🔌 **平台集成** - 支持MT5和IB平台连接
- 📈 **专业回测** - 包含夏普比率、最大回撤等专业指标
- 🌐 **Web界面** - 实时监控和在线管理

## 开发计划 (Roadmap)

### 已完成 ✅
- [x] 核心交易引擎
- [x] 订单和持仓管理
- [x] 多维度风险控制
- [x] MT5平台集成
- [x] Interactive Brokers集成
- [x] 增强回测功能（夏普比率、最大回撤等）
- [x] Web界面展示
- [x] 回测结果可视化和导出

### 计划中 🚧
- [ ] 添加更多内置策略（网格交易、配对交易等）
- [ ] 支持更多平台（如CTP、VNPY等）
- [ ] 实时行情推送和WebSocket支持
- [ ] 支持多账户管理
- [ ] 添加机器学习策略支持
- [ ] 回测性能优化（向量化计算）
- [ ] 数据库持久化
- [ ] 移动端应用

## 许可证 (License)

MIT License

## 贡献 (Contributing)

欢迎提交Issue和Pull Request！

---

**免责声明**: 本系统仅供学习和研究使用，不构成任何投资建议。使用本系统进行交易的风险由使用者自行承担。
