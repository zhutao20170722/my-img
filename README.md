# 日内交易系统 (Day Trading System)

一个完整的Python日内交易系统，支持多策略回测、订单管理、风险控制和持仓跟踪。

## 功能特性 (Features)

### 核心功能
- ✅ **订单管理** - 支持市价单、限价单、止损单
- ✅ **持仓管理** - 实时持仓跟踪、盈亏计算
- ✅ **风险控制** - 多维度风控：持仓限制、订单限额、止损控制
- ✅ **策略引擎** - 可扩展的策略框架，支持多策略并行
- ✅ **回测功能** - 基于历史数据的策略回测

### 内置交易策略
1. **动量策略 (Momentum Strategy)** - 基于均线交叉的趋势跟踪策略
2. **均值回归策略 (Mean Reversion Strategy)** - 基于布林带的反转策略

## 系统架构 (Architecture)

```
trading_system/
├── models.py           # 数据模型（订单、持仓、成交、行情）
├── strategies.py       # 交易策略
├── order_manager.py    # 订单管理器
├── risk_manager.py     # 风险管理器
└── trading_engine.py   # 交易引擎（核心）
```

## 快速开始 (Quick Start)

### 安装
```bash
# 克隆仓库
git clone https://github.com/zhutao20170722/my-img.git
cd my-img

# 本系统仅依赖Python标准库，无需安装额外包
python --version  # 需要 Python 3.7+
```

### 运行示例

#### 动量策略示例
```bash
python example_momentum.py
```

输出示例：
```
============================================================
日内交易系统 - 动量策略示例
Day Trading System - Momentum Strategy Example
============================================================

生成示例市场数据...
生成 300 条市场数据

开始回测...
处理进度: 50/300
处理进度: 100/300
...
回测完成

============================================================
回测结果
============================================================
初始资金: ¥100,000.00
现金余额: ¥95,234.56
组合价值: ¥102,345.67
总盈亏: ¥2,345.67
收益率: 2.35%

持仓数量: 1
总交易次数: 8
...
```

#### 均值回归策略示例
```bash
python example_mean_reversion.py
```

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

### 5. 自定义策略

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

## 风险控制 (Risk Management)

系统提供多层次风险控制：

1. **持仓限制** - 限制单个标的持仓数量
2. **订单限额** - 限制单笔订单金额
3. **亏损控制** - 限制单日最大亏损
4. **持仓数量** - 限制同时持有的标的数量

所有订单在提交前都会经过风控检查，不符合风控要求的订单将被拒绝。

## 注意事项 (Important Notes)

⚠️ **这是一个教学/演示系统，不建议直接用于实盘交易**

- 订单成交采用简化模拟逻辑
- 未考虑滑点、手续费等实际交易成本
- 未实现实际的交易所连接
- 市场数据为模拟生成

如需用于实盘，需要：
1. 接入真实的行情数据源
2. 接入真实的交易接口（如证券公司API）
3. 添加滑点、手续费计算
4. 完善异常处理和日志系统
5. 添加实时监控和告警

## 系统特点 (Highlights)

- 📊 **清晰的架构** - 模块化设计，职责分明
- 🔧 **易于扩展** - 支持自定义策略、风控规则
- 💰 **精确计算** - 使用Decimal类型确保金额计算精度
- 🛡️ **风控完善** - 多维度风险控制
- 🐍 **纯Python** - 仅使用标准库，无外部依赖

## 开发计划 (Roadmap)

- [ ] 添加更多内置策略（网格交易、配对交易等）
- [ ] 支持实时行情数据接入
- [ ] 添加性能分析模块（夏普比率、最大回撤等）
- [ ] 支持多账户管理
- [ ] Web界面展示
- [ ] 添加回测结果可视化

## 许可证 (License)

MIT License

## 贡献 (Contributing)

欢迎提交Issue和Pull Request！

---

**免责声明**: 本系统仅供学习和研究使用，不构成任何投资建议。使用本系统进行交易的风险由使用者自行承担。
