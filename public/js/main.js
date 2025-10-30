// AI彩票分析实验室 - 主JavaScript文件
// 版本: 3.1 - 修复所有语法错误

var currentUpdateTime = '';
var debugMode = true;
var currentStrategy = 'balanced';
var predictionHistory = [];

function log(type, message, data) {
    if (!debugMode) return;
    var emoji = {'info': 'ℹ️', 'success': '✅', 'error': '❌', 'warning': '⚠️', 'debug': '🔍'};
    var prefix = emoji[type] || '📝';
    if (data) {
        console.log(prefix + ' ' + message, data);
    } else {
        console.log(prefix + ' ' + message);
    }
}

document.addEventListener('DOMContentLoaded', function() {
    log('info', '页面加载完成，开始初始化...');
    loadPrediction(false);
    loadHistory();
});

function loadPrediction(forceNew) {
    log('info', '加载预测数据... (重新生成: ' + forceNew + ')');
    
    var loadingEl = document.getElementById('loading');
    var predictionsEl = document.getElementById('predictions');
    
    if (!loadingEl || !predictionsEl) {
        log('error', '找不到必要的DOM元素');
        return;
    }
    
    loadingEl.style.display = 'block';
    predictionsEl.style.display = 'none';
    
    var seed = Date.now() + Math.floor(Math.random() * 10000);
    var apiUrl = '/api/predict.py?seed=' + seed + '&strategy=' + currentStrategy;
    
    log('debug', '请求API: ' + apiUrl);
    
    fetch(apiUrl)
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ': ' + response.statusText);
            }
            return response.json();
        })
        .then(function(data) {
            log('success', '预测数据加载成功', data);
            
            if (!data.red_balls || !data.blue_balls) {
                throw new Error('API返回数据结构不完整');
            }
            
            if (!Array.isArray(data.red_balls) || !Array.isArray(data.blue_balls)) {
                throw new Error('号码数据必须是数组格式');
            }
            
            if (forceNew && predictionHistory.length < 10) {
                predictionHistory.push({
                    timestamp: new Date().toLocaleString('zh-CN'),
                    data: data
                });
            }
            
            displayPrediction(data);
            updateStrategyDisplay();
            fetchAndUpdateTimestamp();
            
            if (forceNew) {
                showReanalysisNotification();
            }
            
            loadingEl.style.display = 'none';
            predictionsEl.style.display = 'block';
        })
        .catch(function(error) {
            log('error', '加载预测失败', error);
            showError('预测加载失败: ' + error.message);
            loadingEl.style.display = 'none';
            predictionsEl.style.display = 'block';
        });
}

function reanalyze() {
    log('info', '用户点击重新分析按钮');
    showStrategySelector();
    loadPrediction(true);
}

function showStrategySelector() {
    if (document.getElementById('strategy-selector')) {
        return;
    }
    
    var modelInfoEl = document.getElementById('model-info');
    if (!modelInfoEl) return;
    
    var selectorHTML = '<div id="strategy-selector" class="strategy-selector">' +
        '<h4>🎯 选择预测策略</h4>' +
        '<div class="strategy-options">' +
        '<button class="strategy-btn ' + (currentStrategy === 'conservative' ? 'active' : '') + '" onclick="changeStrategy(\'conservative\')">' +
        '🛡️ 保守型<small>侧重高频号码</small></button>' +
        '<button class="strategy-btn ' + (currentStrategy === 'balanced' ? 'active' : '') + '" onclick="changeStrategy(\'balanced\')">' +
        '⚖️ 平衡型<small>高频+随机混合</small></button>' +
        '<button class="strategy-btn ' + (currentStrategy === 'aggressive' ? 'active' : '') + '" onclick="changeStrategy(\'aggressive\')">' +
        '🚀 激进型<small>探索冷门号码</small></button>' +
        '<button class="strategy-btn ' + (currentStrategy === 'random' ? 'active' : '') + '" onclick="changeStrategy(\'random\')">' +
        '🎲 随机型<small>完全随机探索</small></button>' +
        '</div></div>';
    
    modelInfoEl.insertAdjacentHTML('beforebegin', selectorHTML);
}

