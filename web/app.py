"""
Flask web server for trading system
交易系统Flask Web服务器
"""

from flask import Flask, render_template, jsonify, request
from decimal import Decimal
from datetime import datetime
import json
import os
import sys

# Add parent directory to path to import trading_system
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from trading_system import (
    TradingEngine, RiskManager, MomentumStrategy, 
    MeanReversionStrategy, MarketData, MT5Connector, IBConnector
)

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Global trading engine instance
trading_engine = None
connector = None


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/init', methods=['POST'])
def init_engine():
    """
    Initialize trading engine
    初始化交易引擎
    """
    global trading_engine, connector
    
    data = request.get_json()
    
    try:
        # Create risk manager
        risk_manager = RiskManager(
            max_position_size=data.get('max_position_size', 1000),
            max_order_value=Decimal(str(data.get('max_order_value', 100000))),
            max_daily_loss=Decimal(str(data.get('max_daily_loss', 10000))),
            max_positions=data.get('max_positions', 10)
        )
        
        # Create trading engine
        trading_engine = TradingEngine(
            initial_capital=Decimal(str(data.get('initial_capital', 100000))),
            risk_manager=risk_manager
        )
        
        # Enable equity tracking for backtesting
        trading_engine.enable_equity_tracking()
        
        return jsonify({
            'success': True,
            'message': 'Trading engine initialized successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/connect/<platform>', methods=['POST'])
def connect_platform(platform):
    """
    Connect to trading platform (MT5 or IB)
    连接到交易平台
    """
    global connector
    
    data = request.get_json()
    
    try:
        if platform.lower() == 'mt5':
            connector = MT5Connector(data)
        elif platform.lower() == 'ib':
            connector = IBConnector(data)
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown platform: {platform}'
            }), 400
        
        success = connector.connect()
        
        return jsonify({
            'success': success,
            'message': 'Connected successfully' if success else 'Connection failed'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/disconnect', methods=['POST'])
def disconnect_platform():
    """Disconnect from trading platform"""
    global connector
    
    if connector:
        connector.disconnect()
        connector = None
        return jsonify({'success': True, 'message': 'Disconnected'})
    
    return jsonify({'success': False, 'message': 'No active connection'})


@app.route('/api/strategies', methods=['GET'])
def get_strategies():
    """Get list of available strategies"""
    if not trading_engine:
        return jsonify({'success': False, 'message': 'Engine not initialized'}), 400
    
    strategies = []
    for strategy in trading_engine.strategies:
        strategies.append({
            'name': strategy.name,
            'enabled': strategy.enabled,
            'type': strategy.__class__.__name__
        })
    
    return jsonify({'success': True, 'strategies': strategies})


@app.route('/api/strategies/add', methods=['POST'])
def add_strategy():
    """
    Add a trading strategy
    添加交易策略
    """
    if not trading_engine:
        return jsonify({'success': False, 'message': 'Engine not initialized'}), 400
    
    data = request.get_json()
    strategy_type = data.get('type')
    
    try:
        if strategy_type == 'momentum':
            strategy = MomentumStrategy(
                name=data.get('name', 'Momentum Strategy'),
                short_period=data.get('short_period', 5),
                long_period=data.get('long_period', 20),
                quantity=data.get('quantity', 100)
            )
        elif strategy_type == 'mean_reversion':
            strategy = MeanReversionStrategy(
                name=data.get('name', 'Mean Reversion Strategy'),
                period=data.get('period', 20),
                std_multiplier=data.get('std_multiplier', 2.0),
                quantity=data.get('quantity', 100)
            )
        else:
            return jsonify({
                'success': False,
                'message': f'Unknown strategy type: {strategy_type}'
            }), 400
        
        trading_engine.add_strategy(strategy)
        
        return jsonify({
            'success': True,
            'message': f'Strategy "{strategy.name}" added successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@app.route('/api/engine/start', methods=['POST'])
def start_engine():
    """Start trading engine"""
    if not trading_engine:
        return jsonify({'success': False, 'message': 'Engine not initialized'}), 400
    
    trading_engine.start()
    return jsonify({'success': True, 'message': 'Engine started'})


@app.route('/api/engine/stop', methods=['POST'])
def stop_engine():
    """Stop trading engine"""
    if not trading_engine:
        return jsonify({'success': False, 'message': 'Engine not initialized'}), 400
    
    trading_engine.stop()
    return jsonify({'success': True, 'message': 'Engine stopped'})


@app.route('/api/account', methods=['GET'])
def get_account():
    """
    Get account summary
    获取账户摘要
    """
    if not trading_engine:
        return jsonify({'success': False, 'message': 'Engine not initialized'}), 400
    
    try:
        summary = trading_engine.get_account_summary()
        
        # Convert Decimals to floats for JSON serialization
        result = {
            'initial_capital': float(summary['initial_capital']),
            'cash': float(summary['cash']),
            'portfolio_value': float(summary['portfolio_value']),
            'total_pnl': float(summary['total_pnl']),
            'positions_count': summary['positions_count'],
            'active_orders_count': summary['active_orders_count'],
            'total_trades': summary['total_trades'],
            'risk_metrics': {
                'daily_pnl': float(summary['risk_metrics']['daily_pnl']),
                'daily_loss_remaining': float(summary['risk_metrics']['daily_loss_remaining'])
            }
        }
        
        return jsonify({'success': True, 'account': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/positions', methods=['GET'])
def get_positions():
    """
    Get current positions
    获取当前持仓
    """
    if not trading_engine:
        return jsonify({'success': False, 'message': 'Engine not initialized'}), 400
    
    try:
        positions = trading_engine.get_positions_summary()
        
        # Convert Decimals to floats
        result = []
        for pos in positions:
            result.append({
                'symbol': pos['symbol'],
                'quantity': pos['quantity'],
                'average_cost': float(pos['average_cost']),
                'current_price': float(pos['current_price']),
                'market_value': float(pos['market_value']),
                'unrealized_pnl': float(pos['unrealized_pnl']),
                'realized_pnl': float(pos['realized_pnl']),
                'total_pnl': float(pos['total_pnl'])
            })
        
        return jsonify({'success': True, 'positions': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/backtest/result', methods=['GET'])
def get_backtest_result():
    """
    Get backtest result with performance metrics
    获取回测结果及性能指标
    """
    if not trading_engine:
        return jsonify({'success': False, 'message': 'Engine not initialized'}), 400
    
    try:
        result = trading_engine.get_backtest_result()
        return jsonify({'success': True, 'result': result.to_dict()})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/market_data', methods=['POST'])
def push_market_data():
    """
    Push market data to engine (for backtesting)
    推送市场数据到引擎（用于回测）
    """
    if not trading_engine:
        return jsonify({'success': False, 'message': 'Engine not initialized'}), 400
    
    data = request.get_json()
    
    try:
        market_data = MarketData(
            symbol=data['symbol'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            open=Decimal(str(data['open'])),
            high=Decimal(str(data['high'])),
            low=Decimal(str(data['low'])),
            close=Decimal(str(data['close'])),
            volume=data['volume']
        )
        
        trading_engine.on_market_data(market_data)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/platform/account', methods=['GET'])
def get_platform_account():
    """Get account info from connected platform"""
    if not connector:
        return jsonify({'success': False, 'message': 'No platform connected'}), 400
    
    try:
        account_info = connector.get_account_info()
        
        # Convert Decimals to floats
        result = {k: float(v) if isinstance(v, Decimal) else v 
                  for k, v in account_info.items()}
        
        return jsonify({'success': True, 'account': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/platform/positions', methods=['GET'])
def get_platform_positions():
    """Get positions from connected platform"""
    if not connector:
        return jsonify({'success': False, 'message': 'No platform connected'}), 400
    
    try:
        positions = connector.get_positions()
        
        # Convert Decimals to floats
        result = []
        for pos in positions:
            result.append({k: float(v) if isinstance(v, Decimal) else v 
                          for k, v in pos.items()})
        
        return jsonify({'success': True, 'positions': result})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


def run_server(host='0.0.0.0', port=5000, debug=False):
    """
    Run the Flask web server
    运行Flask Web服务器
    
    Args:
        host: Host address (default: 0.0.0.0)
        port: Port number (default: 5000)
        debug: Debug mode (default: False for security)
    
    Warning:
        Never set debug=True in production environments as it allows
        arbitrary code execution through the debugger.
    """
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    run_server()
