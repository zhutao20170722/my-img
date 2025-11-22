// Trading System Web Interface JavaScript

// API helper function
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(endpoint, options);
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('API call failed:', error);
        return { success: false, message: error.message };
    }
}

// Engine Control
let engineInitialized = false;
let engineRunning = false;

document.getElementById('initEngine').addEventListener('click', async () => {
    const result = await apiCall('/api/init', 'POST', {
        initial_capital: 100000,
        max_position_size: 1000,
        max_order_value: 100000,
        max_daily_loss: 10000,
        max_positions: 10
    });
    
    if (result.success) {
        engineInitialized = true;
        document.getElementById('startEngine').disabled = false;
        document.getElementById('engineStatus').textContent = '已初始化 / Initialized';
        document.getElementById('engineStatus').className = 'status';
        alert('引擎初始化成功 / Engine initialized successfully');
        refreshAccount();
    } else {
        alert('初始化失败 / Initialization failed: ' + result.message);
    }
});

document.getElementById('startEngine').addEventListener('click', async () => {
    const result = await apiCall('/api/engine/start', 'POST');
    
    if (result.success) {
        engineRunning = true;
        document.getElementById('startEngine').disabled = true;
        document.getElementById('stopEngine').disabled = false;
        document.getElementById('engineStatus').textContent = '运行中 / Running';
        document.getElementById('engineStatus').className = 'status running';
    } else {
        alert('启动失败 / Start failed: ' + result.message);
    }
});

document.getElementById('stopEngine').addEventListener('click', async () => {
    const result = await apiCall('/api/engine/stop', 'POST');
    
    if (result.success) {
        engineRunning = false;
        document.getElementById('startEngine').disabled = false;
        document.getElementById('stopEngine').disabled = true;
        document.getElementById('engineStatus').textContent = '已停止 / Stopped';
        document.getElementById('engineStatus').className = 'status stopped';
    } else {
        alert('停止失败 / Stop failed: ' + result.message);
    }
});

// Platform Connection
let platformConnected = false;

document.getElementById('connectPlatform').addEventListener('click', async () => {
    const platform = document.getElementById('platformSelect').value;
    
    if (!platform) {
        alert('请选择平台 / Please select a platform');
        return;
    }
    
    // Default configuration for simulation mode
    const config = {
        host: '127.0.0.1',
        port: platform === 'mt5' ? 0 : 7497,
        account: '',
        password: '',
        server: ''
    };
    
    const result = await apiCall(`/api/connect/${platform}`, 'POST', config);
    
    if (result.success) {
        platformConnected = true;
        document.getElementById('disconnectPlatform').disabled = false;
        document.getElementById('connectionStatus').textContent = `已连接 (${platform.toUpperCase()}) / Connected`;
        document.getElementById('connectionStatus').className = 'status connected';
    } else {
        alert('连接失败 / Connection failed: ' + result.message);
    }
});

document.getElementById('disconnectPlatform').addEventListener('click', async () => {
    const result = await apiCall('/api/disconnect', 'POST');
    
    if (result.success) {
        platformConnected = false;
        document.getElementById('disconnectPlatform').disabled = true;
        document.getElementById('connectionStatus').textContent = '未连接 / Not Connected';
        document.getElementById('connectionStatus').className = 'status';
        document.getElementById('platformSelect').value = '';
    }
});

// Strategy Management
document.getElementById('addStrategy').addEventListener('click', async () => {
    const strategyType = document.getElementById('strategyType').value;
    
    if (!strategyType) {
        alert('请选择策略类型 / Please select strategy type');
        return;
    }
    
    const config = {
        type: strategyType,
        name: strategyType === 'momentum' ? '动量策略 / Momentum' : '均值回归 / Mean Reversion',
        short_period: 5,
        long_period: 20,
        period: 20,
        std_multiplier: 2.0,
        quantity: 100
    };
    
    const result = await apiCall('/api/strategies/add', 'POST', config);
    
    if (result.success) {
        alert(result.message);
        refreshStrategies();
        document.getElementById('strategyType').value = '';
    } else {
        alert('添加策略失败 / Add strategy failed: ' + result.message);
    }
});