function changeStrategy(strategy) {
    log('info', '切换策略: ' + strategy);
    currentStrategy = strategy;
    
    var buttons = document.querySelectorAll('.strategy-btn');
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].classList.remove('active');
    }
    
    var allButtons = document.querySelectorAll('.strategy-btn');
    for (var j = 0; j < allButtons.length; j++) {
        if (allButtons[j].getAttribute('onclick').indexOf(strategy) !== -1) {
            allButtons[j].classList.add('active');
            break;
        }
    }
    
    loadPrediction(true);
}

function updateStrategyDisplay() {
    var modelInfoEl = document.getElementById('model-info');
    if (!modelInfoEl) return;
    
    var strategyEl = modelInfoEl.querySelector('.current-strategy');
    if (!strategyEl) {
        strategyEl = document.createElement('p');
        strategyEl.className = 'current-strategy';
        modelInfoEl.insertBefore(strategyEl, modelInfoEl.firstChild);
    }
    
    var strategyNames = {
        'conservative': '🛡️ 保守型策略',
        'balanced': '⚖️ 平衡型策略',
        'aggressive': '🚀 激进型策略',
        'random': '🎲 随机型策略'
    };
    
    strategyEl.innerHTML = '<strong>当前策略:</strong> ' + strategyNames[currentStrategy];
}

function showReanalysisNotification() {
    var notification = document.createElement('div');
    notification.className = 'reanalysis-notification';
    notification.innerHTML = '<span class="icon">🔄</span><span class="text">已生成新的预测结果</span>';
    document.body.appendChild(notification);
    
    setTimeout(function() {
        notification.classList.add('fade-out');
        setTimeout(function() {
            notification.remove();
        }, 300);
    }, 3000);
}

function fetchAndUpdateTimestamp() {
    log('info', '开始获取时间戳...');
    
    fetch('/api/latest-results.py')
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status);
            }
            return response.json();
        })
        .then(function(data) {
            log('debug', '时间戳API响应', data);
            
            if (data.status === 'success' && data.updated_at) {
                currentUpdateTime = data.updated_at;
                updateTimestampDisplay(currentUpdateTime);
                log('success', '时间戳更新成功', currentUpdateTime);
            } else {
                throw new Error('时间戳数据格式不正确');
            }
        })
        .catch(function(error) {
            log('warning', '时间戳获取失败，使用当前时间', error);
            var now = new Date();
            currentUpdateTime = now.toLocaleString('zh-CN').replace(/\//g, '-');
            updateTimestampDisplay(currentUpdateTime);
        });
}

function updateTimestampDisplay(timestamp) {
    log('info', '更新时间显示', timestamp);
    var modelInfoEl = document.getElementById('model-info');
    if (!modelInfoEl) {
        log('warning', '找不到 model-info 元素');
        return;
    }
    
    var timeElement = modelInfoEl.querySelector('.update-time');
    if (timeElement) {
        timeElement.innerHTML = '⏰ <strong>训练时间:</strong> ' + timestamp;
    } else {
        var newTimeElement = document.createElement('p');
        newTimeElement.className = 'update-time';
        newTimeElement.innerHTML = '⏰ <strong>训练时间:</strong> ' + timestamp;
        modelInfoEl.appendChild(newTimeElement);
    }
    log('success', '时间显示已更新');
}

function displayPrediction(data) {
    log('info', '开始渲染预测结果', data);
    displayBalls('red-balls', data.red_balls, 'red-ball');
    displayBalls('blue-balls', data.blue_balls, 'blue-ball');
    displayModelInfo(data);
    log('success', '预测结果渲染完成');
}

function displayBalls(containerId, balls, ballClass) {
    var container = document.getElementById(containerId);
    if (!container) {
        log('error', '找不到容器: ' + containerId);
        return;
    }
    
    if (!balls || !Array.isArray(balls) || balls.length === 0) {
        log('warning', containerId + ' 数据无效', balls);
        container.innerHTML = '<p style="color: #999;">暂无数据</p>';
        return;
    }
    
    log('debug', '渲染 ' + containerId, balls);
    
    var ballsHTML = '';
    for (var i = 0; i < balls.length; i++) {
        var displayNum = String(balls[i]).padStart(2, '0');
        ballsHTML += '<div class="ball ' + ballClass + '">' + displayNum + '</div>';
    }
    
    container.innerHTML = ballsHTML;
    log('success', containerId + ' 渲染完成');
}

