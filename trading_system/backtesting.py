"""
Enhanced backtesting module with performance metrics
增强的回测模块，包含性能指标
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from decimal import Decimal
import json


@dataclass
class BacktestResult:
    """
    Backtest result with performance metrics
    回测结果及性能指标
    """
    # Basic metrics
    initial_capital: Decimal
    final_capital: Decimal
    total_pnl: Decimal
    total_return: Decimal  # Percentage
    
    # Trade statistics
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    win_rate: Decimal = Decimal('0')
    
    # Profit metrics
    gross_profit: Decimal = Decimal('0')
    gross_loss: Decimal = Decimal('0')
    profit_factor: Decimal = Decimal('0')
    average_win: Decimal = Decimal('0')
    average_loss: Decimal = Decimal('0')
    
    # Risk metrics
    max_drawdown: Decimal = Decimal('0')
    max_drawdown_percent: Decimal = Decimal('0')
    sharpe_ratio: Decimal = Decimal('0')
    sortino_ratio: Decimal = Decimal('0')
    
    # Time metrics
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    duration_days: int = 0
    
    # Equity curve
    equity_curve: List[Dict[str, Any]] = field(default_factory=list)
    
    # Drawdown curve
    drawdown_curve: List[Dict[str, Any]] = field(default_factory=list)
    
    # Trade history
    trades: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        # Convert equity curve timestamps to ISO format
        equity_curve_json = []
        for point in self.equity_curve:
            equity_curve_json.append({
                'timestamp': point['timestamp'].isoformat() if isinstance(point['timestamp'], datetime) else str(point['timestamp']),
                'value': point['value']
            })
        
        # Convert drawdown curve timestamps to ISO format
        drawdown_curve_json = []
        for point in self.drawdown_curve:
            drawdown_curve_json.append({
                'timestamp': point['timestamp'].isoformat() if isinstance(point['timestamp'], datetime) else str(point['timestamp']),
                'drawdown': point['drawdown'],
                'drawdown_percent': point['drawdown_percent']
            })
        
        # Convert trade timestamps to ISO format
        trades_json = []
        for trade in self.trades:
            trade_copy = trade.copy()
            if 'timestamp' in trade_copy and isinstance(trade_copy['timestamp'], datetime):
                trade_copy['timestamp'] = trade_copy['timestamp'].isoformat()
            trades_json.append(trade_copy)
        
        return {
            'initial_capital': float(self.initial_capital),
            'final_capital': float(self.final_capital),
            'total_pnl': float(self.total_pnl),
            'total_return': float(self.total_return),
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': float(self.win_rate),
            'gross_profit': float(self.gross_profit),
            'gross_loss': float(self.gross_loss),
            'profit_factor': float(self.profit_factor),
            'average_win': float(self.average_win),
            'average_loss': float(self.average_loss),
            'max_drawdown': float(self.max_drawdown),
            'max_drawdown_percent': float(self.max_drawdown_percent),
            'sharpe_ratio': float(self.sharpe_ratio),
            'sortino_ratio': float(self.sortino_ratio),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'duration_days': self.duration_days,
            'equity_curve': equity_curve_json,
            'drawdown_curve': drawdown_curve_json,
            'trades': trades_json,
        }
    
    def to_json(self, filepath: str):
        """Save results to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BacktestResult':
        """Create from dictionary"""
        return cls(
            initial_capital=Decimal(str(data['initial_capital'])),
            final_capital=Decimal(str(data['final_capital'])),
            total_pnl=Decimal(str(data['total_pnl'])),
            total_return=Decimal(str(data['total_return'])),
            total_trades=data['total_trades'],
            winning_trades=data['winning_trades'],
            losing_trades=data['losing_trades'],
            win_rate=Decimal(str(data['win_rate'])),
            gross_profit=Decimal(str(data['gross_profit'])),
            gross_loss=Decimal(str(data['gross_loss'])),
            profit_factor=Decimal(str(data['profit_factor'])),
            average_win=Decimal(str(data['average_win'])),
            average_loss=Decimal(str(data['average_loss'])),
            max_drawdown=Decimal(str(data['max_drawdown'])),
            max_drawdown_percent=Decimal(str(data['max_drawdown_percent'])),
            sharpe_ratio=Decimal(str(data['sharpe_ratio'])),
            sortino_ratio=Decimal(str(data['sortino_ratio'])),
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
            duration_days=data['duration_days'],
            equity_curve=data.get('equity_curve', []),
            drawdown_curve=data.get('drawdown_curve', []),
            trades=data.get('trades', []),
        )
    
    @classmethod
    def from_json(cls, filepath: str) -> 'BacktestResult':
        """Load results from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


class BacktestAnalyzer:
    """
    Analyzer for calculating backtest performance metrics
    回测性能指标分析器
    """
    
    @staticmethod
    def calculate_metrics(initial_capital: Decimal, 
                         equity_curve: List[Dict[str, Any]],
                         trades: List[Dict[str, Any]]) -> BacktestResult:
        """
        Calculate comprehensive backtest metrics
        计算综合回测指标
        
        Args:
            initial_capital: Initial capital
            equity_curve: List of equity snapshots with timestamp and value
            trades: List of trade dictionaries
            
        Returns:
            BacktestResult object with all metrics
        """
        if not equity_curve:
            return BacktestResult(
                initial_capital=initial_capital,
                final_capital=initial_capital,
                total_pnl=Decimal('0'),
                total_return=Decimal('0')
            )
        
        final_capital = Decimal(str(equity_curve[-1]['value']))
        total_pnl = final_capital - initial_capital
        total_return = (total_pnl / initial_capital * 100) if initial_capital > 0 else Decimal('0')
        
        # Trade statistics
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if Decimal(str(t.get('pnl', 0))) > 0)
        losing_trades = sum(1 for t in trades if Decimal(str(t.get('pnl', 0))) < 0)
        win_rate = (Decimal(winning_trades) / Decimal(total_trades) * 100) if total_trades > 0 else Decimal('0')
        
        # Profit metrics
        gross_profit = sum(Decimal(str(t.get('pnl', 0))) for t in trades if Decimal(str(t.get('pnl', 0))) > 0)
        gross_loss = abs(sum(Decimal(str(t.get('pnl', 0))) for t in trades if Decimal(str(t.get('pnl', 0))) < 0))
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else Decimal('0')
        average_win = (gross_profit / Decimal(winning_trades)) if winning_trades > 0 else Decimal('0')
        average_loss = (gross_loss / Decimal(losing_trades)) if losing_trades > 0 else Decimal('0')
        
        # Calculate drawdown
        max_drawdown, max_drawdown_percent, drawdown_curve = BacktestAnalyzer._calculate_drawdown(equity_curve)
        
        # Calculate risk ratios
        sharpe_ratio = BacktestAnalyzer._calculate_sharpe_ratio(equity_curve)
        sortino_ratio = BacktestAnalyzer._calculate_sortino_ratio(equity_curve)
        
        # Time metrics
        start_date = equity_curve[0]['timestamp'] if equity_curve else None
        end_date = equity_curve[-1]['timestamp'] if equity_curve else None
        duration_days = (end_date - start_date).days if start_date and end_date else 0
        
        return BacktestResult(
            initial_capital=initial_capital,
            final_capital=final_capital,
            total_pnl=total_pnl,
            total_return=total_return,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            gross_profit=gross_profit,
            gross_loss=gross_loss,
            profit_factor=profit_factor,
            average_win=average_win,
            average_loss=average_loss,
            max_drawdown=max_drawdown,
            max_drawdown_percent=max_drawdown_percent,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days,
            equity_curve=equity_curve,
            drawdown_curve=drawdown_curve,
            trades=trades,
        )
    
    @staticmethod
    def _calculate_drawdown(equity_curve: List[Dict[str, Any]]) -> tuple:
        """Calculate maximum drawdown"""
        if not equity_curve:
            return Decimal('0'), Decimal('0'), []
        
        peak = Decimal(str(equity_curve[0]['value']))
        max_dd = Decimal('0')
        max_dd_pct = Decimal('0')
        drawdown_curve = []
        
        for point in equity_curve:
            value = Decimal(str(point['value']))
            peak = max(peak, value)
            dd = peak - value
            dd_pct = (dd / peak * 100) if peak > 0 else Decimal('0')
            
            max_dd = max(max_dd, dd)
            max_dd_pct = max(max_dd_pct, dd_pct)
            
            drawdown_curve.append({
                'timestamp': point['timestamp'],
                'drawdown': float(dd),
                'drawdown_percent': float(dd_pct),
            })
        
        return max_dd, max_dd_pct, drawdown_curve
    
    @staticmethod
    def _calculate_sharpe_ratio(equity_curve: List[Dict[str, Any]], 
                               risk_free_rate: Decimal = Decimal('0.02')) -> Decimal:
        """
        Calculate Sharpe ratio
        计算夏普比率
        
        Args:
            equity_curve: Equity curve data
            risk_free_rate: Annual risk-free rate (default: 2%)
            
        Returns:
            Sharpe ratio
        """
        if len(equity_curve) < 2:
            return Decimal('0')
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(equity_curve)):
            prev_value = Decimal(str(equity_curve[i-1]['value']))
            curr_value = Decimal(str(equity_curve[i]['value']))
            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                returns.append(daily_return)
        
        if not returns:
            return Decimal('0')
        
        # Calculate mean and standard deviation
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = variance.sqrt() if variance > 0 else Decimal('0')
        
        if std_dev == 0:
            return Decimal('0')
        
        # Annualized Sharpe ratio (assuming 252 trading days)
        daily_rf = risk_free_rate / 252
        sharpe = (mean_return - daily_rf) / std_dev * Decimal('252').sqrt()
        
        return sharpe
    
    @staticmethod
    def _calculate_sortino_ratio(equity_curve: List[Dict[str, Any]], 
                                 risk_free_rate: Decimal = Decimal('0.02')) -> Decimal:
        """
        Calculate Sortino ratio (uses downside deviation instead of total volatility)
        计算索提诺比率（使用下行偏差代替总波动率）
        
        Args:
            equity_curve: Equity curve data
            risk_free_rate: Annual risk-free rate (default: 2%)
            
        Returns:
            Sortino ratio
        """
        if len(equity_curve) < 2:
            return Decimal('0')
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(equity_curve)):
            prev_value = Decimal(str(equity_curve[i-1]['value']))
            curr_value = Decimal(str(equity_curve[i]['value']))
            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                returns.append(daily_return)
        
        if not returns:
            return Decimal('0')
        
        # Calculate mean return
        mean_return = sum(returns) / len(returns)
        
        # Calculate downside deviation (only negative returns)
        downside_returns = [r for r in returns if r < 0]
        if not downside_returns:
            return Decimal('0')
        
        downside_variance = sum(r ** 2 for r in downside_returns) / len(downside_returns)
        downside_dev = downside_variance.sqrt() if downside_variance > 0 else Decimal('0')
        
        if downside_dev == 0:
            return Decimal('0')
        
        # Annualized Sortino ratio
        daily_rf = risk_free_rate / 252
        sortino = (mean_return - daily_rf) / downside_dev * Decimal('252').sqrt()
        
        return sortino