async function refreshStrategies() {
    const result = await apiCall('/api/strategies');
    
    if (result.success && result.strategies.length > 0) {
        const listDiv = document.getElementById('strategiesList');
        listDiv.innerHTML = '';
        
        result.strategies.forEach(strategy => {
            const item = document.createElement('div');
            item.className = 'strategy-item';
            item.innerHTML = `
                <div>
                    <div class="strategy-name">${strategy.name}</div>
                    <div class="strategy-type">${strategy.type}</div>
                </div>
                <div>${strategy.enabled ? '✅ Enabled' : '❌ Disabled'}</div>
            `;
            listDiv.appendChild(item);
        });
    }
}

// Account Summary
async function refreshAccount() {
    const result = await apiCall('/api/account');
    
    if (result.success) {
        const account = result.account;
        
        document.getElementById('initialCapital').textContent = '¥' + account.initial_capital.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        document.getElementById('cash').textContent = '¥' + account.cash.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        document.getElementById('portfolioValue').textContent = '¥' + account.portfolio_value.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        
        const pnlElement = document.getElementById('totalPnl');
        pnlElement.textContent = '¥' + account.total_pnl.toLocaleString('zh-CN', {minimumFractionDigits: 2, maximumFractionDigits: 2});
        pnlElement.className = 'stat-value pnl ' + (account.total_pnl >= 0 ? 'positive' : 'negative');
        
        document.getElementById('positionsCount').textContent = account.positions_count;
        document.getElementById('totalTrades').textContent = account.total_trades;
    }
}

// Positions
async function refreshPositions() {
    const result = await apiCall('/api/positions');
    
    if (result.success) {
        const tbody = document.getElementById('positionsBody');
        
        if (result.positions.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-message">暂无持仓 / No positions</td></tr>';
        } else {
            tbody.innerHTML = '';
            
            result.positions.forEach(pos => {
                const row = document.createElement('tr');
                const pnlClass = pos.total_pnl >= 0 ? 'positive' : 'negative';
                
                row.innerHTML = `
                    <td>${pos.symbol}</td>
                    <td>${pos.quantity}</td>
                    <td>¥${pos.average_cost.toFixed(2)}</td>
                    <td>¥${pos.current_price.toFixed(2)}</td>
                    <td>¥${pos.market_value.toFixed(2)}</td>
                    <td class="${pnlClass}">¥${pos.total_pnl.toFixed(2)}</td>
                `;
                
                tbody.appendChild(row);
            });
        }
    }
}

// Backtest Results
document.getElementById('refreshBacktest').addEventListener('click', async () => {
    const result = await apiCall('/api/backtest/result');
    
    if (result.success) {
        const data = result.result;
        const container = document.getElementById('backtestResults');
        
        container.innerHTML = `
            <div class="metric-grid">
                <div class="metric-card">
                    <h3>总收益率 / Total Return</h3>
                    <div class="value ${data.total_return >= 0 ? 'positive' : 'negative'}">
                        ${data.total_return.toFixed(2)}%
                    </div>
                </div>
                <div class="metric-card">
                    <h3>总盈亏 / Total P&L</h3>
                    <div class="value ${data.total_pnl >= 0 ? 'positive' : 'negative'}">
                        ¥${data.total_pnl.toFixed(2)}
                    </div>
                </div>
                <div class="metric-card">
                    <h3>交易次数 / Total Trades</h3>
                    <div class="value">${data.total_trades}</div>
                </div>
                <div class="metric-card">
                    <h3>胜率 / Win Rate</h3>
                    <div class="value">${data.win_rate.toFixed(2)}%</div>
                </div>
                <div class="metric-card">
                    <h3>盈利因子 / Profit Factor</h3>
                    <div class="value">${data.profit_factor.toFixed(2)}</div>
                </div>
                <div class="metric-card">
                    <h3>最大回撤 / Max Drawdown</h3>
                    <div class="value negative">${data.max_drawdown_percent.toFixed(2)}%</div>
                </div>
                <div class="metric-card">
                    <h3>夏普比率 / Sharpe Ratio</h3>
                    <div class="value">${data.sharpe_ratio.toFixed(2)}</div>
                </div>
                <div class="metric-card">
                    <h3>索提诺比率 / Sortino Ratio</h3>
                    <div class="value">${data.sortino_ratio.toFixed(2)}</div>
                </div>
            </div>
        `;
    } else {
        alert('获取回测结果失败 / Failed to get backtest results: ' + result.message);
    }
});

// Auto-refresh data
setInterval(() => {
    if (engineInitialized) {
        refreshAccount();
        refreshPositions();
        refreshStrategies();
    }
}, 2000); // Refresh every 2 seconds