function displayModelInfo(data) {
    var modelInfoEl = document.getElementById('model-info');
    if (!modelInfoEl) {
        log('warning', '找不到 model-info 元素');
        return;
    }
    
    var infoHTML = '<div class="model-details">';
    
    if (data.confidence !== undefined) {
        var confidencePercent = (data.confidence * 100).toFixed(1);
        infoHTML += '<p>📊 <strong>置信度:</strong> ' + confidencePercent + '%</p>';
    }
    
    if (data.model) {
        infoHTML += '<p>🤖 <strong>模型:</strong> ' + data.model + '</p>';
    }
    
    if (data.based_on_count) {
        infoHTML += '<p>📈 <strong>基于:</strong> ' + data.based_on_count + ' 期历史数据</p>';
    }
    
    if (currentUpdateTime) {
        infoHTML += '<p class="update-time">⏰ <strong>训练时间:</strong> ' + currentUpdateTime + '</p>';
    }
    
    infoHTML += '</div>';
    modelInfoEl.innerHTML = infoHTML;
    log('success', '模型信息显示完成');
}

function loadHistory() {
    log('info', '开始加载历史数据...');
    
    var loadingEl = document.getElementById('history-loading');
    var contentEl = document.getElementById('history-content');
    var errorEl = document.getElementById('history-error');
    
    if (!loadingEl || !contentEl || !errorEl) {
        log('error', '找不到历史数据相关的DOM元素');
        return;
    }
    
    loadingEl.style.display = 'flex';
    contentEl.style.display = 'none';
    errorEl.style.display = 'none';
    
    log('debug', '正在请求 /api/history.py...');
    
    fetch('/api/history.py')
        .then(function(response) {
            if (!response.ok) {
                throw new Error('HTTP ' + response.status + ': ' + response.statusText);
            }
            return response.json();
        })
        .then(function(data) {
            log('success', '历史数据加载成功', data);
            
            if (!data.history || !Array.isArray(data.history)) {
                throw new Error('历史数据格式不正确');
            }
            
            displayHistory(data);
            loadingEl.style.display = 'none';
            contentEl.style.display = 'block';
        })
        .catch(function(error) {
            log('error', '历史数据加载失败', error);
            loadingEl.style.display = 'none';
            errorEl.style.display = 'block';
            
            var errorText = errorEl.querySelector('p');
            if (errorText) {
                errorText.textContent = '加载失败: ' + error.message;
            }
        });
}

function displayHistory(data) {
    log('info', '开始渲染历史数据', data);
    var tbody = document.getElementById('history-tbody');
    
    if (!tbody) {
        log('error', '找不到 history-tbody 元素');
        return;
    }
    
    if (!data.history || data.history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #999;">暂无数据</td></tr>';
        log('warning', '历史数据为空');
        return;
    }
    
    var recentData = data.history.slice(0, 10);
    log('debug', '渲染 ' + recentData.length + ' 条历史记录');
    
    var rowsHTML = '';
    for (var i = 0; i < recentData.length; i++) {
        var item = recentData[i];
        var period = item.period || '---';
        var date = item.date || '---';
        var redBalls = formatNumbers(item.red_balls, 'red');
        var blueBalls = formatNumbers(item.blue_balls, 'blue');
        
        rowsHTML += '<tr>' +
            '<td class="period">' + period + '</td>' +
            '<td class="date">' + date + '</td>' +
            '<td class="numbers"><div class="number-display">' +
            redBalls + '<span class="separator">+</span>' + blueBalls +
            '</div></td></tr>';
    }
    
    tbody.innerHTML = rowsHTML;
    log('success', '历史数据渲染完成');
}

