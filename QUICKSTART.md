# 快速开始指南 (Quick Start Guide)

## 30秒快速体验 (30-Second Quick Demo)

```bash
# 运行综合示例
python example_comprehensive.py

# 运行动量策略示例
python example_momentum.py

# 运行均值回归策略示例
python example_mean_reversion.py
```

## 5分钟入门教程 (5-Minute Tutorial)

### 1. 创建一个简单的交易系统

```python
from decimal import Decimal
from trading_system import TradingEngine, MomentumStrategy

# 创建交易引擎（初始资金10万）
engine = TradingEngine(initial_capital=Decimal('100000'))

# 添加动量策略
strategy = MomentumStrategy(quantity=100)
engine.add_strategy(strategy)

# 启动引擎
engine.start()
```

### 2. 喂入市场数据

```python
from datetime import datetime
from trading_system import MarketData

# 创建市场数据
data = MarketData(
    symbol="AAPL",
    timestamp=datetime.now(),
    open=Decimal('150.0'),
    high=Decimal('152.0'),
    low=Decimal('149.0'),
    close=Decimal('151.0'),
    volume=1000000
)

# 处理数据（策略会自动生成交易信号）
engine.on_market_data(data)
```

### 3. 查看结果

```python
# 查看账户摘要
account = engine.get_account_summary()
print(f"组合价值: ¥{account['portfolio_value']:,.2f}")
print(f"盈亏: ¥{account['total_pnl']:,.2f}")

# 查看持仓
for pos in engine.get_positions_summary():
    print(f"{pos['symbol']}: {pos['quantity']} 股, 盈亏 ¥{pos['total_pnl']:,.2f}")
```

## 核心概念 (Core Concepts)

### 订单类型
- **市价单 (MARKET)** - 按当前市场价格立即成交
- **限价单 (LIMIT)** - 只在价格达到指定值时成交
- **止损单 (STOP)** - 价格触及止损点时触发

### 策略类型
- **动量策略** - 跟随趋势，均线金叉买入，死叉卖出
- **均值回归** - 逆趋势，价格偏离均值时建仓

### 风控维度
- **持仓限制** - 控制单个标的持仓数量
- **订单限额** - 控制单笔订单金额
- **亏损控制** - 控制单日最大亏损
- **持仓数量** - 控制同时持有的标的数量

## 自定义策略模板 (Custom Strategy Template)

```python
from trading_system.strategies import BaseStrategy
from trading_system.models import OrderSide, OrderType
from typing import List, Optional

class MyStrategy(BaseStrategy):
    def __init__(self, name="我的策略"):
        super().__init__(name)
        # 初始化参数
        
    def generate_signals(self, market_data: List[MarketData]) -> Optional[dict]:
        # 实现你的策略逻辑
        
        # 示例：价格上涨超过5%时买入
        if len(market_data) < 2:
            return None
            
        prev_close = market_data[-2].close
        curr_close = market_data[-1].close
        
        if curr_close > prev_close * Decimal('1.05'):
            return {
                'side': OrderSide.BUY,
                'symbol': market_data[-1].symbol,
                'quantity': 100,
                'order_type': OrderType.MARKET,
                'price': None
            }
        
        return None
```

## 运行测试 (Run Tests)

```bash
# 运行所有单元测试
python -m unittest discover tests -v

# 运行特定测试
python -m unittest tests.test_models -v
```

## 项目结构 (Project Structure)

```
my-img/
├── trading_system/          # 核心交易系统
│   ├── __init__.py
│   ├── models.py           # 数据模型
│   ├── strategies.py       # 交易策略
│   ├── order_manager.py    # 订单管理
│   ├── risk_manager.py     # 风险管理
│   └── trading_engine.py   # 交易引擎
├── tests/                   # 单元测试
│   ├── test_models.py
│   ├── test_order_manager.py
│   └── test_risk_manager.py
├── example_momentum.py      # 动量策略示例
├── example_mean_reversion.py # 均值回归示例
├── example_comprehensive.py  # 综合示例
├── requirements.txt         # 依赖（无需外部库）
└── README.md               # 完整文档
```

## 常见问题 (FAQ)

**Q: 需要安装哪些依赖？**  
A: 无需任何外部依赖，只使用Python标准库。

**Q: 如何添加多个策略？**  
A: 使用 `engine.add_strategy()` 可以添加多个策略，它们会并行工作。

**Q: 如何调整风控参数？**  
A: 创建 `RiskManager` 时传入参数，或使用 `set_position_limit()` 等方法。

**Q: 支持实盘交易吗？**  
A: 当前版本仅供学习和回测，需要接入实际交易接口才能实盘。

**Q: 如何获取订单历史？**  
A: 使用 `engine.order_manager.get_order_history()` 获取所有订单。

## 下一步 (Next Steps)

1. 阅读完整 [README.md](README.md) 了解详细功能
2. 运行三个示例程序体验系统功能
3. 查看单元测试了解各模块的详细用法
4. 尝试编写自己的交易策略
5. 使用真实历史数据进行回测

## 获取帮助 (Get Help)

- 查看源代码注释（中英双语）
- 运行示例程序查看输出
- 阅读单元测试了解API用法
- 提交 Issue 报告问题或建议

---

Happy Trading! 祝交易愉快！ 🚀📈