function formatNumbers(numbers, type) {
    if (!numbers || !Array.isArray(numbers) || numbers.length === 0) {
        return '<span style="color: #999;">--</span>';
    }
    
    var className = type === 'red' ? 'red-ball-small' : 'blue-ball-small';
    var html = '';
    
    for (var i = 0; i < numbers.length; i++) {
        var displayNum = String(numbers[i]).padStart(2, '0');
        html += '<span class="ball-small ' + className + '">' + displayNum + '</span>';
        if (i < numbers.length - 1) {
            html += ' ';
        }
    }
    
    return html;
}

function showPredictionHistory() {
    if (predictionHistory.length === 0) {
        alert('暂无预测历史记录');
        return;
    }
    
    var historyHTML = '<div class="modal-overlay" id="history-modal" onclick="closeHistoryModal()">' +
        '<div class="modal-content" onclick="event.stopPropagation()">' +
        '<div class="modal-header"><h2>📊 预测历史记录</h2>' +
        '<button class="close-btn" onclick="closeHistoryModal()">×</button></div>' +
        '<div class="modal-body"><div class="history-list">';
    
    for (var i = 0; i < predictionHistory.length; i++) {
        var record = predictionHistory[i];
        historyHTML += '<div class="history-item">' +
            '<div class="history-header">' +
            '<span class="history-index">#' + (i + 1) + '</span>' +
            '<span class="history-time">' + record.timestamp + '</span></div>' +
            '<div class="history-numbers">' +
            '<div class="red-numbers">';
        
        for (var j = 0; j < record.data.red_balls.length; j++) {
            historyHTML += '<span class="ball-small red-ball-small">' + String(record.data.red_balls[j]).padStart(2, '0') + '</span>';
        }
        
        historyHTML += '</div><span class="separator">+</span><div class="blue-numbers">';
        
        for (var k = 0; k < record.data.blue_balls.length; k++) {
            historyHTML += '<span class="ball-small blue-ball-small">' + String(record.data.blue_balls[k]).padStart(2, '0') + '</span>';
        }
        
        historyHTML += '</div></div>' +
            '<div class="history-meta">' +
            '<span>策略: ' + record.data.model + '</span>' +
            '<span>置信度: ' + (record.data.confidence * 100).toFixed(1) + '%</span>' +
            '</div></div>';
    }
    
    historyHTML += '</div></div>' +
        '<div class="modal-footer">' +
        '<button class="btn btn-secondary" onclick="clearPredictionHistory()">清空历史</button>' +
        '<button class="btn btn-primary" onclick="closeHistoryModal()">关闭</button>' +
        '</div></div></div>';
    
    document.body.insertAdjacentHTML('beforeend', historyHTML);
}

function closeHistoryModal() {
    var modal = document.getElementById('history-modal');
    if (modal) {
        modal.remove();
    }
}

function clearPredictionHistory() {
    if (confirm('确定要清空所有预测历史记录吗？')) {
        predictionHistory = [];
        closeHistoryModal();
        log('info', '预测历史已清空');
    }
}

function showAbout() {
    var predictionsEl = document.getElementById('predictions');
    var aboutEl = document.getElementById('about');
    if (predictionsEl && aboutEl) {
        predictionsEl.style.display = 'none';
        aboutEl.style.display = 'block';
        log('info', '显示关于页面');
    }
}

function hideAbout() {
    var predictionsEl = document.getElementById('predictions');
    var aboutEl = document.getElementById('about');
    if (predictionsEl && aboutEl) {
        aboutEl.style.display = 'none';
        predictionsEl.style.display = 'block';
        log('info', '返回主页面');
    }
}

function showError(message) {
    log('error', '显示错误信息', message);
    var predictionsEl = document.getElementById('predictions');
    if (!predictionsEl) return;
    
    predictionsEl.innerHTML = '<div class="error-message" style="text-align: center; padding: 40px 20px; background: #fff3cd; border-radius: 10px; margin: 20px 0;">' +
        '<span style="font-size: 48px;">❌</span>' +
        '<h3 style="color: #856404; margin: 20px 0;">加载失败</h3>' +
        '<p style="color: #856404; margin-bottom: 20px;">' + message + '</p>' +
        '<button onclick="loadPrediction(false)" class="btn btn-primary" style="padding: 12px 30px; background: #667eea; color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 16px;">🔄 重试</button>' +
        '</div>';
}

log('success', 'main.js 加载完成！版本: 3.1');
